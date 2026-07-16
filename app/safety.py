"""
Lightweight placeholder safety check.

This is intentionally simple (keyword-based) for Phase 1. In Phase 2 this gets
replaced/augmented by the trained Keras risk-classification model. The point of
having *some* check from day one is that every journal entry already flows
through a safety layer, so plugging in the real model later is a drop-in swap
rather than a redesign.
"""

CRISIS_KEYWORDS = [
    "kill myself", "suicide", "end my life", "want to die", "self harm",
    "hurt myself", "no reason to live",
]

CRISIS_RESOURCE_MESSAGE = (
    "It sounds like you might be going through something really heavy right now. "
    "You deserve support from someone who can help directly — please consider "
    "reaching out to a crisis line or a trusted person near you. "
    "If you're in India, iCall: 9152987821. If you're elsewhere, search "
    "'crisis helpline' + your country for a local number."
)


def check_crisis_flag(text: str) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in CRISIS_KEYWORDS)