# =========================
# IMPORTS
# =========================

import json, base64, os, uuid, qrcode
from io import BytesIO
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt   # 🔥 MUST
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import User

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import (
    Product, Order, OrderItem, SupportTicket,
    UserProfile, PaymentProof
)

from .utils import (
    send_support_ticket_email,
    send_brevo_email,
    send_invoice_mail,
    send_sms_otp,
    send_whatsapp_otp
)

import razorpay

# Razorpay Client
client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# =========================
# BASIC PAGES
# =========================
def index(request): return render(request, "index.html")
def about(request): return render(request, "about.html")
def product_details(request): return render(request, "product_details.html")
def cart(request): return render(request, "cart.html")
def contact(request): return render(request, "contact.html")

def computer_sales(request): return render(request, "computer_sales.html")
def repair_maintenance(request): return render(request, "repair_maintenance.html")
def printer_toner(request): return render(request, "printer_toner.html")
def cctv_fitting(request): return render(request, "cctv_fitting.html")
def lokmitra_services(request): return render(request, "lokmitra_services.html")
def hp_retailer(request): return render(request, "hp-retailer.html")
def website_policy(request): return render(request, "website_policy.html")
def return_policy(request): return render(request, "return_policy.html")
def return_request(request): return render(request, "return_request.html")


# =========================
# PRODUCTS PAGE
# =========================
def products(request):
    q = request.GET.get("q")
    cat = request.GET.get("cat")

    products = Product.objects.all()

    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(category__icontains=q) |
            Q(description__icontains=q)
        )

    if cat:
        products = products.filter(category__iexact=cat)

    return render(request, "products.html", {"products": products})


# =========================
# SUPPORT FORM
# =========================
def support(request):
    if request.method == "POST":
        tid = "RC-" + str(uuid.uuid4()).split("-")[0].upper()

        ticket = SupportTicket.objects.create(
            ticket_id=tid,
            name=request.POST["name"],
            phone=request.POST["phone"],
            email=request.POST["email"],
            issue_type=request.POST["issue_type"],
            message=request.POST["message"],
            photo=request.FILES.get("photo")
        )

        send_support_ticket_email(ticket)

        send_brevo_email(
            subject=f"Ticket {tid} Received - RCShop",
            html_content=f"""
            <h2>Support Ticket Received</h2>
            <p>Hello {ticket.name},</p>
            <p>Your support ticket <b>{tid}</b> has been successfully submitted.</p>
            <p><b>Issue:</b> {ticket.issue_type}</p>
            <p>{ticket.message}</p>
            """,
            to_emails=[ticket.email]
        )

        return render(request, "support_success.html", {"ticket": tid})

    return render(request, "support.html")


# =========================
# TRACK TICKET
# =========================
def track_ticket(request):
    ticket = None
    if request.method == "POST":
        tid = request.POST.get("ticket_id", "").strip().upper()
        ticket = SupportTicket.objects.filter(ticket_id=tid).first()

    return render(request, "track_ticket.html", {"ticket": ticket})

# =========================
# CHECKOUT
# =========================
@login_required(login_url="login")
def checkout(request):

    user = request.user
    profile, _ = UserProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        try:
            items = json.loads(request.POST.get("items", "[]"))
        except:
            items = []

        mobile = request.POST.get("mobile")

        if mobile:
            profile.mobile = mobile
            profile.save()

        request.session["checkout_data"] = {
            "name": request.POST.get("name", ""),
            "email": request.POST.get("email", ""),
            "mobile": mobile or "",
            "address": request.POST.get("address", ""),
            "pincode": request.POST.get("pincode", ""),
            "items": items,
            "subtotal": str(request.POST.get("subtotal", "0")),
            "total": str(request.POST.get("total", "0")),
        }

        return redirect("payment")

    return render(request, "checkout.html", {
        "user_name": user.first_name,
        "user_email": user.email,
        "user_mobile": profile.mobile or "",
    })


# =========================
# PAYMENT SELECTION PAGE
# =========================
def payment(request):
    data = request.session.get("checkout_data")
    if not data:
        return redirect("checkout")

    return render(request, "payment.html", {"total": data.get("total")})


# =========================
# RAZORPAY ORDER CREATE (FINAL)
# =========================
@require_POST
def create_razorpay_order(request):
    data = request.session.get("checkout_data")
    if not data:
        return JsonResponse({"error": "No checkout session"})

    # Amount in paise
    amount = int(Decimal(str(data["total"])) * 100)

    rp_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": "RC-" + uuid.uuid4().hex[:10],
        "notes": {
            "name": data.get("name"),
            "email": data.get("email"),
            "mobile": data.get("mobile"),
        },
        "payment_capture": 1
    })

    # Save order id for verification later
    request.session["razorpay_order_id"] = rp_order["id"]

    return JsonResponse({
        "order_id": rp_order["id"],
        "amount": amount,
        "currency": "INR"
    })

# =========================
# RAZORPAY PAYMENT SUCCESS
# =========================
@csrf_exempt
def razorpay_success(request):

    payment_id = request.GET.get("razorpay_payment_id")
    order_id = request.GET.get("razorpay_order_id")
    signature = request.GET.get("razorpay_signature")

    if not payment_id or not order_id:
        return redirect("checkout")

    try:
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        # 🔥 FETCH ORDER CREATED BEFORE PAYMENT
        order = Order.objects.get(temp_order_id=order_id)

        order.razorpay_payment_id = payment_id
        order.razorpay_signature = signature
        order.is_paid = True
        order.status = "Placed"
        order.save()

        send_invoice_mail(order)

        return redirect(reverse("thankyou") + f"?order_id={order.id}")

    except Exception as e:
        print("RAZORPAY ERROR:", e)
        return redirect("checkout")

# =========================
# THANK YOU
# =========================
def thankyou(request):
    order_id = request.GET.get("order_id")
    order = get_object_or_404(Order, id=order_id)
    return render(request, "thankyou.html", {"order": order})

# =========================
# GENERATE INVOICE PDF
# =========================
def generate_invoice_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    font = "Helvetica"

    p.setFillColorRGB(0.1, 0.2, 0.35)
    p.rect(0, height - 80, width, 80, fill=1)
    p.setFillColorRGB(1, 1, 1)
    p.setFont(font, 20)
    p.drawString(40, height - 50, "RCShop")

    p.setFillColorRGB(0, 0, 0)
    p.setFont(font, 10)
    p.drawString(40, height - 110, f"Invoice No: RC-{order.id}")
    p.drawString(40, height - 130, f"Customer: {order.name}")
    p.drawString(40, height - 150, f"Mobile: {order.mobile}")

    y = height - 200
    for item in order.items:
        p.drawString(40, y, f"{item['name']}  x{item['quantity']}  Rs.{item['price']}")
        y -= 18

    p.drawString(40, y - 10, f"Total Amount: Rs.{order.total_amount}")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# =========================
# CASH ON DELIVERY
# =========================
def cod_details(request):
    data = request.session.get("checkout_data")
    if not data:
        return redirect("checkout")

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=data["name"],
            email=data["email"],
            mobile=data["mobile"],
            address=data["address"],
            items=data["items"],
            subtotal=Decimal(data["subtotal"]),
            total_amount=Decimal(data["total"]),
            payment_method="COD",
            status="Placed"
        )

        request.session.pop("checkout_data", None)
        return redirect(reverse("thankyou") + f"?order_id={order.id}")

    return render(request, "cod_details.html", {"data": data})


# =========================
# MY ACCOUNT
# =========================
@login_required(login_url="login")
def my_account(request):
    return render(request, "account.html")


@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "my_orders.html", {"orders": orders})


@login_required(login_url="login")
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "order_detail.html", {"order": order})


# =========================
# ADMIN ORDERS
# =========================
@staff_member_required
def admin_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin/orders.html", {"orders": orders})


@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        order.status = request.POST.get("status")
        order.save()
    return redirect("admin_orders")


# =========================
# LOGOUT
# =========================
def logout_user(request):
    logout(request)
    return redirect("logout_page")


def logout_page(request):
    return render(request, "logout.html")

# =========================
# TRACK ORDER
# =========================
def track_order(request):
    order = None
    error = None

    if request.method == "POST":
        order_id = request.POST.get("order_id")
        mobile = request.POST.get("mobile")

        try:
            order = Order.objects.get(id=order_id, mobile=mobile)
        except Order.DoesNotExist:
            error = "Order not found. Please check details."

    return render(request, "track_order.html", {"order": order, "error": error})


# =========================
# REGISTER
# =========================
def register(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        cpassword = request.POST.get("cpassword")

        if password != cpassword:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "register.html")


# =========================
# API CHECKOUT (OPTIONAL)
# =========================
@require_POST
def create_razorpay_order(request):
    data = request.session.get("checkout_data")
    if not data:
        return JsonResponse({"error": "No checkout session"})

    amount = int(Decimal(str(data["total"])) * 100)

    rp_order = client.order.create({
        "amount": amount,
        "currency": "INR",
        "receipt": "RC-" + uuid.uuid4().hex[:10],
        "payment_capture": 1
    })

    request.session["razorpay_order_id"] = rp_order["id"]

    return JsonResponse({
        "order_id": rp_order["id"],
        "amount": amount,
        "key": settings.RAZORPAY_KEY_ID
    })
@csrf_exempt
def razorpay_webhook(request):
    payload = request.body
    signature = request.headers.get("X-Razorpay-Signature")

    try:
        client.utility.verify_webhook_signature(
            payload, signature, settings.RAZORPAY_WEBHOOK_SECRET
        )
    except:
        return HttpResponseBadRequest("Invalid Signature")

    data = json.loads(payload)

    if data["event"] == "payment.captured":
        rp_order = data["payload"]["payment"]["entity"]["order_id"]
        rp_payment = data["payload"]["payment"]["entity"]["id"]

        order = Order.objects.filter(razorpay_order_id=rp_order).first()
        if order:
            order.is_paid = True
            order.razorpay_payment_id = rp_payment
            order.save()

    return JsonResponse({"status": "ok"})
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def api_checkout(request):
    return JsonResponse({"status": "ok"})
