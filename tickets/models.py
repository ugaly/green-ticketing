from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Ticket(models.Model):
    class Source(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        EXTERNAL = "external", "External"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In progress"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    source = models.CharField(max_length=20, choices=Source.choices)
    external_ref = models.CharField(max_length=120, blank=True, null=True)

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    category = models.CharField(
        max_length=50,
        default="general",
    )

    customer_id = models.EmailField(blank=True, null=True)
    assigned_to = models.EmailField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "priority"]),
            models.Index(fields=["category"]),
            models.Index(fields=["assigned_to"]),
            models.Index(fields=["source"]),
            models.Index(fields=["customer_id"]),
            models.Index(fields=["created_at"]),
        ]

    def clean(self):
        # Keep validation close to the model for consistency across API/admin.
        from django.core.exceptions import ValidationError

        if self.source == self.Source.EXTERNAL and not self.external_ref:
            raise ValidationError({"external_ref": "external_ref is required when source=external"})

    def __str__(self) -> str:
        return f"#{self.pk} [{self.status}] {self.title}"


class Comment(models.Model):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        ADMIN = "admin", "Admin"

    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=Role.choices)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
            models.Index(fields=["role"]),
        ]

    def __str__(self) -> str:
        return f"Comment #{self.pk} on Ticket #{self.ticket_id}"


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="attachments/%Y/%m/%d/")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["ticket", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Attachment #{self.pk} on Ticket #{self.ticket_id}"


