from django.db.models import Count
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.api.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    TicketAdminUpdateSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
)
from tickets.domain.actor import get_actor_from_request
from tickets.domain.permissions import require_role
from tickets.domain.selectors import admin_ticket_qs, get_admin_ticket_or_404
from tickets.domain.services import add_comment, admin_update_ticket
from tickets.models import Comment, Ticket


class AdminTicketListView(generics.ListAPIView):
    """
    GET /admin/tickets
    Filters:
      - status, priority, category, assigned_to, source, q
    """

    serializer_class = TicketListSerializer

    def get_queryset(self):
        actor = get_actor_from_request(self.request)
        require_role(actor, "admin")

        params = self.request.query_params
        return admin_ticket_qs(
            status=params.get("status"),
            priority=params.get("priority"),
            category=params.get("category"),
            assigned_to=params.get("assigned_to"),
            source=params.get("source"),
            q=params.get("q"),
        )


class AdminTicketRetrieveUpdateView(APIView):
    """
    GET /admin/tickets/{id}
    PUT /admin/tickets/{id}

    Update fields:
      - status, priority, category, assigned_to, title, description
    """

    def get(self, request, ticket_id: int):
        actor = get_actor_from_request(request)
        require_role(actor, "admin")

        ticket = get_admin_ticket_or_404(ticket_id=int(ticket_id))
        return Response(TicketDetailSerializer(ticket).data, status=status.HTTP_200_OK)

    def put(self, request, ticket_id: int):
        actor = get_actor_from_request(request)
        require_role(actor, "admin")

        ticket = get_admin_ticket_or_404(ticket_id=int(ticket_id))
        serializer = TicketAdminUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = admin_update_ticket(ticket=ticket, data=serializer.validated_data)
        return Response(TicketDetailSerializer(ticket).data, status=status.HTTP_200_OK)


class AdminTicketCommentCreateView(APIView):
    """
    POST /admin/tickets/{id}/comments
    """

    def post(self, request, ticket_id: int):
        actor = get_actor_from_request(request)
        require_role(actor, "admin")

        ticket = get_admin_ticket_or_404(ticket_id=int(ticket_id))
        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment: Comment = add_comment(
            ticket=ticket,
            author=actor.user,
            role="admin",
            message=serializer.validated_data["message"],
        )
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class AdminTicketStatsView(APIView):
    """
    GET /admin/tickets/stats
    """

    def get(self, request):
        actor = get_actor_from_request(request)
        require_role(actor, "admin")

        by_status = {
            row["status"]: row["c"]
            for row in Ticket.objects.values("status").annotate(c=Count("id")).order_by()
        }
        by_priority = {
            row["priority"]: row["c"]
            for row in Ticket.objects.values("priority").annotate(c=Count("id")).order_by()
        }
        by_source = {
            row["source"]: row["c"]
            for row in Ticket.objects.values("source").annotate(c=Count("id")).order_by()
        }
        return Response(
            {
                "by_status": by_status,
                "by_priority": by_priority,
                "by_source": by_source,
            }
        )

