"""
VeriSigil SDK — Main Client
The complete VeriSigil API wrapped in a clean Python interface.
"""

import json
import urllib.request
import urllib.error
from typing import Optional, List, Dict, Any

from .models import (
    GovernanceResult, DocumentVerifyResult, AdmissibilityResult,
    EUAIActResult, VESCertificate, LitigationPackage,
)
from .exceptions import (
    VeriSigilError, AuthenticationError, AdmissibilityError,
    RateLimitError, TimelockError, ValidationError,
)

DEFAULT_BASE_URL = "https://verisigil-api-production.up.railway.app"


class VeriSigil:
    """
    VeriSigil AI Python SDK.

    Operational Admissibility Infrastructure for Autonomous Enterprise AI.

    Usage:
        from verisigil import VeriSigil

        vs = VeriSigil(api_key="your-key")

        # Govern any AI action before execution
        result = vs.govern(
            agent="finance-agent",
            action="wire_transfer",
            consequence="CRITICAL",
            irreversible=True,
        )
        if result:
            execute_transfer()
        else:
            escalate_to_human(result.ruling, result.signature)

        # Verify document integrity
        doc = vs.verify_document(
            original_text="Payment within 30 days...",
            generated_text="Payment within 300 days...",
            consequence="CRITICAL",
        )
        if doc.corruption_detected:
            block_document(doc.signature)

        # EU AI Act compliance assessment
        compliance = vs.eu_ai_act_assess(
            org_name="Acme Bank",
            use_case="AI loan approval for EU retail customers",
            sector="finance",
        )
        print(f"Compliance score: {compliance.compliance_score}/100")
        print(f"Fine exposure: {compliance.fine_exposure}")
    """

    def __init__(
        self,
        api_key:  str,
        base_url: str = DEFAULT_BASE_URL,
        timeout:  int = 30,
    ):
        if not api_key:
            raise AuthenticationError("api_key is required")
        self.api_key  = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout  = timeout

    # ── INTERNAL HTTP ─────────────────────────────────────────

    def _request(
        self,
        method:   str,
        path:     str,
        body:     dict = None,
        public:   bool = False,
    ) -> dict:
        """Make an authenticated request to the VeriSigil API."""
        url  = f"{self.base_url}{path}"
        data = json.dumps(body).encode() if body else None

        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if not public:
            headers["x-api-key"] = self.api_key

        req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())

        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            body_str = e.read().decode()
            try:
                detail = json.loads(body_str)
            except Exception:
                detail = {"detail": body_str}

            if e.code == 401:
                raise AuthenticationError(
                    "Invalid or missing API key. Check your api_key.",
                    status_code=401, detail=detail
                )
            elif e.code == 422:
                raise ValidationError(
                    f"Validation error: {detail.get('detail', body_str)}",
                    status_code=422, detail=detail
                )
            elif e.code == 425:
                remaining = detail.get("detail", {})
                if isinstance(remaining, dict):
                    hours = remaining.get("remaining_hours", 0)
                else:
                    hours = 0
                raise TimelockError(
                    f"Operation is time-locked. {hours} hours remaining.",
                    remaining_hours=hours
                )
            elif e.code == 429:
                raise RateLimitError(
                    "Rate limit exceeded. Slow down requests.",
                    status_code=429
                )
            else:
                raise VeriSigilError(
                    f"API error {e.code}: {detail.get('detail', body_str)}",
                    status_code=e.code, detail=detail
                )
        except urllib.error.URLError as e:
            raise VeriSigilError(f"Connection error: {e.reason}")

    # ── CORE: GOVERN ──────────────────────────────────────────

    def govern(
        self,
        agent:           str,
        action:          str,
        consequence:     str   = "OPERATIONAL",
        authority_scope: list  = None,
        tools_invoked:   list  = None,
        external_systems:list  = None,
        irreversible:    bool  = False,
        human_present:   bool  = False,
        trust_score:     float = 0.963,
        workflow_step:   int   = 1,
        jurisdiction:    str   = "EU",
        raise_on_inadmissible: bool = False,
    ) -> GovernanceResult:
        """
        Govern any AI action. The core VeriSigil primitive.

        Continuously determines whether this action is admissible
        at this exact moment under current authority, context,
        and consequence conditions.

        Args:
            agent:           Agent identifier
            action:          Action type being performed
            consequence:     MINIMAL / LOW / OPERATIONAL / HIGH / CRITICAL / EMERGENCY
            authority_scope: List of granted authorities
            tools_invoked:   Tools being called in this action
            external_systems:External systems being touched
            irreversible:    Whether this action cannot be undone
            human_present:   Whether a human is available to oversee
            trust_score:     Current agent trust score (0.0-1.0)
            workflow_step:   Step number in the workflow
            jurisdiction:    EU / US / UK / GLOBAL
            raise_on_inadmissible: Raise AdmissibilityError if not admissible

        Returns:
            GovernanceResult — use as bool: if vs.govern(...): proceed()

        Example:
            result = vs.govern(
                agent="finance-agent",
                action="wire_transfer",
                consequence="CRITICAL",
                irreversible=True,
                human_present=True,
            )
            if result:
                execute()
            else:
                escalate(result.ruling)
        """
        resp = self._request("POST", "/v1/admissibility/check", {
            "agent_id":          agent,
            "action_type":       action,
            "consequence_class": consequence,
            "authority_scope":   authority_scope or [],
            "tools_invoked":     tools_invoked or [],
            "external_systems":  external_systems or [],
            "irreversible":      irreversible,
            "human_present":     human_present,
            "trust_score":       trust_score,
            "workflow_step":     workflow_step,
            "jurisdiction":      jurisdiction,
            "current_state":     "EXECUTING",
        })

        result = GovernanceResult.from_dict(resp)

        if raise_on_inadmissible and not result.admissible:
            raise AdmissibilityError(
                f"Action '{action}' ruled {result.ruling}: {result.action}",
                ruling=resp,
            )

        return result

    # ── DOCUMENT INTEGRITY ────────────────────────────────────

    def verify_document(
        self,
        original_text:  str,
        generated_text: str,
        document_id:    str  = "doc-001",
        context:        str  = "general",
        consequence:    str  = "OPERATIONAL",
        agent_id:       str  = "sdk-agent",
    ) -> DocumentVerifyResult:
        """
        Verify document integrity using 4-layer detection.

        Detects:
        - Semantic drift
        - Clause mutation
        - Intent corruption
        - Numerical inconsistency

        Returns Ed25519-sealed evidence bundle.

        Example:
            doc = vs.verify_document(
                original_text="Payment within 30 days. No sub-delegation.",
                generated_text="Payment within 300 days. Sub-delegation allowed.",
                consequence="CRITICAL",
            )
            if doc.corruption_detected:
                quarantine(doc.signature)
        """
        resp = self._request("POST", "/v1/document/verify", {
            "document_id":   document_id,
            "original_text": original_text,
            "generated_text":generated_text,
            "context":       context,
            "consequence":   consequence,
            "agent_id":      agent_id,
        })
        return DocumentVerifyResult.from_dict(resp)

    # ── EU AI ACT ─────────────────────────────────────────────

    def eu_ai_act_assess(
        self,
        use_case:            str,
        org_name:            str   = "My Organisation",
        sector:              str   = "general",
        affects_humans:      bool  = True,
        has_audit_trail:     bool  = False,
        has_human_oversight: bool  = False,
        has_risk_assessment: bool  = False,
        has_technical_docs:  bool  = False,
        has_data_governance: bool  = False,
        has_monitoring:      bool  = False,
        annual_revenue_eur:  float = 0.0,
        jurisdiction:        str   = "EU",
    ) -> EUAIActResult:
        """
        EU AI Act compliance assessment.

        Returns risk classification, compliance gaps per Article,
        fine exposure calculation, and remediation plan.

        Deadline: August 2, 2026.
        Fine: €30M or 6% of global annual revenue.

        Example:
            result = vs.eu_ai_act_assess(
                use_case="AI loan approval for EU retail customers",
                org_name="Acme Bank",
                sector="finance",
                annual_revenue_eur=500_000_000,
            )
            print(f"Score: {result.compliance_score}/100")
            print(f"Fine exposure: €{result.fine_exposure:,.0f}")
            for gap in result.critical_gaps:
                print(f"CRITICAL: {gap['article']}")
        """
        resp = self._request("POST", "/v1/eu-aiact/assess", {
            "org_name":            org_name,
            "use_case":            use_case,
            "sector":              sector,
            "affects_humans":      affects_humans,
            "has_audit_trail":     has_audit_trail,
            "has_human_oversight": has_human_oversight,
            "has_risk_assessment": has_risk_assessment,
            "has_technical_docs":  has_technical_docs,
            "has_data_governance": has_data_governance,
            "has_monitoring":      has_monitoring,
            "annual_revenue_eur":  annual_revenue_eur,
            "jurisdiction":        jurisdiction,
        })
        return EUAIActResult.from_dict(resp)

    def eu_ai_act_deadline(self) -> dict:
        """Get days remaining to EU AI Act enforcement deadline."""
        return self._request("GET", "/v1/eu-aiact/deadline", public=True)

    # ── VES-1.0 EVIDENCE STANDARD ─────────────────────────────

    def certify_evidence(
        self,
        evidence_bundle: dict,
        jurisdiction:    str = "EU",
        purpose:         str = "compliance",
        agent_id:        str = "sdk-agent",
    ) -> VESCertificate:
        """
        Certify any evidence bundle to VES-1.0 standard.

        Makes evidence independently verifiable by courts,
        regulators, and auditors without trusting VeriSigil.

        Example:
            cert = vs.certify_evidence(
                evidence_bundle={
                    "evidence_id":   "EVD-001",
                    "agent_id":      "finance-agent",
                    "decision":      "APPROVED",
                    "action_type":   "wire_transfer",
                    "timestamp":     "2026-06-01T12:00:00Z",
                    "consequence_class": "CRITICAL",
                    "jurisdiction":  "EU",
                },
                jurisdiction="EU",
            )
            print(cert.ves_id)            # VES-XXXX
            print(cert.court_admissible)  # True
        """
        resp = self._request("POST", "/v1/ves/certify", {
            "evidence_bundle": evidence_bundle,
            "jurisdiction":    jurisdiction,
            "purpose":         purpose,
            "agent_id":        agent_id,
        })
        return VESCertificate.from_dict(resp)

    def ves_standard(self) -> dict:
        """Get VES-1.0 public specification. No auth required."""
        return self._request("GET", "/v1/ves/standard", public=True)

    # ── LITIGATION ────────────────────────────────────────────

    def litigation_package(
        self,
        org_name:          str,
        agent_id:          str,
        action_type:       str,
        decision:          str,
        consequence:       str  = "HIGH",
        jurisdiction:      str  = "EU",
        case_reference:    str  = "",
        evidence_bundles:  list = None,
        requesting_party:  str  = "",
        legal_counsel:     str  = "",
    ) -> LitigationPackage:
        """
        Generate a court-admissible litigation evidence dossier.

        For use when an enterprise faces legal proceedings
        arising from an AI decision.

        Returns Ed25519-sealed package with full chain of custody.
        """
        resp = self._request("POST", "/v1/litigation/package", {
            "org_name":         org_name,
            "agent_id":         agent_id,
            "action_type":      action_type,
            "decision":         decision,
            "consequence":      consequence,
            "jurisdiction":     jurisdiction,
            "case_reference":   case_reference,
            "evidence_bundles": evidence_bundles or [],
            "requesting_party": requesting_party,
            "legal_counsel":    legal_counsel,
        })
        return LitigationPackage.from_dict(resp)

    # ── AUTHORITY CONTINUITY ──────────────────────────────────

    def check_authority_continuity(
        self,
        agent_id:         str,
        initial_scope:    list = None,
        current_scope:    list = None,
        authority_chain:  list = None,
        state_transitions:list = None,
        consequence:      str  = "OPERATIONAL",
        jurisdiction:     str  = "EU",
    ) -> dict:
        """
        Check whether agent authority remains valid across state transitions.

        Answers: "Does authority granted at workflow start still hold now?"
        """
        return self._request("POST", "/v1/authority/continuity", {
            "agent_id":          agent_id,
            "initial_scope":     initial_scope or [],
            "current_scope":     current_scope or [],
            "authority_chain":   authority_chain or [],
            "state_transitions": state_transitions or [],
            "consequence":       consequence,
            "jurisdiction":      jurisdiction,
        })

    # ── HUMAN AUTHORITY CONTINUITY ────────────────────────────

    def check_human_authority(
        self,
        agent_id:              str,
        human_id:              str,
        decisions_made:        int   = 0,
        time_elapsed_minutes:  int   = 0,
        consequence:           str   = "OPERATIONAL",
    ) -> dict:
        """
        Check whether human authority remains meaningful.

        Detects: fatigue saturation, temporal decay, consequence escalation.
        Not "human in the loop" — human authority continuity.
        """
        return self._request("POST", "/v1/human/authority-continuity", {
            "agent_id":             agent_id,
            "human_id":             human_id,
            "decisions_made":       decisions_made,
            "time_elapsed_minutes": time_elapsed_minutes,
            "consequence":          consequence,
        })

    # ── TIMELOCK ──────────────────────────────────────────────

    def create_timelock(
        self,
        operation_id:   str,
        operation_type: str,
        consequence:    str  = "HIGH",
        payload:        dict = None,
        requestor_id:   str  = "",
        justification:  str  = "",
    ) -> dict:
        """
        Create a time-locked operation.

        CRITICAL operations lock for 72h.
        HIGH operations lock for 24h.
        Humans can cancel during the window.
        """
        return self._request("POST", "/v1/governance/timelock", {
            "operation_id":   operation_id,
            "operation_type": operation_type,
            "consequence":    consequence,
            "payload":        payload or {},
            "requestor_id":   requestor_id,
            "justification":  justification,
        })

    # ── HEALTH ────────────────────────────────────────────────

    def health(self) -> dict:
        """Check API health."""
        return self._request("GET", "/health", public=True)

    def health_db(self) -> dict:
        """Check persistent storage health."""
        return self._request("GET", "/health/db", public=True)

    def vcda_status(self) -> dict:
        """Check security defense status."""
        return self._request("GET", "/v1/vcda/status")
