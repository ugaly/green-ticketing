from django.contrib import admin

from .models import Category, Comment, Ticket, TicketAttachment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


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


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "file", "created_at")
    list_filter = ("created_at",)
    search_fields = ("file",)
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

