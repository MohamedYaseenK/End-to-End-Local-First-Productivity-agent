"""
classifier.py
Classifies an app/title into a category.
Uses YAML rules first — calls Claude API only if enabled in settings.yaml.
"""

import yaml


# ── Load Config ───────────────────────────────────────────────────────────────

with open("config/rules.yaml", "r") as f:
    RULES: dict = yaml.safe_load(f)

with open("config/settings.yaml", "r") as f:
    SETTINGS: dict = yaml.safe_load(f)

USE_AI = SETTINGS.get("classifier", {}).get("use_ai", False)


# ── Rule Engine ───────────────────────────────────────────────────────────────

def _rule_classify(app: str, title: str) -> str | None:
    """
    Check app name and window title against YAML rules.
    Returns a category string or None if no rule matches.
    """
    app_lower   = app.lower()
    title_lower = title.lower()

    for category, keywords in RULES.items():
        for keyword in keywords:
            if keyword in app_lower or keyword in title_lower:
                return category

    return None


# ── AI Classifier (optional) ──────────────────────────────────────────────────

def _ai_classify(app: str, title: str) -> str:
    """
    Asks Claude to classify the activity when rules don't match.
    Only called when use_ai is true in settings.yaml.
    """
    try:
        import anthropic
        client = anthropic.Anthropic()

        prompt = f"""
        Classify this computer activity into exactly one category.
        App: {app}
        Window title: {title}

        Categories: Work, Learning, Communication, Distraction, Idle
        Reply with the category name only. No explanation.
        """

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text.strip()

    except Exception as e:
        print(f"[classifier] AI failed: {e} — defaulting to Work")
        return "Work"


# ── Main Classify Function ────────────────────────────────────────────────────

def classify(app: str, title: str) -> str:
    """
    Returns a category for the given app and window title.
    Rule engine runs first. AI only used if enabled in settings.yaml.
    Falls back to 'Work' if nothing matches.
    """
    category = _rule_classify(app, title)

    if category:
        return category

    if USE_AI:
        return _ai_classify(app, title)

    # Default fallback when no rule matches and AI is off
    print(f"[classifier] no rule matched for {app!r} — defaulting to Work")
    return "Work"