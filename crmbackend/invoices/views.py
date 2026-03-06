from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from django.http import FileResponse

from .models import Invoice
from .serializers import InvoiceSerializer
from .utils import generate_invoice_pdf


class InvoiceViewSet(ModelViewSet):

    serializer_class = InvoiceSerializer
    queryset = Invoice.objects.all().order_by("-issued_at")

    @action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):

        invoice = self.get_object()

        pdf_buffer = generate_invoice_pdf(invoice)

        return FileResponse(
            pdf_buffer,
            as_attachment=True,
            filename=f"Invoice-{invoice.invoice_number}.pdf"
        )