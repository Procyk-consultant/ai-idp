# AI-IDP / AegisTrace — Complete Deployment Automation Package

**Generated:** 2026-08-02  
**Project Root:** `C:\Cognitive Industries\AI-IDP-AegisTrace`  
**GitHub:** https://github.com/Procyk-consultant/ai-idp  
**Zenodo:** https://zenodo.org

---

## 🎯 One-Command Deployment

```bash
cd "C:\Cognitive Industries\AI-IDP-AegisTrace"
python scripts\deploy_all.py --github-token $GITHUB_TOKEN --zenodo-token $ZENODO_TOKEN
```

**Required env vars (set once):**
```powershell
$env:GITHUB_TOKEN = "ghp_xxx"          # GitHub PAT with 'repo' scope
$env:ZENODO_TOKEN = "xxx"              # Zenodo PAT from zenodo.org/account/settings/applications/
```

---

## 📦 What It Does (Fully Automated)

| Step | Action | Method |
|---|---|---|
| 1 | Verify local repo clean | `git status --porcelain` |
| 2 | Force-push cleaned history to GitHub | `git push --force origin main` (uses `GITHUB_TOKEN`) |
| 3 | Create Zenodo deposition | REST API `POST /api/deposit/depositions` (uses `ZENODO_TOKEN`) |
| 4 | Upload files | REST API `POST /api/deposit/depositions/{id}/files` |
| 5 | Publish deposition | REST API `POST /api/deposit/depositions/{id}/actions/publish` |
| 6 | Get DOI | Parse response |
| 7 | Update local metadata | `CITATION.cff`, `README.md`, `paper/main.tex` |
| 8 | Commit & push updates | `git push origin main` |

---

## 🔧 GitHub Force Push (Browser Alternative)

If CLI fails, use browser:

1. Open https://github.com/Procyk-consultant/ai-idp in your **logged-in Chrome/Comet**
2. Navigate to **Settings → Branches**
3. Delete branch protection on `main` (if any)
4. Open terminal locally:
   ```bash
   cd "C:\Cognitive Industries\AI-IDP-AegisTrace"
   git push --force origin main
   ```
5. Re-enable branch protection

---

## 🌐 Zenodo Deposition (API Method)

### Prerequisites
- Zenodo account logged in via browser
- Personal Access Token: `https://zenodo.org/account/settings/applications/` → "New token" → `deposit:write deposit:actions`

### Files to Upload (from official root)
| File | Description |
|---|---|
| `paper/main.pdf` | Compiled paper (13 pages, 58 refs, 111 tests) |
| `AI-IDP-AegisTrace-2.0.0-source.zip` | Clean source (no sensitive files) |
| `OFFICIAL_PROJECT_DOCUMENT_EN.pdf` | Official English document |
| `DOCUMENT_OFFICIEL_PROJET_FR.pdf` | Official French document |
| `paper/main.tex` | LaTeX source |
| `paper/references.bib` | Bibliography (58 entries) |

### Metadata (Auto-Generated)
```json
{
  "metadata": {
    "title": "Identity Before Autonomy: A Universal Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation",
    "upload_type": "publication",
    "publication_type": "article",
    "description": "<abstract from paper/main.tex>",
    "creators": [{"name": "Procyk, Pierre-Edward", "affiliation": "Cognitive Industries — Les Industries Cognitives", "orcid": "YOUR_ORCID"}],
    "keywords": ["AI governance", "AI accountability", "AI identity", "provenance", "traceability", "audit", "permanent record", "delegation", "authorization", "Canadian law", "PIPEDA", "AIDA", "Algorithmic Impact Assessment", "Ed25519", "hash chain", "Merkle tree", "registry", "federation", "privacy", "human rights", "Indigenous data sovereignty", "OCAP", "TRC Calls to Action"],
    "access_right": "open",
    "license": "cc-by-4.0",
    "publication_date": "2026-08-02",
    "version": "2.0.0",
    "related_identifiers": [
      {"relation": "isSupplementTo", "identifier": "https://github.com/Procyk-consultant/ai-idp", "scheme": "url"}
    ]
  }
}
```

---

## 🚀 Complete Automation Script

**File:** `C:\Cognitive Industries\AI-IDP-AegisTrace\scripts\deploy_all.py`

```python
#!/usr/bin/env python3
"""
AI-IDP / AegisTrace — Complete Deployment Automation
Deploys to GitHub (force push) and Zenodo (API deposition) in one run.
"""
import os, sys, json, subprocess, zipfile, requests
from pathlib import Path
from datetime import datetime

ROOT = Path(r"C:\Cognitive Industries\AI-IDP-AegisTrace")
GITHUB_REPO = "Procyk-consultant/ai-idp"
ZENODO_API = "https://zenodo.org/api"

def run(cmd, cwd=ROOT, env=None):
    """Run command, return (success, stdout, stderr)."""
    e = os.environ.copy()
    if env: e.update(env)
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=e, shell=True)
    return p.returncode == 0, p.stdout.strip(), p.stderr.strip()

def verify_repo():
    ok, out, _ = run("git status --porcelain")
    if out.strip():
        print(f"⚠️  Uncommitted changes:\n{out}")
        return False
    print("✅ Repo clean")
    return True

def github_force_push(token):
    env = {"GITHUB_TOKEN": token}
    ok, out, err = run("git push --force origin main", env=env)
    if ok:
        print("✅ GitHub force push successful")
        return True
    print(f"❌ GitHub push failed: {err}")
    return False

def create_source_zip():
    zip_path = ROOT / "AI-IDP-AegisTrace-2.0.0-source.zip"
    exclude = {
        '.venv', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache',
        '.git', '.github', 'release', 'backups', '*.log', '*.zip',
        'OFFICIAL_EMAIL_TEMPLATES.md', 'LINKEDIN_CONTENT_TEMPLATES.md',
        'ARXIV_SUBMISSION_INSTRUCTIONS.md', 'GITHUB_PUSH_INSTRUCTIONS.md',
        'OFFICIAL_PROJECT_DOCUMENT_EN.pdf', 'DOCUMENT_OFFICIEL_PROJET_FR.pdf',
        'government/OFFICIAL_PROJECT_DOCUMENT_EN.md',
        'government/DOCUMENT_OFFICIEL_PROJET_FR.md',
    }
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for f in ROOT.rglob('*'):
            if f.is_file():
                rel = f.relative_to(ROOT)
                if not any(ex in str(rel) for ex in exclude):
                    zf.write(f, f"AI-IDP-AegisTrace-2.0.0/{rel}")
    print(f"✅ Source zip created: {zip_path} ({zip_path.stat().st_size/1e6:.1f} MB)")
    return zip_path

def zenodo_create(token):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "metadata": {
            "title": "Identity Before Autonomy: A Universal Framework for Persistent AI Actor Identity, Permanent Traceability, Delegation, Quality Assurance, and Accountable AI Operation",
            "upload_type": "publication",
            "publication_type": "article",
            "description": open(ROOT/"paper"/"main.tex").read().split("\\begin{abstract}")[1].split("\\end{abstract}")[0].strip(),
            "creators": [{"name": "Procyk, Pierre-Edward", "affiliation": "Cognitive Industries — Les Industries Cognitives"}],
            "keywords": ["AI governance", "AI accountability", "AI identity", "provenance", "traceability", "audit", "permanent record", "delegation", "authorization", "Canadian law", "PIPEDA", "AIDA", "Ed25519", "hash chain", "Merkle tree", "registry", "federation", "privacy", "human rights", "Indigenous data sovereignty", "OCAP", "TRC Calls to Action"],
            "access_right": "open",
            "license": "cc-by-4.0",
            "publication_date": "2026-08-02",
            "version": "2.0.0",
        }
    }
    r = requests.post(f"{ZENODO_API}/deposit/depositions", headers=headers, json=data)
    r.raise_for_status()
    dep = r.json()
    print(f"✅ Zenodo deposition created: {dep['id']}")
    return dep['id'], dep['links']['files']

def zenodo_upload_files(dep_id, files_url, token, file_paths):
    headers = {"Authorization": f"Bearer {token}"}
    for fp in file_paths:
        with open(fp, 'rb') as f:
            data = {"name": Path(fp).name}
            r = requests.post(files_url, headers=headers, data=data, files={"file": f})
            r.raise_for_status()
            print(f"✅ Uploaded: {Path(fp).name}")
    return True

def zenodo_publish(dep_id, token):
    r = requests.post(f"{ZENODO_API}/deposit/depositions/{dep_id}/actions/publish",
                      headers={"Authorization": f"Bearer {token}"})
    r.raise_for_status()
    dep = r.json()
    doi = dep.get('doi') or dep.get('metadata', {}).get('doi')
    print(f"✅ Published! DOI: {doi}")
    return doi

def update_metadata(doi):
    # Update CITATION.cff
    cit = (ROOT/"CITATION.cff").read_text(encoding="utf-8")
    cit = cit.replace("doi: ", f"doi: {doi}")
    (ROOT/"CITATION.cff").write_text(cit, encoding="utf-8")
    
    # Update README.md
    readme = (ROOT/"README.md").read_text(encoding="utf-8")
    if "Zenodo" not in readme:
        badge = f"[![DOI](https://zenodo.org/badge/DOI/{doi}.svg)](https://doi.org/{doi})"
        readme = readme.replace("# AI-IDP", f"# AI-IDP\n{badge}")
        (ROOT/"README.md").write_text(readme, encoding="utf-8")
    
    # Update paper/main.tex
    tex = (ROOT/"paper"/"main.tex").read_text(encoding="utf-8")
    if "\\date{" in tex:
        tex = tex.replace("\\date{", f"\\date{{Zenodo DOI: {doi} \\\\ ")
        (ROOT/"paper"/"main.tex").write_text(tex, encoding="utf-8")
    
    # Commit updates
    run("git add CITATION.cff README.md paper/main.tex")
    run('git commit -m "chore: add Zenodo DOI"')
    run("git push origin main")
    print("✅ Metadata updated and pushed")

def main():
    github_token = os.getenv("GITHUB_TOKEN")
    zenodo_token = os.getenv("ZENODO_TOKEN")
    
    if not github_token:
        print("❌ GITHUB_TOKEN not set")
        return 1
    if not zenodo_token:
        print("❌ ZENODO_TOKEN not set")
        return 1
    
    print("🚀 Starting AI-IDP / AegisTrace deployment...")
    
    if not verify_repo():
        return 1
    
    print("\n1️⃣ GitHub force push...")
    if not github_force_push(github_token):
        return 1
    
    print("\n2️⃣ Creating source zip...")
    zip_path = create_source_zip()
    
    print("\n3️⃣ Zenodo deposition...")
    files = [
        ROOT/"paper"/"main.pdf",
        ROOT/"paper"/"main.tex",
        ROOT/"paper"/"references.bib",
        ROOT/"OFFICIAL_PROJECT_DOCUMENT_EN.pdf",
        ROOT/"DOCUMENT_OFFICIEL_PROJET_FR.pdf",
        ROOT/"AI-IDP-AegisTrace-2.0.0-source.zip",
    ]
    files = [str(f) for f in files if Path(f).exists()]
    
    dep_id, files_url = zenodo_create(os.getenv("ZENODO_TOKEN"))
    zenodo_upload_files(dep_id, files_url, os.getenv("ZENODO_TOKEN"), files)
    doi = zenodo_publish(dep_id, os.getenv("ZENODO_TOKEN"))
    
    print("\n4️⃣ Updating metadata...")
    update_metadata(doi)
    
    print(f"\n🎉 DEPLOYMENT COMPLETE!")
    print(f"   GitHub: https://github.com/Procyk-consultant/ai-idp")
    print(f"   Zenodo: https://doi.org/{doi}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

---

## 📋 Manual Checklist (If Automation Fails)

### GitHub Force Push
- [ ] Open terminal at `C:\Cognitive Industries\AI-IDP-AegisTrace`
- [ ] Run: `git push --force origin main`
- [ ] Verify at https://github.com/Procyk-consultant/ai-idp

### Zenodo Deposition
- [ ] Log into Zenodo (ORCID/GitHub/email)
- [ ] Get PAT: https://zenodo.org/account/settings/applications/
- [ ] Run Python script OR manual upload:
  1. https://zenodo.org/deposit/new
  2. Fill metadata (see JSON above)
  3. Upload files (PDF, ZIP, TeX, Bib)
  4. Publish → Get DOI
- [ ] Update local files with DOI

### Post-Deployment
- [ ] Update `CITATION.cff` with DOI
- [ ] Update `README.md` with Zenodo badge
- [ ] Update `paper/main.tex` with DOI
- [ ] Commit & push: `git add . && git commit -m "chore: add Zenodo DOI" && git push`

---

## 💾 Saved Permanently

This document saved to:
- `C:\Cognitive Industries\AI-IDP-AegisTrace\scripts\DEPLOYMENT_SOP.md`
- `C:\Cognitive Industries\AI-IDP-AegisTrace\scripts\deploy_all.py`

Run anytime:
```bash
cd "C:\Cognitive Industries\AI-IDP-AegisTrace"
$env:GITHUB_TOKEN="ghp_xxx"; $env:ZENODO_TOKEN="xxx"
python scripts\deploy_all.py
```

---

## 🔐 Security Notes

- **Never commit tokens** — use environment variables only
- **Sensitive files already purged** from Git history via `git filter-repo`
- **Official root immutable** — `C:\Cognitive Industries\AI-IDP-AegisTrace` read-only
- **Zenodo DOI** makes it citable for government outreach

---

**End of Deployment Package**  
*Generated 2026-08-02 | AI-IDP / AegisTrace v2.0.0*