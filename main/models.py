from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


# =========================
# ORDERS
# =========================
class Order(models.Model):

    ORDER_STATUS = (
        ("Placed", "Placed"),
        ("Confirmed", "Confirmed"),
        ("Packed", "Packed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=100, default="")
    email = models.EmailField(default="")
    mobile = models.CharField(max_length=15, default="")
    address = models.TextField(default="")

    items = models.JSONField(default=list)

    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    flat_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    extra_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_method = models.CharField(max_length=30, default="COD")
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default="Placed")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id} - {self.name} ({self.status})"


# =========================
# USER PROFILE
# =========================
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.user.username


# =========================
# USER ADDRESS
# =========================
class UserAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    address = models.TextField()
    pincode = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} - {self.pincode}"


# =========================
# PRODUCTS
# =========================
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to="products/")

    def __str__(self):
        return self.name


# =========================
# SUPPORT TICKETS
# =========================
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
    status = models.CharField(max_length=20, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_id
