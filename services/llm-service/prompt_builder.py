"""
Prompt Builder — constructs the Gemini system prompt from an
LLMOptimizationRequest payload, exactly matching the PRD template.
"""
from rule_engine import LLMOptimizationRequest

# Using double-braces {{ }} to escape literal JSON braces from Python
# .format(), so {payload} is the only substitution point.
SYSTEM_PROMPT_TEMPLATE = """\
You are an autonomous supply chain routing agent for a global logistics platform.
Your job is to evaluate shipment disruption data and select the optimal fallback route.

RULES:
1. For HIGH priority cargo: minimize delay above all else, cost is secondary.
2. For STANDARD priority cargo: balance delay and cost equally.
3. For LOW priority cargo: minimize cost. Delay is acceptable.
4. If severity >= 9 OR threat_type == WEATHER with delay > 72hrs: set requires_human = true.
5. If no route meaningfully reduces delay, recommend "WAIT" and set requires_human = true.
6. You MUST return only valid JSON. No markdown. No explanation outside JSON.

INPUT PAYLOAD: {payload}

Return ONLY this JSON structure:
{{
  "selected_route_id": "<route_id from fallback_routes>",
  "action": "REROUTE | WAIT | ESCALATE",
  "reasoning": "<2-3 sentence explanation>",
  "requires_human": true | false,
  "new_eta_offset_hours": <float — hours saved vs original delay>
}}"""


def build_prompt(request_data: LLMOptimizationRequest) -> str:
    """Build a prompt without leaking sensitive request data."""
    
    # Extract only necessary optimization data
    routes_summary = "\n".join([
        f"- Route {r.route_id}: delay={r.delay_hours}h, cost=${r.cost}, carrier={r.carrier}"
        for r in request_data.fallback_routes
    ])
    
    disruption_summary = f"""
Priority: {request_data.priority}
Severity: {request_data.disruption_details.severity}
Threat: {request_data.disruption_details.threat_type}
Delay: {request_data.disruption_details.estimated_delay_hours}h
"""
    
    return SYSTEM_PROMPT_TEMPLATE.format(
        payload=f"{disruption_summary}\nAvailable Routes:\n{routes_summary}"
    )
