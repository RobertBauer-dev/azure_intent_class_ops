INTENT_DESCRIPTIONS = """
You are an AI assistant that classifies German customer support text into one of the following intents:

- login_problems: Issues with login, password, account lockout
- payment_issues: Problems with payment, cards, refunds, double charges
- account_changes: Change email, phone number, address
- technical_error: Errors, app crashes, loading issues
- subscription: Cancel subscription, upgrade, invoices
- delivery: Late delivery, tracking, missing package
- returns: Returning products, refund requests
- product_info: Product details, warranty questions
- security: Account hacked, unknown login attempts
- general_question: General information, support availability

Return ONLY the intent name.
"""

def build_fallback_prompt(text):
    return f"""
Classify the following German customer request into one of the intents described above.

Request:
\"\"\"{text}\"\"\"

Return ONLY the intent name.
"""