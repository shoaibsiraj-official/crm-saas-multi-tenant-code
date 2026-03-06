import uuid
from django.db import models
from clients.models import Client
from projects.models import Project


class Invoice(models.Model):

    STATUS_CHOICES = [
        ("DRAFT", "Draft"),
        ("SENT", "Sent"),
        ("PAID", "Paid"),
        ("OVERDUE", "Overdue"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="invoices"
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invoices"
    )

    invoice_number = models.CharField(max_length=50, unique=True)

    tax = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    total = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="DRAFT"
    )

    due_date = models.DateField()

    issued_at = models.DateTimeField(auto_now_add=True)

    # ======================
    # Generate Invoice Number
    # ======================
    @staticmethod
    def generate_invoice_number():

        last_invoice = Invoice.objects.order_by("-issued_at").first()

        if not last_invoice:
            return "INV-0001"

        try:
            last_number = int(last_invoice.invoice_number.split("-")[1])
        except:
            return "INV-0001"

        new_number = last_number + 1

        return f"INV-{new_number:04d}"

    def save(self, *args, **kwargs):

        if not self.invoice_number:
            self.invoice_number = Invoice.generate_invoice_number()

        super().save(*args, **kwargs)

        # calculate total from items
        total_items = sum(item.subtotal for item in self.items.all())

        self.total = total_items + self.tax

        super().save(update_fields=["total"])

    def __str__(self):
        return f"{self.invoice_number} - {self.client.name}"


class InvoiceItem(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="items"
    )

    description = models.CharField(max_length=255)

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):

        self.subtotal = self.quantity * self.price

        super().save(*args, **kwargs)

    def __str__(self):
        return self.description