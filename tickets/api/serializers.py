from rest_framework import serializers

from tickets.models import Category, Comment, Ticket, TicketAttachment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "ticket_id", "author", "role", "message", "created_at")
        read_only_fields = fields


class CommentCreateSerializer(serializers.Serializer):
    message = serializers.CharField(allow_blank=False, trim_whitespace=True)


class TicketListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = (
            "id",
            "source",
            "external_ref",
            "title",
            "description",
            "priority",
            "status",
            "category",
            "customer_id",
            "assigned_to",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class TicketCreateSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200, allow_blank=False, trim_whitespace=True)
    description = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(choices=Ticket.Priority.choices, required=False)
    category = serializers.CharField(required=False, max_length=50)


class TicketAdminUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Ticket.Status.choices, required=False)
    priority = serializers.ChoiceField(choices=Ticket.Priority.choices, required=False)
    category = serializers.CharField(required=False, max_length=50)
    assigned_to = serializers.EmailField(required=False, allow_null=True)
    title = serializers.CharField(required=False, max_length=200, allow_blank=False, trim_whitespace=True)
    description = serializers.CharField(required=False, allow_blank=True)


class ExternalTicketIngestSerializer(serializers.Serializer):
    external_ref = serializers.CharField(max_length=120, allow_blank=False, trim_whitespace=True)
    title = serializers.CharField(max_length=200, allow_blank=False, trim_whitespace=True)
    description = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(choices=Ticket.Priority.choices, required=False)
    category = serializers.CharField(required=False, max_length=50)
    customer_id = serializers.EmailField(required=False, allow_null=True)


class TicketAttachmentSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = TicketAttachment
        fields = ("id", "url", "created_at")
        read_only_fields = fields

    def get_url(self, obj) -> str:
        request = self.context.get("request")
        url = obj.file.url
        if request is not None:
            return request.build_absolute_uri(url)
        return url


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = fields

class TicketDetailSerializer(TicketListSerializer):
    comments = CommentSerializer(many=True, read_only=True)
    attachments = TicketAttachmentSerializer(many=True, read_only=True)

    class Meta(TicketListSerializer.Meta):
        fields = TicketListSerializer.Meta.fields + ("comments", "attachments")
