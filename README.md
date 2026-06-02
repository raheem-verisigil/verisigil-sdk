# VeriSigil AI Python SDK

**Operational Admissibility Infrastructure for Autonomous Enterprise AI**

The Python SDK for [VeriSigil AI](https://verisigilai.com) — the runtime infrastructure layer that determines whether consequential AI actions may become operationally real.

## Installation

```bash
pip install verisigil
```

Zero dependencies. Pure Python stdlib.

## Quick Start

```python
from verisigil import VeriSigil

vs = VeriSigil(api_key="your-api-key")

# Govern any AI action before execution
result = vs.govern(
    agent="finance-agent",
    action="wire_transfer",
    consequence="CRITICAL",
    irreversible=True,
    human_present=True,
)

if result:
    execute_transfer()
else:
    escalate_to_human(result.ruling, result.signature)
```

One-line shorthand with environment variable:

```bash
export VERISIGIL_API_KEY="your-api-key"
```

```python
from verisigil import govern

result = govern("finance-agent", "wire_transfer", consequence="CRITICAL")
if result:
    proceed()
```

## Core Capabilities

### Runtime Admissibility
```python
result = vs.govern(
    agent="my-agent",
    action="database_write",
    consequence="HIGH",
    tools_invoked=["sql_executor"],
    external_systems=["production-db"],
    irreversible=True,
)
# result.admissible → True/False
# result.ruling     → ADMISSIBLE / CONDITIONALLY_ADMISSIBLE / INADMISSIBLE
# result.signature  → Ed25519 governance signature (offline verifiable)
```

### Document Integrity (4-Layer Detection)
```python
doc = vs.verify_document(
    original_text="Payment within 30 days. No sub-delegation without board approval.",
    generated_text="Payment within 300 days. Sub-delegation allowed.",
    consequence="CRITICAL",
)
# doc.corruption_detected → True
# doc.corruption_score    → 0.59
# doc.decision            → "QUARANTINE"
# doc.signature           → Ed25519 sealed evidence
```

### EU AI Act Compliance
```python
result = vs.eu_ai_act_assess(
    use_case="AI loan approval for EU retail customers",
    org_name="Acme Bank",
    sector="finance",
    annual_revenue_eur=500_000_000,
)
# result.compliance_score → 40.0
# result.risk_category    → "HIGH"
# result.fine_exposure    → 15000000.0
# result.days_remaining   → 62
for gap in result.critical_gaps:
    print(f"CRITICAL: {gap['article']} — {gap['vgs_fix']}")
```

### VES-1.0 Evidence Certification
```python
cert = vs.certify_evidence(
    evidence_bundle={
        "evidence_id":       "EVD-001",
        "agent_id":          "finance-agent",
        "decision":          "APPROVED",
        "action_type":       "wire_transfer",
        "timestamp":         "2026-06-01T12:00:00Z",
        "consequence_class": "CRITICAL",
        "jurisdiction":      "EU",
    },
    jurisdiction="EU",
)
# cert.ves_id           → "VES-XXXX"
# cert.court_admissible → True
# cert.canonical_hash   → "sha256:..."
```

### Litigation Evidence Package
```python
package = vs.litigation_package(
    org_name="Acme Bank",
    agent_id="finance-agent",
    action_type="loan_decision",
    decision="REJECTED",
    consequence="HIGH",
    jurisdiction="EU",
)
# package.court_admissible  → True
# package.package_signature → Ed25519 sealed
# package.chain_of_custody  → Full audit trail
```

## LangChain Integration

```python
from langchain.agents import AgentExecutor
from verisigil import VeriSigil

vs = VeriSigil(api_key="your-key")

class GovernedAgentExecutor(AgentExecutor):
    def invoke(self, input, **kwargs):
        result = vs.govern(
            agent=self.agent.name,
            action="agent_execution",
            consequence="OPERATIONAL",
        )
        if not result:
            raise RuntimeError(f"Agent execution blocked: {result.ruling}")
        return super().invoke(input, **kwargs)
```

## API Reference

Full API documentation: [https://verisigil-api-production.up.railway.app/docs](https://verisigil-api-production.up.railway.app/docs)

| Method | Description |
|--------|-------------|
| `vs.govern()` | Runtime admissibility check — core primitive |
| `vs.verify_document()` | 4-layer document integrity detection |
| `vs.eu_ai_act_assess()` | EU AI Act compliance assessment |
| `vs.certify_evidence()` | VES-1.0 evidence certification |
| `vs.litigation_package()` | Court-admissible evidence dossier |
| `vs.check_authority_continuity()` | Authority validity across state transitions |
| `vs.check_human_authority()` | Human authority continuity check |
| `vs.create_timelock()` | Time-lock high-risk operations |
| `vs.health_db()` | Persistent storage health |
| `vs.vcda_status()` | Security defense status |

## Pricing

[https://verisigilai.com/pricing.html](https://verisigilai.com/pricing.html)

- **Free**: EU AI Act scanner, public VES standard
- **Pro ($499/month)**: Full API access, 10,000 governance checks/month
- **Enterprise**: Dedicated deployment, SLA, custom integration

## License

MIT — VeriSigil AI · [info@verisigilai.com](mailto:info@verisigilai.com)
