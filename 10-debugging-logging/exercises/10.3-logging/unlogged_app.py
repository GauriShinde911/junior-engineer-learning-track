"""
unlogged_app.py - Payment and Order Service (Unobservable Version)

This application performs user authentication, balance checks, and payment processing
without using the Python logging framework. Operations execute silently or use raw
print statements, providing zero visibility into system state, error context, or performance.
"""

from typing import Dict, Any, Optional


class PaymentGatewayError(Exception):
    pass


class UnloggedPaymentService:
    def __init__(self):
        self.accounts = {
            "usr_100": {"balance": 250.00, "active": True},
            "usr_200": {"balance": 15.00, "active": True},
        }

    def authenticate_user(self, username: str, password: str, api_token: str) -> bool:
        # Authentication check without auditing or visibility
        if username == "alice" and password == "SuperSecretPassword!123" and api_token == "tok_live_99887766":
            return True
        return False

    def process_payment(
        self,
        order_id: str,
        user_id: str,
        amount: float,
        card_details: Dict[str, str],
        idempotency_key: str
    ) -> Dict[str, Any]:
        # No debug visibility into payload
        if user_id not in self.accounts:
            raise ValueError(f"Unknown user {user_id}")

        account = self.accounts[user_id]
        
        # Low balance check without warnings
        if account["balance"] < 50.0:
            pass  # Silent; operator has no idea user is near zero

        if account["balance"] < amount:
            try:
                raise PaymentGatewayError("Insufficient funds in account")
            except PaymentGatewayError:
                # Raw print or silent suppression loses traceback and structured context
                print("Payment failed for user")
                raise

        account["balance"] -= amount
        
        # Payment succeeded silently without audit log
        return {
            "status": "success",
            "order_id": order_id,
            "user_id": user_id,
            "charged_amount": amount,
            "remaining_balance": account["balance"],
        }


if __name__ == "__main__":
    service = UnloggedPaymentService()
    auth = service.authenticate_user("alice", "SuperSecretPassword!123", "tok_live_99887766")
    print(f"Auth result: {auth}")
    result = service.process_payment(
        order_id="ORD-001",
        user_id="usr_100",
        amount=45.00,
        card_details={"card_number": "4111222233334444", "cvv": "987", "expiry": "12/28"},
        idempotency_key="idem_abc123"
    )
    print("Payment completed:", result)
