from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Order(models.Model):

    ORDER_STATUS = (
        ("Placed", "Placed"),
        ("Confirmed", "Confirmed"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    mobile = models.CharField(max_length=15, default="")
    address = models.TextField(default="")

    items = models.JSONField(default=list)   # 🛒 cart items

    # ✅ BILL BREAKUP (NEW)
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    gst = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    flat_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    extra_discount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    payment_method = models.CharField(
        max_length=30,
        default="COD"   # COD / ONLINE / UPI
    )

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default="Placed"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.name}"
