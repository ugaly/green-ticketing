from django.contrib import admin

from .models import Comment, Ticket


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "source",
        "status",
        "priority",
        "category",
        "customer_id",
        "assigned_to",
        "created_at",
        "updated_at",
    )
    list_filter = ("source", "status", "priority", "category", "assigned_to", "created_at")
    search_fields = ("title", "description", "external_ref", "customer_id", "assigned_to")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "role", "author", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("author", "message")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

