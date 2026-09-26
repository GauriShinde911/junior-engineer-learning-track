"""
logged_app.py - Payment and Order Service (Observable Version)

This application adds production-grade logging using Python's standard `logging` library.
Features:
- Structured contextual logging (operation, user_id, order_id, amount).
- Proper log levels: DEBUG, INFO, WARNING, ERROR.
- Exception logging via `logger.exception()` to capture full stack traces.
- Secret sanitization: Passwords, tokens, and CVVs are strictly excluded; card PAN is masked.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("payment_service")


class PaymentGatewayError(Exception):
    pass


class LoggedPaymentService:
    def __init__(self):
        self.accounts = {
            "usr_100": {"balance": 250.00, "active": True},
            "usr_200": {"balance": 15.00, "active": True},
        }

    @staticmethod
    def _mask_card_number(pan: str) -> str:
        """Returns masked PAN showing only the last 4 digits."""
        clean_pan = pan.replace("-", "").replace(" ", "")
        if len(clean_pan) < 4:
            return "****"
        return f"****-****-****-{clean_pan[-4:]}"

    def authenticate_user(self, username: str, password: str, api_token: str) -> bool:
        """
        Authenticates a user.
        CRITICAL: Never logs password or api_token; only logs username and outcome.
        """
        logger.debug("Authenticating user credentials: username=%s", username)
        
        is_valid = (
            username == "alice"
            and password == "SuperSecretPassword!123"
            and api_token == "tok_live_99887766"
        )
        
        if is_valid:
            logger.info("User authentication succeeded: username=%s", username)
            return True
        else:
            logger.warning("User authentication failed: username=%s [reason=invalid_credentials]", username)
            return False

    def process_payment(
        self,
        order_id: str,
        user_id: str,
        amount: float,
        card_details: Dict[str, str],
        idempotency_key: str
    ) -> Dict[str, Any]:
        """
        Processes a customer payment with structured diagnostic logs.
        """
        raw_pan = card_details.get("card_number", "")
        masked_card = self._mask_card_number(raw_pan)

        # DEBUG: Diagnostic payload details with secrets sanitized
        logger.debug(
            "Processing payment transaction: order_id=%s user_id=%s amount=%.2f card=%s idempotency_key=%s",
            order_id,
            user_id,
            amount,
            masked_card,
            idempotency_key,
        )

        if user_id not in self.accounts:
            logger.error("Payment aborted: unknown account user_id=%s order_id=%s", user_id, order_id)
            raise ValueError(f"Unknown user {user_id}")

        account = self.accounts[user_id]

        # WARNING: Proactive alert for operational anomalies
        if account["balance"] < 50.0:
            logger.warning(
                "Low account balance detected: user_id=%s current_balance=%.2f threshold=50.00",
                user_id,
                account["balance"],
            )

        if account["balance"] < amount:
            try:
                raise PaymentGatewayError(
                    f"Insufficient funds: available {account['balance']:.2f}, required {amount:.2f}"
                )
            except PaymentGatewayError:
                # ERROR: Captures traceback and context without leaking raw card data
                logger.exception(
                    "Payment processing failed: order_id=%s user_id=%s amount=%.2f card=%s",
                    order_id,
                    user_id,
                    amount,
                    masked_card,
                )
                raise

        account["balance"] -= amount

        # INFO: Key business milestone
        logger.info(
            "Payment successful: order_id=%s user_id=%s charged_amount=%.2f remaining_balance=%.2f card=%s",
            order_id,
            user_id,
            amount,
            account["balance"],
            masked_card,
        )

        return {
            "status": "success",
            "order_id": order_id,
            "user_id": user_id,
            "charged_amount": amount,
            "remaining_balance": account["balance"],
            "card_masked": masked_card,
        }


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
    )

    service = LoggedPaymentService()
    service.authenticate_user("alice", "SuperSecretPassword!123", "tok_live_99887766")
    service.process_payment(
        order_id="ORD-101",
        user_id="usr_100",
        amount=45.00,
        card_details={"card_number": "4111222233334444", "cvv": "987", "expiry": "12/28"},
        idempotency_key="idem_987xyz"
    )
    try:
        service.process_payment(
            order_id="ORD-102",
            user_id="usr_200",
            amount=100.00,
            card_details={"card_number": "5555666677778888", "cvv": "123", "expiry": "01/30"},
            idempotency_key="idem_failed456"
        )
    except PaymentGatewayError:
        pass
