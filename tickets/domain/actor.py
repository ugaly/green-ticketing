from dataclasses import dataclass
from typing import Literal

from rest_framework.exceptions import ValidationError


Role = Literal["customer", "admin"]


@dataclass(frozen=True, slots=True)
class Actor:
    role: Role
    user: str  # email-ish identifier


def get_actor_from_request(request) -> Actor:
    """
    Role simulation for interview time-box:

    Prefer headers:
      - X-ROLE: customer|admin
      - X-USER: email

    Or query params:
      - role=customer|admin
      - user=email
    """
    role = (request.headers.get("X-ROLE") or request.query_params.get("role") or "").strip().lower()
    user = (request.headers.get("X-USER") or request.query_params.get("user") or "").strip()

    if role not in {"customer", "admin"}:
        raise ValidationError({"role": "Missing/invalid role. Use X-ROLE: customer|admin (or ?role=...)"})
    if not user:
        raise ValidationError({"user": "Missing user. Use X-USER: email (or ?user=...)"})

    return Actor(role=role, user=user)

