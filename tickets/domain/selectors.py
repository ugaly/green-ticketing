from django.db.models import Q, QuerySet
from rest_framework.exceptions import NotFound

from tickets.models import Ticket


def customer_ticket_qs(*, customer_email: str) -> QuerySet[Ticket]:
    return Ticket.objects.filter(customer_id=customer_email).order_by("-created_at")


def get_customer_ticket_or_404(*, ticket_id: int, customer_email: str) -> Ticket:
    try:
        return Ticket.objects.prefetch_related("comments").get(id=ticket_id, customer_id=customer_email)
    except Ticket.DoesNotExist as exc:
        raise NotFound("Ticket not found") from exc


def admin_ticket_qs(
    *,
    status: str | None = None,
    priority: str | None = None,
    category: str | None = None,
    assigned_to: str | None = None,
    source: str | None = None,
    q: str | None = None,
) -> QuerySet[Ticket]:
    qs = Ticket.objects.all().order_by("-created_at")
    if status:
        qs = qs.filter(status=status)
    if priority:
        qs = qs.filter(priority=priority)
    if category:
        qs = qs.filter(category=category)
    if assigned_to:
        qs = qs.filter(assigned_to=assigned_to)
    if source:
        qs = qs.filter(source=source)
    if q:
        q = q.strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(external_ref__icontains=q)
                | Q(customer_id__icontains=q)
                | Q(assigned_to__icontains=q)
            )
    return qs


def get_admin_ticket_or_404(*, ticket_id: int) -> Ticket:
    try:
        return Ticket.objects.prefetch_related("comments").get(id=ticket_id)
    except Ticket.DoesNotExist as exc:
        raise NotFound("Ticket not found") from exc

