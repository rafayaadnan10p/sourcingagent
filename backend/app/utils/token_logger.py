"""
Token usage logger for OpenAI API calls.

Usage:
    from app.utils.token_logger import log_tokens
    log_tokens("Agent 1", model, response.usage)
"""

# Pricing as of July 2025 — verify at https://openai.com/api/pricing/
_PRICING: dict[str, dict[str, float]] = {
    "gpt-4o": {
        "input":  2.50 / 1_000_000,   # $ per token
        "output": 10.00 / 1_000_000,
    },
    "gpt-4o-mini": {
        "input":  0.15 / 1_000_000,
        "output": 0.60 / 1_000_000,
    },
}
_DEFAULT_PRICING = _PRICING["gpt-4o"]


def log_tokens(agent_name: str, model: str, usage) -> None:
    """Print a one-line token usage summary to stdout."""
    if usage is None:
        return

    prompt_tokens     = getattr(usage, "prompt_tokens",     0)
    completion_tokens = getattr(usage, "completion_tokens", 0)
    total_tokens      = getattr(usage, "total_tokens",      0)

    # Match pricing by model prefix
    rates = _DEFAULT_PRICING
    for key, price in _PRICING.items():
        if key in model.lower():
            rates = price
            break

    cost = prompt_tokens * rates["input"] + completion_tokens * rates["output"]

    print(
        f"[tokens] {agent_name:<22} | model={model}"
        f" | in={prompt_tokens:,} out={completion_tokens:,} total={total_tokens:,}"
        f" | est. ${cost:.5f}"
    )
