from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Order(models.Model):

    # =========================
    # ORDER STATUS FLOW
    # =========================
    ORDER_STATUS = (
        ("Placed", "Placed"),          # Order received
        ("Confirmed", "Confirmed"),    # COD / Payment confirmed
        ("Packed", "Packed"),          # Packed in warehouse
        ("Shipped", "Shipped"),        # Given to courier
        ("Delivered", "Delivered"),    # Delivered to customer
        ("Cancelled", "Cancelled"),    # Cancelled
    )

    # =========================
    # USER (OPTIONAL)
    # =========================
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    # =========================
    # CUSTOMER DETAILS
    # =========================
    name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    mobile = models.CharField(max_length=15, default="")
    address = models.TextField(default="")

    # =========================
    # CART ITEMS (JSON)
    # =========================
    items = models.JSONField(default=list)   # 🛒 cart items

    # =========================
    # BILL BREAKUP
    # =========================
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

    # =========================
    # PAYMENT & STATUS
    # =========================
    payment_method = models.CharField(
        max_length=30,
        default="COD"   # COD / ONLINE / UPI
    )

    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS,
        default="Placed"
    )

    # =========================
    # TIMESTAMP
    # =========================
    created_at = models.DateTimeField(auto_now_add=True)

    # =========================
    # STRING REPRESENTATION
    # =========================
    def __str__(self):
        return f"Order #{self.id} - {self.name} ({self.status})"
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username
class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} - {self.pincode}"
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to="products/")
class SupportTicket(models.Model):
    TICKET_TYPE = [
        ("Query","Query"),
        ("Complaint","Complaint"),
        ("Service","Service"),
        ("Payment","Payment"),
    ]

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE)
    message = models.TextField()
    status = models.CharField(max_length=20, default="Pending")
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.name}"

class SupportTicket(models.Model):
    TICKET_TYPE = [
        ('General', 'General Query'),
        ('Order', 'Order Related'),
        ('Payment', 'Payment Issue'),
        ('Return', 'Return / Refund'),
        ('Technical', 'Technical Problem'),
    ]

    ticket_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    issue_type = models.CharField(max_length=50, choices=TICKET_TYPE)
    message = models.TextField()
    photo = models.ImageField(upload_to="support/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
