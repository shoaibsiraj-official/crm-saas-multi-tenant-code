from rest_framework import serializers
from .models import Invoice, InvoiceItem


class InvoiceItemSerializer(serializers.ModelSerializer):

    class Meta:
        model = InvoiceItem
        fields = [
            "id",
            "description",
            "quantity",
            "price",
            "subtotal"
        ]
        read_only_fields = ["id", "subtotal"]


class InvoiceSerializer(serializers.ModelSerializer):

    items = InvoiceItemSerializer(many=True, required=False)

    client_name = serializers.CharField(source="client.name", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)

    class Meta:
        model = Invoice
        fields = "__all__"

        read_only_fields = [
            "id",
            "invoice_number",
            "total",
            "issued_at"
        ]

    def create(self, validated_data):

        items_data = validated_data.pop("items", [])

        invoice = Invoice.objects.create(**validated_data)

        for item in items_data:
            InvoiceItem.objects.create(
                invoice=invoice,
                **item
            )

        return invoice