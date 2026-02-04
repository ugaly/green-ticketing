from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.api.serializers import (
    CommentCreateSerializer,
    CommentSerializer,
    TicketCreateSerializer,
    TicketDetailSerializer,
    TicketListSerializer,
)
from tickets.domain.actor import get_actor_from_request
from tickets.domain.permissions import require_role
from tickets.domain.selectors import customer_ticket_qs, get_customer_ticket_or_404
from tickets.domain.services import add_attachments, add_comment, create_customer_ticket, customer_close_ticket
from tickets.models import Comment


class CustomerTicketListCreateView(generics.ListCreateAPIView):
    """
    - POST /customer/tickets
    - GET  /customer/tickets
    """

    def get_queryset(self):
        actor = get_actor_from_request(self.request)
        require_role(actor, "customer")
        return customer_ticket_qs(customer_email=actor.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return TicketCreateSerializer
        return TicketListSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        serializer = TicketListSerializer(page or queryset, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        actor = get_actor_from_request(request)
        require_role(actor, "customer")

        serializer = TicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = create_customer_ticket(customer_email=actor.user, data=serializer.validated_data)
        # Optional file uploads (multiple) via multipart/form-data, field name: "attachments"
        files = request.FILES.getlist("attachments")
        if files:
            add_attachments(ticket=ticket, files=files, uploaded_by=actor.user)

        return Response(TicketDetailSerializer(ticket, context={"request": request}).data, status=status.HTTP_201_CREATED)


class CustomerTicketDetailView(generics.RetrieveAPIView):
    """
    GET /customer/tickets/{id}
    """

    serializer_class = TicketDetailSerializer

    def get_object(self):
        actor = get_actor_from_request(self.request)
        require_role(actor, "customer")
        return get_customer_ticket_or_404(ticket_id=int(self.kwargs["ticket_id"]), customer_email=actor.user)


class CustomerTicketCommentCreateView(APIView):
    """
    POST /customer/tickets/{id}/comments
    """

    def post(self, request, ticket_id: int):
        actor = get_actor_from_request(request)
        require_role(actor, "customer")

        ticket = get_customer_ticket_or_404(ticket_id=int(ticket_id), customer_email=actor.user)

        serializer = CommentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment: Comment = add_comment(
            ticket=ticket,
            author=actor.user,
            role="customer",
            message=serializer.validated_data["message"],
        )
        return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)


class CustomerTicketCloseView(APIView):
    """
    POST /customer/tickets/{id}/close

    Rule (Option A): customer can close only if status=resolved.
    """

    def post(self, request, ticket_id: int):
        actor = get_actor_from_request(request)
        require_role(actor, "customer")

        ticket = get_customer_ticket_or_404(ticket_id=int(ticket_id), customer_email=actor.user)
        result = customer_close_ticket(ticket=ticket)
        if not result.was_closed:
            return Response(
                {"detail": result.reason},
                status=status.HTTP_409_CONFLICT,
            )
        return Response(TicketDetailSerializer(ticket).data, status=status.HTTP_200_OK)

