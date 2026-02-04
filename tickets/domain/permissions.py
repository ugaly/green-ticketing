from rest_framework.exceptions import PermissionDenied

from .actor import Actor


def require_role(actor: Actor, required_role: str) -> None:
    if actor.role != required_role:
        raise PermissionDenied(f"Requires role={required_role}")

