"""
VeriSigil AI — Python SDK
Operational Admissibility Infrastructure for Autonomous Enterprise AI

pip install verisigil

Quick start:
    from verisigil import VeriSigil

    vs = VeriSigil(api_key="your-key")
    result = vs.govern(agent="finance-agent", action="wire_transfer", consequence="CRITICAL")
    print(result.admissible)  # True / False
    print(result.signature)   # Ed25519 governance signature
"""

from .client import VeriSigil
from .govern import govern
from .models import (
    GovernanceResult,
    DocumentVerifyResult,
    AdmissibilityResult,
    EUAIActResult,
    VESCertificate,
    LitigationPackage,
)
from .exceptions import (
    VeriSigilError,
    AuthenticationError,
    AdmissibilityError,
    RateLimitError,
)

__version__ = "0.1.0"
__author__  = "VeriSigil AI"
__email__   = "info@verisigilai.com"
__url__     = "https://verisigilai.com"

__all__ = [
    "VeriSigil",
    "govern",
    "GovernanceResult",
    "DocumentVerifyResult",
    "AdmissibilityResult",
    "EUAIActResult",
    "VESCertificate",
    "LitigationPackage",
    "VeriSigilError",
    "AuthenticationError",
    "AdmissibilityError",
    "RateLimitError",
]
