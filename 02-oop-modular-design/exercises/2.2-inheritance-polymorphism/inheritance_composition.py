"""
Exercise: Inheritance vs. Composition

This exercise demonstrates:
1. Inheritance: Used for an 'IS-A' relationship via an Abstract Base Class (Notifier).
   - EmailNotifier IS-A Notifier
   - SmsNotifier IS-A Notifier
2. Composition: Used for a 'HAS-A' relationship (OrderService HAS-A Notifier).
   - OrderService takes a Notifier instance via dependency injection in its constructor.

--- WHY COMPOSITION OVER INHERITANCE HERE? ---
If OrderService inherited from EmailNotifier (class OrderService(EmailNotifier)):
1. Tight Coupling: OrderService would be hardcoded to email. Switching to SMS or Slack
   would require changing class inheritance or duplicating OrderService.
2. Violation of Single Responsibility: An order service should manage order processing
   lifecycle, not transport-level messaging logic.
3. Inflexibility at Runtime: With composition, we can swap or mock the notifier dynamically
   (e.g., in unit tests or when a user chooses SMS over Email) without modifying OrderService.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


# =====================================================================
# 1. INHERITANCE HIERARCHY: Abstract Base Class (ABC)
# =====================================================================
class Notifier(ABC):
    """
    Abstract Base Class defining the contract for all notification channels.
    Any concrete subclass MUST implement the `send` method.
    """

    @abstractmethod
    def send(self, recipient: str, message: str) -> bool:
        """
        Send a notification to the specified recipient.
        
        :param recipient: Target email address, phone number, etc.
        :param message: The text payload to deliver.
        :return: True if delivery succeeded, False otherwise.
        """
        pass


class EmailNotifier(Notifier):
    """Concrete implementation for sending email notifications."""

    def __init__(self, sender_email: str = "no-reply@store.com"):
        self.sender_email = sender_email

    def send(self, recipient: str, message: str) -> bool:
        # In a real system, this would integrate with SMTP / SendGrid / AWS SES.
        print(f"[EmailNotifier] From: {self.sender_email} | To: {recipient}")
        print(f"                Subject: Order Update")
        print(f"                Body: {message}")
        return True


class SmsNotifier(Notifier):
    """Concrete implementation for sending SMS notifications."""

    def __init__(self, gateway_id: str = "SMS-GW-01"):
        self.gateway_id = gateway_id

    def send(self, recipient: str, message: str) -> bool:
        # In a real system, this would call Twilio or an SMS API gateway.
        print(f"[SmsNotifier] Gateway: {self.gateway_id} | To: {recipient}")
        print(f"              SMS Text: {message}")
        return True


# =====================================================================
# 2. COMPOSITION: OrderService 'HAS-A' Notifier
# =====================================================================
class OrderService:
    """
    Handles order business logic.
    Instead of inheriting from a specific notifier, it receives any Notifier
    conforming to the Notifier interface via constructor dependency injection.
    """

    def __init__(self, notifier: Notifier):
        """
        Constructor Dependency Injection:
        Accepts any object conforming to the Notifier contract.
        """
        if not isinstance(notifier, Notifier):
            raise TypeError("notifier must be an instance of Notifier (ABC)")
        self._notifier = notifier

    def process_order(self, order_id: str, customer_contact: str, amount: float) -> Dict[str, Any]:
        """
        Executes order fulfillment steps and notifies the customer.
        """
        # Step 1: Business validation & calculation
        if amount <= 0:
            raise ValueError("Order amount must be positive.")

        print(f"\n[OrderService] Processing order #{order_id} for ${amount:.2f}...")

        # Step 2: Simulate order confirmation
        order_record = {
            "order_id": order_id,
            "amount": amount,
            "status": "CONFIRMED"
        }

        # Step 3: Trigger notification using the injected notifier
        msg = f"Your order #{order_id} of ${amount:.2f} is confirmed and being prepared!"
        self._notifier.send(recipient=customer_contact, message=msg)

        return order_record


# =====================================================================
# DEMONSTRATION & VERIFICATION
# =====================================================================
if __name__ == "__main__":
    print("=" * 60)
    print("DEMO: Composition in Action (Swapping Notifiers seamlessly)")
    print("=" * 60)

    # 1. Using EmailNotifier
    email_service = EmailNotifier(sender_email="orders@ecommerce.org")
    order_processor_email = OrderService(notifier=email_service)
    order_processor_email.process_order("ORD-101", "alice@example.com", 149.99)

    # 2. Swapping to SmsNotifier without altering OrderService code!
    sms_service = SmsNotifier(gateway_id="TWILIO-US-EAST")
    order_processor_sms = OrderService(notifier=sms_service)
    order_processor_sms.process_order("ORD-102", "+1-555-0199", 79.50)
