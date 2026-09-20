"""Role-Based Access Control (RBAC) enforced at the application service layer."""

import functools
from typing import Any, Callable, Dict, List, Optional, Set
from auth_service import AuthService, SessionRecord, AuthenticationError


class AccessDeniedError(Exception):
    """Raised when an authenticated user lacks the required role or permission."""
    pass


def require_roles(auth_service: AuthService, allowed_roles: Set[str]) -> Callable:
    """Decorator enforcing that the caller possesses one of the allowed roles.

    Enforces authorization at the service layer rather than relying on UI hiding.
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(token: str, *args: Any, **kwargs: Any) -> Any:
            # Step 1: Authentication check (valid and unexpired session)
            session = auth_service.get_session(token)

            # Step 2: Authorization check (role verification)
            if session.role not in allowed_roles:
                raise AccessDeniedError(
                    f"Access denied. User '{session.username}' with role '{session.role}' "
                    f"lacks required permissions: {allowed_roles}"
                )

            # Inject session into kwargs if requested or proceed
            return func(token, *args, **kwargs)
        return wrapper
    return decorator


class ApplicationPortalService:
    """Sample application services gated by role-based authorization rules."""

    def __init__(self, auth_service: AuthService) -> None:
        self.auth = auth_service
        self._audit_logs: List[Dict[str, str]] = [
            {"event": "SYSTEM_STARTUP", "detail": "Auth services initialized."},
            {"event": "FIREWALL_RULE_UPDATED", "detail": "Inbound port 443 opened."}
        ]
        self._tickets: List[Dict[str, str]] = []

    def view_my_profile(self, token: str) -> Dict[str, Any]:
        """User or Admin: View own authenticated profile details."""
        session = self.auth.get_session(token)
        return {
            "username": session.username,
            "role": session.role,
            "session_created": session.created_at,
            "status": "active"
        }

    def submit_support_ticket(self, token: str, subject: str, message: str) -> Dict[str, str]:
        """User or Admin: Submit a support ticket."""
        session = self.auth.get_session(token)
        ticket = {
            "ticket_id": f"TCK-{len(self._tickets) + 1:04d}",
            "author": session.username,
            "subject": subject,
            "message": message
        }
        self._tickets.append(ticket)
        return ticket

    def view_system_audit_logs(self, token: str) -> List[Dict[str, str]]:
        """ADMIN ONLY: Access sensitive system audit logs."""
        session = self.auth.get_session(token)
        if session.role != "admin":
            raise AccessDeniedError(
                f"Forbidden: Role '{session.role}' is not authorized to inspect audit logs."
            )
        return list(self._audit_logs)

    def delete_system_user(self, token: str, target_username: str) -> bool:
        """ADMIN ONLY: Perform administrative user deletion."""
        session = self.auth.get_session(token)
        if session.role != "admin":
            raise AccessDeniedError(
                f"Forbidden: Role '{session.role}' cannot perform administrative user deletions."
            )
        # Record administrative audit action
        self._audit_logs.append({
            "event": "USER_DELETED",
            "detail": f"User '{target_username}' deleted by admin '{session.username}'."
        })
        return True
