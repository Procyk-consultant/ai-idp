"""Cognitive Industries — Les Industries Cognitives
Project: AI-IDP / AegisTrace
Author and Intellectual Property Owner: Pierre-Edward Procyk
Copyright: © 2026 Pierre-Edward Procyk. All rights reserved.
File: src/aegistrace/governance/__init__.py
Purpose: Governed execution package
Classification: service
Version: 2.0.0
Last Material Revision: 2026-08-17
Licence Status: No licence selected unless approved in writing by Pierre-Edward Procyk.
"""

from aegistrace.governance.service import GovernanceDenied, GovernedEventService

__all__ = ["GovernanceDenied", "GovernedEventService"]
