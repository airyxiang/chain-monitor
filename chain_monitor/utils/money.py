from decimal import Decimal

CENTS = Decimal('.01')


def convert_float_dollar_amount_to_cents(amount: float):
    assert isinstance(amount, float)
    amount_in_cents = int((Decimal(amount) * Decimal(100)).quantize(CENTS))
    return amount_in_cents


def convert_to_float(balance: int):
    return round(balance / 1000000000000000000, 2)
