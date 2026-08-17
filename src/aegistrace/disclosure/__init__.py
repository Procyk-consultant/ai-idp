"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/disclosure/__init__.py
Purpose: Visibility-tier disclosure package
Classification: service
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""

from aegistrace.disclosure.public import PublicEventProjector, PublicProjectionError

__all__ = ["PublicEventProjector", "PublicProjectionError"]
