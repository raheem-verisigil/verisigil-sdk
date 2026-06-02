"""
VeriSigil — The govern() shorthand.

The simplest possible integration:

    from verisigil import govern
    
    govern("finance-agent", "wire_transfer", consequence="CRITICAL")

No client instantiation needed for quick scripts.
Uses VERISIGIL_API_KEY environment variable.
"""

import os
from typing import Optional
from .client import VeriSigil
from .models import GovernanceResult

_default_client: Optional[VeriSigil] = None


def _get_client() -> VeriSigil:
    global _default_client
    if _default_client is None:
        api_key = os.environ.get("VERISIGIL_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "VERISIGIL_API_KEY environment variable not set. "
                "Set it or use VeriSigil(api_key='your-key') directly."
            )
        _default_client = VeriSigil(api_key=api_key)
    return _default_client


def govern(
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
    api_key:         str   = None,
) -> GovernanceResult:
    """
    Govern any AI action. The simplest VeriSigil integration.

    Set VERISIGIL_API_KEY env var, then:

        from verisigil import govern

        result = govern("my-agent", "send_email", consequence="LOW")
        if result:
            send_email()

    Or pass api_key directly:

        result = govern("my-agent", "wire_transfer", consequence="CRITICAL",
                        api_key="your-key", raise_on_inadmissible=True)
    """
    global _default_client

    if api_key:
        client = VeriSigil(api_key=api_key)
    else:
        client = _get_client()

    return client.govern(
        agent=agent,
        action=action,
        consequence=consequence,
        authority_scope=authority_scope,
        tools_invoked=tools_invoked,
        external_systems=external_systems,
        irreversible=irreversible,
        human_present=human_present,
        trust_score=trust_score,
        workflow_step=workflow_step,
        jurisdiction=jurisdiction,
        raise_on_inadmissible=raise_on_inadmissible,
    )
