"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: scripts/build_government_pdfs.py
Purpose: Render the three canonical government-facing Markdown documents as branded PDFs.
Classification: build tooling
Version: 2.0.0
Last Material Revision: 2026-08-01
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""

from __future__ import annotations

import argparse
import html
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    ListFlowable,
    ListItem,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BRAND_LOGO = (
    PROJECT_ROOT
    / "brand"
    / "originals"
    / "CI-Logo-Brand-Lockup-Horizontal_Cognitive-Industries-Bilingual-Gold-Text-Transparent.png"
)

NAVY = HexColor("#0F1728")
GOLD = HexColor("#B89A5E")
CYAN = HexColor("#77D5F0")
IVORY = HexColor("#FBF7EE")
BODY = HexColor("#182033")
MUTED = HexColor("#667085")


@dataclass(frozen=True)
class DocumentSpec:
    """Describe one canonical source-to-PDF rendering contract."""

    key: str
    source: Path
    output: Path
    title: str
    subtitle: str
    author_role: str
    document_id: str
    classification: str
    language: str
    rights_text: str
    contact_lines: tuple[str, ...]
    cover_heading_count: int = 1
    required_text: tuple[str, ...] = ("2.0.0", "2026-08-01")
    forbidden_text: tuple[str, ...] = (
        "1.3.0",
        "1.1.0",
        "1.0.0",
        "2026-07-28",
        "2026-07-24",
    )
    minimum_pages: int = 2


DOCUMENTS = {
    "en": DocumentSpec(
        key="en",
        source=PROJECT_ROOT / "government" / "OFFICIAL_PROJECT_DOCUMENT_EN.md",
        output=PROJECT_ROOT / "OFFICIAL_PROJECT_DOCUMENT_EN.pdf",
        title="AI-IDP / AegisTrace",
        subtitle=(
            "Official Project Document — Universal AI Identity, Delegation, Provenance, "
            "Traceability, Quality, Accountability, and Permanent Audit Standard"
        ),
        author_role="Founder / CEO",
        document_id="AI-IDP-OFFICIAL-EN-2.0.0",
        classification="Official",
        language="English",
        rights_text="All rights reserved.",
        contact_lines=(
            "Pierre-Edward Procyk",
            "Founder / CEO",
            "Cognitive Industries — Les Industries Cognitives",
            "Saguenay, Québec, Canada",
            "p.procyk.media@gmail.com",
            "p.1o9.cognitive@outlook.com",
            "",
            "LinkedIn: linkedin.com/in/pierre-edward-procyk-223b75305",
        ),
        cover_heading_count=2,
        required_text=("2.0.0", "2026-08-01", "113"),
        minimum_pages=3,
    ),
    "fr": DocumentSpec(
        key="fr",
        source=PROJECT_ROOT / "government" / "DOCUMENT_OFFICIEL_PROJET_FR.md",
        output=PROJECT_ROOT / "DOCUMENT_OFFICIEL_PROJET_FR.pdf",
        title="AI-IDP / AegisTrace",
        subtitle=(
            "Document officiel de projet — Norme universelle d'identité, de délégation, "
            "de provenance, de traçabilité, de qualité, de responsabilité et d'audit permanent de l'IA"
        ),
        author_role="Fondateur / PDG",
        document_id="AI-IDP-OFFICIEL-FR-2.0.0",
        classification="Officiel",
        language="Français",
        rights_text="Tous droits réservés.",
        contact_lines=(
            "Pierre-Edward Procyk",
            "Fondateur / PDG",
            "Cognitive Industries — Les Industries Cognitives",
            "Saguenay, Québec, Canada",
            "p.procyk.media@gmail.com",
            "p.1o9.cognitive@outlook.com",
            "",
            "LinkedIn : linkedin.com/in/pierre-edward-procyk-223b75305",
        ),
        cover_heading_count=2,
        required_text=("2.0.0", "2026-08-01", "113"),
        minimum_pages=3,
    ),
    "note": DocumentSpec(
        key="note",
        source=PROJECT_ROOT / "government" / "NOTE_DE_SYNTHESE_FR.md",
        output=PROJECT_ROOT / "government" / "NOTE_DE_SYNTHESE_FR.pdf",
        title="Note de synthèse — AI-IDP",
        subtitle=(
            "Identité avant l'autonomie : un cadre universel pour l'identité, la traçabilité "
            "et la responsabilité des agents d'intelligence artificielle au Canada"
        ),
        author_role="Fondateur / PDG",
        document_id="AI-IDP-NSFR-2.0.0",
        classification="Public",
        language="Français",
        rights_text="Tous droits réservés.",
        contact_lines=(
            "Pierre-Edward Procyk",
            "Fondateur / PDG",
            "Cognitive Industries — Les Industries Cognitives",
            "Saguenay, Québec, Canada",
            "p.procyk.media@gmail.com",
        ),
        cover_heading_count=2,
        required_text=("2.0.0", "2026-08-01", "113"),
        minimum_pages=3,
    ),
}


def _register_fonts() -> tuple[str, str]:
    """Register one Unicode-capable sans-serif family without modifying system fonts."""

    candidates = (
        (Path(r"C:\Windows\Fonts\arial.ttf"), Path(r"C:\Windows\Fonts\arialbd.ttf")),
        (
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        ),
    )
    for regular, bold in candidates:
        if regular.is_file() and bold.is_file():
            pdfmetrics.registerFont(TTFont("AegisBody", str(regular)))
            pdfmetrics.registerFont(TTFont("AegisBold", str(bold)))
            return "AegisBody", "AegisBold"
    return "Helvetica", "Helvetica-Bold"


def _strip_front_matter(markdown: str) -> str:
    """Remove one simple YAML-style front-matter block from a canonical source."""

    if not markdown.startswith("---\n"):
        raise ValueError("Canonical Markdown source must begin with front matter")
    end = markdown.find("\n---\n", 4)
    if end == -1:
        raise ValueError("Canonical Markdown source has an unterminated front-matter block")
    return markdown[end + 5 :]


def _inline_markup(text: str) -> str:
    """Convert the supported inline Markdown subset to ReportLab paragraph markup."""

    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1 (\2)", text)
    escaped = html.escape(text, quote=False)
    escaped = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escaped)
    escaped = re.sub(r"`([^`]+)`", r"<font color='#0F1728'>\1</font>", escaped)
    return re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", escaped)


def _parse_markdown(markdown: str, cover_heading_count: int = 1) -> list[tuple[str, object]]:
    """Parse the constrained project Markdown subset into typed rendering blocks."""

    lines = _strip_front_matter(markdown).splitlines()
    blocks: list[tuple[str, object]] = []
    paragraph: list[str] = []
    ordered: list[str] = []
    unordered: list[str] = []
    quote: list[str] = []
    table: list[tuple[str, ...]] = []
    skipped_cover_headings = 0

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(("paragraph", " ".join(part.strip() for part in paragraph)))
            paragraph.clear()

    def flush_ordered() -> None:
        if ordered:
            blocks.append(("ordered", tuple(ordered)))
            ordered.clear()

    def flush_unordered() -> None:
        if unordered:
            blocks.append(("unordered", tuple(unordered)))
            unordered.clear()

    def flush_quote() -> None:
        if quote:
            blocks.append(("quote", tuple(quote)))
            quote.clear()

    def flush_table() -> None:
        if table:
            rows = tuple(
                row
                for row in table
                if not all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in row)
            )
            if rows:
                blocks.append(("table", rows))
            table.clear()

    def flush_all() -> None:
        flush_paragraph()
        flush_ordered()
        flush_unordered()
        flush_quote()
        flush_table()

    for raw in lines:
        line = raw.strip()
        if not line:
            flush_all()
            continue
        if line.startswith("#"):
            flush_all()
            level = len(line) - len(line.lstrip("#"))
            heading = line[level:].strip()
            if skipped_cover_headings < cover_heading_count and level in {1, 2}:
                skipped_cover_headings += 1
                continue
            blocks.append(("heading2" if level == 2 else "heading3", heading))
            continue
        if line.startswith("|") and line.endswith("|"):
            flush_paragraph()
            flush_ordered()
            flush_unordered()
            flush_quote()
            table.append(tuple(cell.strip() for cell in line.strip("|").split("|")))
            continue
        ordered_match = re.match(r"^\d+\.\s+(.+)$", line)
        if ordered_match:
            flush_paragraph()
            flush_unordered()
            flush_quote()
            flush_table()
            ordered.append(ordered_match.group(1))
            continue
        unordered_match = re.match(r"^[-*+]\s+(.+)$", line)
        if unordered_match:
            flush_paragraph()
            flush_ordered()
            flush_quote()
            flush_table()
            unordered.append(unordered_match.group(1))
            continue
        if line.startswith(">"):
            flush_paragraph()
            flush_ordered()
            flush_unordered()
            flush_table()
            quote.append(line[1:].strip())
            continue
        flush_ordered()
        flush_unordered()
        flush_quote()
        flush_table()
        paragraph.append(line)

    flush_all()
    if not blocks:
        raise ValueError("Canonical Markdown source contains no renderable body content")
    return blocks


def _styles(body_font: str, bold_font: str) -> dict[str, ParagraphStyle]:
    """Create the immutable visual style contract for all government PDFs."""

    return {
        "body": ParagraphStyle(
            "AegisBody",
            fontName=body_font,
            fontSize=8.25,
            leading=10.25,
            textColor=BODY,
            alignment=TA_LEFT,
            spaceAfter=5.5,
            allowWidows=0,
            allowOrphans=0,
        ),
        "heading2": ParagraphStyle(
            "AegisHeading2",
            fontName=bold_font,
            fontSize=14,
            leading=16,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceBefore=7,
            spaceAfter=5,
            keepWithNext=True,
        ),
        "heading3": ParagraphStyle(
            "AegisHeading3",
            fontName=bold_font,
            fontSize=11,
            leading=13,
            textColor=NAVY,
            alignment=TA_LEFT,
            spaceBefore=5,
            spaceAfter=4,
            keepWithNext=True,
        ),
        "list": ParagraphStyle(
            "AegisList",
            fontName=body_font,
            fontSize=8.15,
            leading=10,
            textColor=BODY,
            alignment=TA_LEFT,
            spaceAfter=1.5,
        ),
        "quote": ParagraphStyle(
            "AegisQuote",
            fontName=bold_font,
            fontSize=8.1,
            leading=10.1,
            textColor=NAVY,
            leftIndent=10,
            borderColor=GOLD,
            borderWidth=1.5,
            borderPadding=(3, 5, 3, 8),
            spaceBefore=3,
            spaceAfter=6,
        ),
        "table_header": ParagraphStyle(
            "AegisTableHeader",
            fontName=bold_font,
            fontSize=7.2,
            leading=8.6,
            textColor=IVORY,
            alignment=TA_LEFT,
        ),
        "table_body": ParagraphStyle(
            "AegisTableBody",
            fontName=body_font,
            fontSize=7,
            leading=8.4,
            textColor=BODY,
            alignment=TA_LEFT,
        ),
        "cover_title": ParagraphStyle(
            "AegisCoverTitle",
            fontName=bold_font,
            fontSize=25,
            leading=29,
            textColor=GOLD,
            alignment=TA_LEFT,
        ),
        "cover_subtitle": ParagraphStyle(
            "AegisCoverSubtitle",
            fontName=body_font,
            fontSize=12.5,
            leading=16,
            textColor=IVORY,
            alignment=TA_LEFT,
        ),
    }


def _draw_cover(canvas, doc, spec: DocumentSpec, styles: dict[str, ParagraphStyle], logo: ImageReader) -> None:
    """Draw one branded cover page for a document specification."""

    width, height = A4
    canvas.saveState()
    canvas.setTitle(f"{spec.title} — {spec.language}")
    canvas.setAuthor("Pierre-Edward Procyk")
    canvas.setSubject("AI-IDP / AegisTrace")
    canvas.setCreator("Cognitive Industries — Les Industries Cognitives (AegisTrace)")
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, width, height, stroke=0, fill=1)
    canvas.setFillColor(GOLD)
    canvas.rect(0, height - 14, width, 14, stroke=0, fill=1)
    canvas.drawImage(logo, 188, 590, width=220, height=146, preserveAspectRatio=True, mask="auto")

    title = Paragraph(_inline_markup(spec.title), styles["cover_title"])
    _, title_height = title.wrap(width - 100, 90)
    title.drawOn(canvas, 50, 500 - title_height)

    subtitle = Paragraph(_inline_markup(spec.subtitle), styles["cover_subtitle"])
    _, subtitle_height = subtitle.wrap(width - 100, 100)
    subtitle.drawOn(canvas, 50, 450 - subtitle_height)

    canvas.setFillColor(IVORY)
    canvas.setFont(styles["body"].fontName, 8.2)
    y = 245
    for line in spec.contact_lines:
        canvas.drawString(50, y, line)
        y -= 12

    metadata = (
        f"Document ID: {spec.document_id}",
        "Version: 2.0.0",
        "Date: 2026-08-01",
        f"Classification: {spec.classification}",
    )
    y = 125
    for line in metadata:
        canvas.drawString(50, y, line)
        y -= 12

    rights = Paragraph(
        _inline_markup(
            f"© 2026 Pierre-Edward Procyk. Cognitive Industries — Les Industries Cognitives. "
            f"{spec.rights_text}"
        ),
        ParagraphStyle(
            "CoverRights",
            parent=styles["body"],
            fontSize=7.2,
            leading=9,
            textColor=IVORY,
            alignment=TA_LEFT,
        ),
    )
    rights.wrapOn(canvas, width - 100, 40)
    rights.drawOn(canvas, 50, 45)
    canvas.restoreState()


def _draw_body_page(canvas, doc, spec: DocumentSpec, body_font: str) -> None:
    """Draw the stable header, footer, and page number on a body page."""

    width, height = A4
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1.3)
    canvas.line(50, height - 46, width - 50, height - 46)
    canvas.setFillColor(MUTED)
    canvas.setFont(body_font, 5.8)
    canvas.drawString(50, height - 38, "Cognitive Industries — Les Industries Cognitives")
    canvas.drawRightString(width - 50, height - 38, "AI-IDP / AegisTrace")
    canvas.drawString(
        50,
        30,
        f"© 2026 Pierre-Edward Procyk | Cognitive Industries — Les Industries Cognitives | "
        f"{spec.rights_text}",
    )
    canvas.drawRightString(width - 50, 30, f"Page {canvas.getPageNumber()}")
    canvas.restoreState()


def _flowables(
    blocks: list[tuple[str, object]],
    styles: dict[str, ParagraphStyle],
    bold_font: str,
) -> list[object]:
    """Convert typed Markdown blocks into ReportLab flowables."""

    output: list[object] = []
    for kind, value in blocks:
        if kind in {"heading2", "heading3", "paragraph"}:
            style_name = "body" if kind == "paragraph" else kind
            output.append(Paragraph(_inline_markup(str(value)), styles[style_name]))
        elif kind == "quote":
            quote_lines = "<br/>".join(_inline_markup(str(line)) for line in value)
            output.append(Paragraph(quote_lines, styles["quote"]))
        elif kind == "ordered":
            items = [
                ListItem(Paragraph(_inline_markup(str(item)), styles["list"]), leftIndent=12)
                for item in value
            ]
            output.append(
                ListFlowable(
                    items,
                    bulletType="1",
                    start="1",
                    leftIndent=20,
                    bulletFontName=bold_font,
                    bulletFontSize=8.1,
                    bulletOffsetY=0,
                    spaceAfter=5,
                )
            )
        elif kind == "unordered":
            items = [
                ListItem(Paragraph(_inline_markup(str(item)), styles["list"]), leftIndent=12)
                for item in value
            ]
            output.append(
                ListFlowable(
                    items,
                    bulletType="bullet",
                    leftIndent=20,
                    bulletFontName=bold_font,
                    bulletFontSize=7.5,
                    bulletOffsetY=0,
                    spaceAfter=5,
                )
            )
        elif kind == "table":
            rows = tuple(value)
            column_count = max(len(row) for row in rows)
            padded_rows = tuple(row + ("",) * (column_count - len(row)) for row in rows)
            column_weights = [
                max(8, max(len(re.sub(r"[*_`]", "", row[index])) for row in padded_rows))
                for index in range(column_count)
            ]
            total_weight = sum(column_weights)
            available_width = A4[0] - 100
            widths = [available_width * weight / total_weight for weight in column_weights]
            rendered_rows = [
                [
                    Paragraph(_inline_markup(cell), styles["table_header" if row_index == 0 else "table_body"])
                    for cell in row
                ]
                for row_index, row in enumerate(padded_rows)
            ]
            table_flowable = Table(
                rendered_rows,
                colWidths=widths,
                repeatRows=1,
                hAlign="LEFT",
                splitByRow=1,
            )
            table_flowable.setStyle(
                TableStyle(
                    (
                        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                        ("TEXTCOLOR", (0, 0), (-1, 0), IVORY),
                        ("BACKGROUND", (0, 1), (-1, -1), HexColor("#F6F2E9")),
                        ("GRID", (0, 0), (-1, -1), 0.45, GOLD),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    )
                )
            )
            output.extend((Spacer(1, 3), table_flowable, Spacer(1, 7)))
        else:
            raise ValueError(f"Unsupported render block: {kind}")
    return output


def _validate_source(spec: DocumentSpec, markdown: str) -> None:
    """Fail before rendering if canonical release facts are absent or stale."""

    missing = [value for value in spec.required_text if value not in markdown]
    stale = [
        value
        for value in spec.forbidden_text
        if re.search(rf"(?<!\d){re.escape(value)}(?!\d)", markdown)
    ]
    if missing:
        raise ValueError(f"{spec.source}: missing required release facts {missing}")
    if stale:
        raise ValueError(f"{spec.source}: stale release facts remain {stale}")
    if "[INSERT " in markdown or "[ARXIV LINK]" in markdown or "[GITHUB LINK]" in markdown:
        raise ValueError(f"{spec.source}: unresolved publishing placeholder")


def _validate_pdf(spec: DocumentSpec, pdf_path: Path) -> dict[str, object]:
    """Reopen the generated PDF and verify its semantic release contract."""

    reader = PdfReader(str(pdf_path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    required = (*spec.required_text, spec.document_id)
    forbidden = spec.forbidden_text
    missing = [value for value in required if value not in text]
    stale = [value for value in forbidden if re.search(rf"(?<!\d){re.escape(value)}(?!\d)", text)]
    if missing:
        raise ValueError(f"{spec.output}: generated PDF is missing {missing}")
    if stale:
        raise ValueError(f"{spec.output}: generated PDF contains stale facts {stale}")
    if len(reader.pages) < spec.minimum_pages:
        raise ValueError(f"{spec.output}: generated PDF has an implausible page count")
    return {"pages": len(reader.pages), "characters": len(text)}


def _normalise_metadata(spec: DocumentSpec, pdf_path: Path) -> None:
    """Set stable release metadata without altering rendered page content."""

    descriptor, normalized_name = tempfile.mkstemp(
        prefix=f".{spec.output.stem}.metadata.",
        suffix=".tmp.pdf",
        dir=spec.output.parent,
    )
    os.close(descriptor)
    normalized = Path(normalized_name)
    try:
        writer = PdfWriter(clone_from=str(pdf_path))
        writer.add_metadata(
            {
                "/Title": f"{spec.title} — {spec.language}",
                "/Author": "Pierre-Edward Procyk",
                "/Subject": "AI-IDP / AegisTrace",
                "/Creator": "Cognitive Industries — Les Industries Cognitives (AegisTrace)",
                "/CreationDate": "D:20260801000000-04'00'",
                "/ModDate": "D:20260801000000-04'00'",
            }
        )
        with normalized.open("wb") as output_stream:
            writer.write(output_stream)
        os.replace(normalized, pdf_path)
    finally:
        normalized.unlink(missing_ok=True)


def build_document(spec: DocumentSpec, body_font: str, bold_font: str) -> dict[str, object]:
    """Render one validated source atomically to its stable delivery path."""

    if not spec.source.is_file():
        raise FileNotFoundError(f"Canonical source not found: {spec.source}")
    if not BRAND_LOGO.is_file():
        raise FileNotFoundError(f"Official brand logo not found: {BRAND_LOGO}")

    markdown = spec.source.read_text(encoding="utf-8-sig")
    _validate_source(spec, markdown)
    blocks = _parse_markdown(markdown, spec.cover_heading_count)
    styles = _styles(body_font, bold_font)
    logo = ImageReader(str(BRAND_LOGO))
    spec.output.parent.mkdir(parents=True, exist_ok=True)

    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{spec.output.stem}.",
        suffix=".tmp.pdf",
        dir=spec.output.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        width, height = A4
        cover_frame = Frame(0, 0, width, height, id="cover")
        body_frame = Frame(50, 55, width - 100, height - 116, id="body")
        document = BaseDocTemplate(
            str(temporary),
            pagesize=A4,
            leftMargin=50,
            rightMargin=50,
            topMargin=61,
            bottomMargin=55,
            title=spec.title,
            author="Pierre-Edward Procyk",
            subject="AI-IDP / AegisTrace",
            creator="Cognitive Industries — Les Industries Cognitives (AegisTrace)",
        )
        document.addPageTemplates(
            (
                PageTemplate(
                    id="cover",
                    frames=(cover_frame,),
                    onPage=lambda canvas, doc: _draw_cover(canvas, doc, spec, styles, logo),
                ),
                PageTemplate(
                    id="body",
                    frames=(body_frame,),
                    onPage=lambda canvas, doc: _draw_body_page(canvas, doc, spec, body_font),
                ),
            )
        )
        story: list[object] = [NextPageTemplate("body"), PageBreak(), Spacer(1, 2)]
        story.extend(_flowables(blocks, styles, bold_font))
        document.build(story)
        _normalise_metadata(spec, temporary)
        validation = _validate_pdf(spec, temporary)
        os.replace(temporary, spec.output)
    finally:
        temporary.unlink(missing_ok=True)

    return {
        "key": spec.key,
        "source": str(spec.source),
        "output": str(spec.output),
        **validation,
    }


def main() -> int:
    """Build the requested government-facing PDFs and report their validation summary."""

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only",
        choices=tuple(DOCUMENTS),
        action="append",
        help="Build only the selected document key; repeat to select more than one.",
    )
    args = parser.parse_args()
    selected = args.only or list(DOCUMENTS)
    body_font, bold_font = _register_fonts()
    for key in selected:
        result = build_document(DOCUMENTS[key], body_font, bold_font)
        print(
            f"{result['key']}: {result['pages']} pages, {result['characters']} extracted characters -> "
            f"{result['output']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
