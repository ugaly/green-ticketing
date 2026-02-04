from django.conf import settings
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from tickets.api.serializers import ExternalTicketIngestSerializer
from tickets.domain.services import add_attachments, create_external_ticket


class ExternalTicketIngestView(APIView):
    """
    POST /external/tickets
    Header: X-API-KEY: <secret>
    """

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        api_key = (request.headers.get("X-API-KEY") or "").strip()
        if not api_key or api_key != getattr(settings, "EXTERNAL_TICKET_API_KEY", ""):
            raise PermissionDenied("Invalid or missing X-API-KEY")

        serializer = ExternalTicketIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ticket = create_external_ticket(data=serializer.validated_data)

        # Optional file uploads (multiple) via multipart/form-data, field name: "attachments"
        files = request.FILES.getlist("attachments")
        if files:
            add_attachments(ticket=ticket, files=files)

        # Build absolute URLs for attachments in response
        attachments = []
        for attachment in ticket.attachments.all():
            url = attachment.file.url
            if request is not None:
                url = request.build_absolute_uri(url)
            attachments.append(url)

        return Response(
            {
                "ticket_id": ticket.id,
                "external_ref": ticket.external_ref,
                "status": ticket.status,
                "attachments": attachments,
            },
            status=status.HTTP_201_CREATED,
        )

