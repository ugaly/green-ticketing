from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.db import transaction
from rest_framework.exceptions import ValidationError

from tickets.models import Comment, Ticket


@dataclass(frozen=True, slots=True)
class CloseResult:
    was_closed: bool
    reason: str | None = None


@transaction.atomic
def create_customer_ticket(*, customer_email: str, data: dict[str, Any]) -> Ticket:
    ticket = Ticket(
        source=Ticket.Source.CUSTOMER,
        customer_id=customer_email,
        title=data["title"],
        description=data.get("description", "") or "",
        priority=data.get("priority", Ticket.Priority.MEDIUM),
        category=data.get("category", Ticket.Category.GENERAL),
        status=Ticket.Status.OPEN,
    )
    ticket.full_clean()
    ticket.save()
    return ticket


@transaction.atomic
def create_external_ticket(*, data: dict[str, Any]) -> Ticket:
    ticket = Ticket(
        source=Ticket.Source.EXTERNAL,
        external_ref=data["external_ref"],
        customer_id=data.get("customer_id"),
        title=data["title"],
        description=data.get("description", "") or "",
        priority=data.get("priority", Ticket.Priority.MEDIUM),
        category=data.get("category", Ticket.Category.GENERAL),
        status=Ticket.Status.OPEN,
    )
    ticket.full_clean()
    ticket.save()
    return ticket


@transaction.atomic
def add_comment(*, ticket: Ticket, author: str, role: str, message: str) -> Comment:
    comment = Comment(ticket=ticket, author=author, role=role, message=message)
    comment.full_clean()
    comment.save()
    return comment


@transaction.atomic
def customer_close_ticket(*, ticket: Ticket) -> CloseResult:
    if ticket.status == Ticket.Status.CLOSED:
        return CloseResult(was_closed=True, reason=None)

    if ticket.status != Ticket.Status.RESOLVED:
        return CloseResult(
            was_closed=False,
            reason="Ticket can be closed by customer only when status=resolved",
        )

    ticket.status = Ticket.Status.CLOSED
    ticket.full_clean()
    ticket.save(update_fields=["status", "updated_at"])
    return CloseResult(was_closed=True, reason=None)


@transaction.atomic
def admin_update_ticket(*, ticket: Ticket, data: dict[str, Any]) -> Ticket:
    allowed = {"status", "priority", "category", "assigned_to", "title", "description"}
    unknown = set(data.keys()) - allowed
    if unknown:
        raise ValidationError({"detail": f"Unknown fields: {', '.join(sorted(unknown))}"})

    for k, v in data.items():
        setattr(ticket, k, v)

    ticket.full_clean()
    ticket.save()
    return ticket

