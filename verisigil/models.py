"""
VeriSigil SDK — Response Models
Typed wrappers around API responses for IDE autocomplete and type safety.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any


@dataclass
class GovernanceResult:
    """
    Result of a govern() call.
    The core primitive — admissibility + evidence in one object.
    """
    admissible:       bool
    ruling:           str          # ADMISSIBLE / CONDITIONALLY_ADMISSIBLE / INADMISSIBLE / REQUIRES_HUMAN_DECISION
    action:           str          # What to do next
    admissibility_id: str
    signature:        str          # Ed25519 governance signature
    timestamp:        str
    agent_id:         str
    action_type:      str
    consequence:      str
    signals:          List[dict]   = field(default_factory=list)
    conditions:       List[str]    = field(default_factory=list)
    reasons:          List[str]    = field(default_factory=list)
    raw:              Dict         = field(default_factory=dict)

    def __bool__(self):
        """Allows: if vs.govern(...): proceed()"""
        return self.admissible

    def __repr__(self):
        return (
            f"GovernanceResult("
            f"admissible={self.admissible}, "
            f"ruling={self.ruling!r}, "
            f"id={self.admissibility_id!r})"
        )

    @classmethod
    def from_dict(cls, data: dict) -> "GovernanceResult":
        return cls(
            admissible       = data.get("admissible", False),
            ruling           = data.get("ruling", "INADMISSIBLE"),
            action           = data.get("action", ""),
            admissibility_id = data.get("admissibility_id", ""),
            signature        = data.get("governance_signature", ""),
            timestamp        = data.get("timestamp", ""),
            agent_id         = data.get("agent_id", ""),
            action_type      = data.get("action_type", ""),
            consequence      = data.get("consequence_class", ""),
            signals          = data.get("signals", []),
            conditions       = data.get("conditions", []),
            reasons          = data.get("inadmissible_reasons", []),
            raw              = data,
        )


@dataclass
class DocumentVerifyResult:
    """Result of a document integrity verification."""
    corruption_detected:  bool
    corruption_score:     float
    integrity_score:      float
    overall_severity:     str
    governance_decision:  dict
    signature:            str
    verify_id:            str
    detection_layers:     Dict     = field(default_factory=dict)
    hashes:               Dict     = field(default_factory=dict)
    raw:                  Dict     = field(default_factory=dict)

    @property
    def clean(self) -> bool:
        return not self.corruption_detected

    @property
    def decision(self) -> str:
        return self.governance_decision.get("decision", "UNKNOWN")

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentVerifyResult":
        return cls(
            corruption_detected = data.get("corruption_detected", False),
            corruption_score    = data.get("corruption_score", 0.0),
            integrity_score     = data.get("integrity_score", 0.0),
            overall_severity    = data.get("overall_severity", "NONE"),
            governance_decision = data.get("governance_decision", {}),
            signature           = data.get("governance_signature", ""),
            verify_id           = data.get("verify_id", ""),
            detection_layers    = data.get("detection_layers", {}),
            hashes              = data.get("document_hashes", {}),
            raw                 = data,
        )


@dataclass
class AdmissibilityResult:
    """Result of an admissibility check."""
    admissible:       bool
    ruling:           str
    action:           str
    admissibility_id: str
    signature:        str
    signals:          List[dict] = field(default_factory=list)
    conditions:       List[str]  = field(default_factory=list)
    raw:              Dict       = field(default_factory=dict)

    def __bool__(self):
        return self.admissible

    @classmethod
    def from_dict(cls, data: dict) -> "AdmissibilityResult":
        return cls(
            admissible       = data.get("admissible", False),
            ruling           = data.get("ruling", "INADMISSIBLE"),
            action           = data.get("action", ""),
            admissibility_id = data.get("admissibility_id", ""),
            signature        = data.get("governance_signature", ""),
            signals          = data.get("signals", []),
            conditions       = data.get("conditions", []),
            raw              = data,
        )


@dataclass
class EUAIActResult:
    """Result of an EU AI Act compliance assessment."""
    compliance_score:  float
    compliance_level:  str
    risk_category:     str
    gaps_found:        int
    gaps:              List[dict]
    days_remaining:    int
    fine_exposure:     Any
    urgency:           str
    assessment_id:     str
    remediation_plan:  List[dict] = field(default_factory=list)
    raw:               Dict       = field(default_factory=dict)

    @property
    def compliant(self) -> bool:
        return self.compliance_level == "COMPLIANT"

    @property
    def critical_gaps(self) -> List[dict]:
        return [g for g in self.gaps if g.get("severity") == "CRITICAL"]

    @classmethod
    def from_dict(cls, data: dict) -> "EUAIActResult":
        return cls(
            compliance_score = data.get("compliance_score", 0.0),
            compliance_level = data.get("compliance_level", "NON_COMPLIANT"),
            risk_category    = data.get("risk_category", "UNKNOWN"),
            gaps_found       = data.get("gaps_found", 0),
            gaps             = data.get("gaps", []),
            days_remaining   = data.get("days_remaining", 0),
            fine_exposure    = data.get("fine_exposure_eur", "N/A"),
            urgency          = data.get("urgency", ""),
            assessment_id    = data.get("assessment_id", ""),
            remediation_plan = data.get("remediation_plan", []),
            raw              = data,
        )


@dataclass
class VESCertificate:
    """A VES-1.0 certified evidence bundle."""
    ves_id:           str
    canonical_hash:   str
    court_admissible: bool
    jurisdiction:     str
    issued_at:        str
    ves_signature:    str
    bundle_valid:     bool
    raw:              Dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "VESCertificate":
        cert = data.get("certificate", data)
        return cls(
            ves_id           = cert.get("ves_id", ""),
            canonical_hash   = cert.get("canonical_hash", ""),
            court_admissible = cert.get("court_admissible", False),
            jurisdiction     = cert.get("jurisdiction", ""),
            issued_at        = cert.get("issued_at", ""),
            ves_signature    = cert.get("ves_signature", ""),
            bundle_valid     = cert.get("bundle_valid", False),
            raw              = data,
        )


@dataclass
class LitigationPackage:
    """A court-admissible litigation evidence dossier."""
    package_id:        str
    court_admissible:  bool
    jurisdiction:      str
    package_hash:      str
    package_signature: str
    certified_bundles: List[dict]
    chain_of_custody:  List[dict]
    legal_notice:      str
    raw:               Dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict) -> "LitigationPackage":
        return cls(
            package_id        = data.get("package_id", ""),
            court_admissible  = data.get("court_admissible", False),
            jurisdiction      = data.get("jurisdiction", ""),
            package_hash      = data.get("package_hash", ""),
            package_signature = data.get("package_signature", ""),
            certified_bundles = data.get("certified_evidence_bundles", []),
            chain_of_custody  = data.get("chain_of_custody", []),
            legal_notice      = data.get("legal_notice", ""),
            raw               = data,
        )
