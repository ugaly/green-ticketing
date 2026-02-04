from django.urls import path

from tickets.api.admin_views import (
    AdminTicketCommentCreateView,
    AdminTicketListView,
    AdminTicketRetrieveUpdateView,
    AdminTicketStatsView,
)
from tickets.api.customer_views import (
    CustomerTicketCloseView,
    CustomerTicketCommentCreateView,
    CustomerTicketDetailView,
    CustomerTicketListCreateView,
)
from tickets.api.external_views import ExternalTicketIngestView


urlpatterns = [
    # Customer
    path("customer/tickets", CustomerTicketListCreateView.as_view(), name="customer-ticket-list-create"),
    path("customer/tickets/<int:ticket_id>", CustomerTicketDetailView.as_view(), name="customer-ticket-detail"),
    path(
        "customer/tickets/<int:ticket_id>/comments",
        CustomerTicketCommentCreateView.as_view(),
        name="customer-ticket-comment-create",
    ),
    path("customer/tickets/<int:ticket_id>/close", CustomerTicketCloseView.as_view(), name="customer-ticket-close"),
    # Admin
    path("admin/tickets", AdminTicketListView.as_view(), name="admin-ticket-list"),
    path("admin/tickets/stats", AdminTicketStatsView.as_view(), name="admin-ticket-stats"),
    path(
        "admin/tickets/<int:ticket_id>",
        AdminTicketRetrieveUpdateView.as_view(),
        name="admin-ticket-retrieve-update",
    ),
    path(
        "admin/tickets/<int:ticket_id>/comments",
        AdminTicketCommentCreateView.as_view(),
        name="admin-ticket-comment-create",
    ),
    # External
    path("external/tickets", ExternalTicketIngestView.as_view(), name="external-ticket-ingest"),
]

