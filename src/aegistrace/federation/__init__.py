"""AI-IDP federation primitives."""
from aegistrace.federation.gateway import (
    FederatedRegistryClient,
    FederationAgreement,
    FederationBreak,
    FederationGateway,
    FederationResolutionError,
    HTTPFederatedRegistryClient,
)

__all__ = [
    "FederatedRegistryClient",
    "FederationAgreement",
    "FederationBreak",
    "FederationGateway",
    "FederationResolutionError",
    "HTTPFederatedRegistryClient",
]
