from rest_framework import generics

from tickets.api.serializers import CategorySerializer
from tickets.models import Category


class CategoryListView(generics.ListAPIView):
    """
    GET /categories

    Public endpoint to list all available categories.
    Frontend can use this to populate dropdowns when creating tickets.
    """

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    authentication_classes = []
    permission_classes = []

