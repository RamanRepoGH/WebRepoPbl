SUPPORTED_CURRENCIES = {"USD", "EUR", "GBP"}
VALID_PRODUCTS = {"Product A", "Product B"}


def validate_purchase_business(event):
    errors = []

    if event.amount <= 0:
        errors.append("Amount must be positive")

    if event.currency not in SUPPORTED_CURRENCIES:
        errors.append("Unsupported currency")

    if event.product_id and event.product_id not in VALID_PRODUCTS:
        errors.append("Unknown product_id")

    return errors
