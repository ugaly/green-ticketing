from django.conf import settings
from rest_framework.test import APITestCase

from tickets.models import Ticket


class TicketApiTests(APITestCase):
    def test_customer_sees_only_own_tickets(self):
        # Create two tickets for different customers
        r1 = self.client.post(
            "/customer/tickets",
            data={"title": "My ticket", "description": "hello"},
            format="json",
            HTTP_X_ROLE="customer",
            HTTP_X_USER="alice@example.com",
        )
        self.assertEqual(r1.status_code, 201)

        r2 = self.client.post(
            "/customer/tickets",
            data={"title": "Other ticket"},
            format="json",
            HTTP_X_ROLE="customer",
            HTTP_X_USER="bob@example.com",
        )
        self.assertEqual(r2.status_code, 201)

        # Alice lists -> only 1
        r = self.client.get(
            "/customer/tickets",
            HTTP_X_ROLE="customer",
            HTTP_X_USER="alice@example.com",
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data["results"]), 1)
        self.assertEqual(r.data["results"][0]["title"], "My ticket")

        # Alice cannot access Bob's ticket
        bob_ticket_id = r2.data["id"]
        r = self.client.get(
            f"/customer/tickets/{bob_ticket_id}",
            HTTP_X_ROLE="customer",
            HTTP_X_USER="alice@example.com",
        )
        self.assertEqual(r.status_code, 404)

    def test_external_ingest_requires_api_key(self):
        r = self.client.post(
            "/external/tickets",
            data={"external_ref": "EXT-1", "title": "From external"},
            format="json",
        )
        self.assertEqual(r.status_code, 403)

        r = self.client.post(
            "/external/tickets",
            data={"external_ref": "EXT-1", "title": "From external"},
            format="json",
            HTTP_X_API_KEY=settings.EXTERNAL_TICKET_API_KEY,
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["external_ref"], "EXT-1")

        ticket = Ticket.objects.get(id=r.data["ticket_id"])
        self.assertEqual(ticket.source, Ticket.Source.EXTERNAL)

