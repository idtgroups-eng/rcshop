import json
import base64
import qrcode
import os   
from io import BytesIO
from decimal import Decimal
from reportlab.pdfbase import pdfmetrics   # ✅ ADD
from reportlab.pdfbase.ttfonts import TTFont  # ✅ ADD

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.conf import settings
from django.urls import reverse

from .models import Order
from .utils import send_brevo_email, send_order_emails




# =========================
# BASIC PAGES
# =========================
def index(request): return render(request, "index.html")
def about(request): return render(request, "about.html")
from django.db.models import Q
from .models import Product

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

def product_details(request): return render(request, "product_details.html")
def cart(request): return render(request, "cart.html")
def contact(request): return render(request, "contact.html")
def computer_sales(request):
    return render(request, "computer_sales.html")
def repair_maintenance(request):
    return render(request, "repair_maintenance.html")
def printer_toner(request):
    return render(request, "printer_toner.html")
def cctv_fitting(request):
    return render(request, "cctv_fitting.html")
def lokmitra_services(request):
    return render(request, "lokmitra_services.html")
def hp_retailer(request):
    return render(request, "hp-retailer.html")
import uuid
from django.shortcuts import render
from django.core.mail import send_mail
from .models import SupportTicket
def return_policy(request):
    return render(request, "return_policy.html")
def return_request(request):
    return render(request, "return_request.html")

# =============================
# SUPPORT FORM SUBMIT
# =============================
from .utils import send_support_ticket_email, send_brevo_email

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

        # 📧 ADMIN EMAIL WITH PHOTO ATTACHMENT
        send_support_ticket_email(ticket)

        # 📩 CUSTOMER CONFIRMATION EMAIL
        send_brevo_email(
            subject=f"Ticket {tid} Received - RCShop",
            html_content=f"""
                <h2>Support Ticket Received</h2>
                <p>Hello {ticket.name},</p>
                <p>Your support ticket <b>{tid}</b> has been successfully submitted.</p>
                <p>Our technical team will contact you shortly.</p>
                <p><b>Issue:</b> {ticket.issue_type}</p>
                <p>{ticket.message}</p>
                <br>
                <p>Thank you for choosing RCShop.</p>
            """,
            to_emails=[ticket.email]
        )

        return render(request, "support_success.html", {"ticket": tid})

    return render(request, "support.html")

# =============================
# TRACK TICKET PAGE
# =============================
def track_ticket(request):
    ticket = None
    if request.method == "POST":
        tid = request.POST.get("ticket_id").strip().upper()
        ticket = SupportTicket.objects.filter(ticket_id=tid).first()

    return render(request, "track_ticket.html", {"ticket": ticket})

# =========================
# CHECKOUT
# =========================
def checkout(request):
    if request.method == "POST":
        try:
            items = json.loads(request.POST.get("items", "[]"))
        except Exception:
            items = []

        request.session["checkout_data"] = {
            "name": request.POST.get("name", ""),
            "email": request.POST.get("email", ""),
            "mobile": request.POST.get("mobile", ""),
            "address": request.POST.get("address", ""),
            "city": request.POST.get("city", ""),
            "pincode": request.POST.get("pincode", ""),
            "items": items,

            # store as STRING (safe for Decimal)
            "subtotal": str(request.POST.get("subtotal", "0")),
            "total": str(request.POST.get("total", "0")),
        }
        return redirect("payment")

    return render(request, "checkout.html")


# =========================
# PAYMENT OPTIONS (FIXED)
# =========================
def payment(request):
    """
    Allow both:
    - POST (from checkout form)
    - GET  (direct link / debug)
    """

    data = request.session.get("checkout_data")

    # 🔓 Allow GET (direct open)
    if request.method == "GET":
        return render(request, "payment.html", {
            "total": data.get("total") if data else "0"
        })

    # 🔒 POST case (normal checkout flow)
    if not data:
        return redirect("checkout")

    return render(request, "payment.html", {
        "total": data.get("total")
    })
import uuid

def payment_upi(request):
    data = request.session.get("checkout_data")

    # Allow direct open safety
    if request.method == "GET" and not data:
        return render(request, "payment-upi.html", {
            "qr_code": None,
            "amount": "0",
            "upi_id": "9625252254@ybl",
            "upi_url": "",
            "order_id": ""
        })

    if not data:
        return redirect("checkout")

    amount = str(data.get("total", "0"))
    upi_id = "9625252254@ybl"
    name = "RCShop"

    # Generate secure unique order id
    order_id = str(uuid.uuid4()).replace("-", "")[:12]
    request.session["upi_order_id"] = order_id

    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR&tn=RCShop{order_id}"

    qr = qrcode.make(upi_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return render(request, "payment-upi.html", {
        "qr_code": base64.b64encode(buffer.getvalue()).decode(),
        "amount": amount,
        "upi_id": upi_id,
        "upi_url": upi_url,
        "order_id": order_id
    })
def upi_verify(request):
    order_id = request.session.get("upi_order_id")

    # Abhi basic safety (next step me Cashfree/Razorpay connect hoga)
    if order_id:
        return HttpResponse("PENDING")

    return HttpResponse("FAILED")


def payment_online(request):
    data = request.session.get("checkout_data")

    # 🔓 Allow GET
    if request.method == "GET":
        return render(request, "payment-online.html", {
            "total": data.get("total") if data else "0"
        })

    if not data:
        return redirect("checkout")

    return render(request, "payment-online.html", {
        "total": data.get("total")
    })

# =========================
# PDF INVOICE GENERATOR
# =========================
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from decimal import Decimal
import os
from django.conf import settings

def generate_invoice_pdf(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    font_name = "Helvetica"

    # ---------- HEADER BAR ----------
    p.setFillColorRGB(0.1, 0.2, 0.35)
    p.rect(0, height - 80, width, 80, fill=1)
    p.setFillColorRGB(1, 1, 1)

    p.setFont(font_name, 20)
    p.drawString(40, height - 50, "RCShop")

    p.setFont(font_name, 11)
    p.drawRightString(width - 40, height - 45, "TAX INVOICE")

    # ---------- COMPANY INFO ----------
    p.setFillColorRGB(0, 0, 0)
    y = height - 110

    p.setFont(font_name, 10)
    p.drawString(40, y, "RCShop")
    p.drawString(40, y - 14, "Rajgarh, Sirmour, Himachal Pradesh")
    p.drawString(40, y - 28, "Phone: +91 9625252254")
    p.drawString(40, y - 42, "Email: support@rcshop.co.in")

    # ---------- INVOICE INFO BOX ----------
    p.rect(width - 260, y - 55, 220, 70, stroke=1, fill=0)

    p.drawString(width - 250, y - 15, f"Invoice No: RC-{order.id}")
    p.drawString(width - 250, y - 30, f"Order ID: {order.id}")
    p.drawString(
        width - 250, y - 45,
        f"Date: {order.created_at.strftime('%d %b %Y')}"
    )

    # ---------- CUSTOMER DETAILS ----------
    y -= 90
    p.setFont(font_name, 11)
    p.drawString(40, y, "BILL TO")

    p.setFont(font_name, 10)
    p.drawString(40, y - 18, f"Name: {order.name}")
    p.drawString(40, y - 32, f"Mobile: {order.mobile}")
    p.drawString(40, y - 46, f"Email: {order.email}")

    # ---------- TABLE HEADER ----------
    y -= 80
    p.setFillColorRGB(0.9, 0.9, 0.9)
    p.rect(40, y, width - 80, 25, fill=1)

    p.setFillColorRGB(0, 0, 0)
    p.setFont(font_name, 10)
    p.drawString(50, y + 7, "Product")
    p.drawString(width - 240, y + 7, "Qty")
    p.drawString(width - 190, y + 7, "Price")
    p.drawString(width - 120, y + 7, "Total")

    # ---------- PRODUCTS ----------
    y -= 25
    p.setFont(font_name, 10)

    for item in order.items:
        qty = int(item.get("quantity", 1))
        price = float(item.get("price", 0))
        total = qty * price

        p.drawString(50, y + 7, item.get("name"))
        p.drawRightString(width - 215, y + 7, str(qty))
        p.drawRightString(width - 155, y + 7, f"Rs. {price:,.2f}")
        p.drawRightString(width - 80, y + 7, f"Rs. {total:,.2f}")
        y -= 22

    # ---------- BILL BREAKUP ----------
    y -= 10
    p.setFont(font_name, 10)

    subtotal = float(order.subtotal or 0)
    total_amount = float(order.total_amount or 0)

    p.drawRightString(width - 155, y, "Subtotal:")
    p.drawRightString(width - 80, y, f"Rs. {subtotal:,.2f}")

    y -= 15

    # ---------- FINAL TOTAL ----------
    y -= 20
    p.setFont(font_name, 11)
    p.drawRightString(width - 155, y, "Total Amount:")
    p.setFont(font_name, 13)
    p.drawRightString(width - 80, y, f"Rs. {total_amount:,.2f}")

    # ---------- FOOTER ----------
    y -= 50
    p.setFont(font_name, 9)
    p.drawString(40, y, "Payment Method: Cash on Delivery")
    p.drawString(40, y - 14, "This is a computer-generated invoice. No signature required.")
    p.drawString(40, y - 28, "Thank you for shopping with RCShop!")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer

def cod_details(request):
    data = request.session.get("checkout_data")
    if not data:
        return redirect("checkout")

    if request.method == "POST":

        # ---------- CREATE ORDER ----------
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=data.get("name", ""),
            email=data.get("email", ""),
            mobile=data.get("mobile", ""),
            address=f"{data.get('address')}, {data.get('city')} - {data.get('pincode')}",
            items=data.get("items", []),
            subtotal=Decimal(data.get("subtotal", "0")),
            total_amount=Decimal(data.get("total", "0")),
            payment_method="COD",
            status="Placed",
        )

        # ---------- SEND ORDER EMAILS (PDF + CUSTOMER + ADMIN) ----------
        send_order_emails(order, settings.ADMIN_EMAIL)

        # ---------- CLEAN SESSION ----------
        request.session.pop("checkout_data", None)

        return redirect(reverse("thankyou") + f"?order_id={order.id}")

    return render(request, "cod_details.html", {"data": data})

# =========================
# THANK YOU & INVOICE
# =========================
def thankyou(request):
    order = get_object_or_404(Order, id=request.GET.get("order_id"))
    return render(request, "thankyou.html", {"order": order})


def invoice(request):
    order = get_object_or_404(Order, id=request.GET.get("order_id"))

    upi_id = "9625252254@ybl"
    upi_url = f"upi://pay?pa={upi_id}&pn=RCShop&am={order.total_amount}&cu=INR"

    qr = qrcode.make(upi_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return render(request, "invoice.html", {
        "order": order,
        "subtotal": order.subtotal,
        "total": order.total_amount,
        "qr_code": base64.b64encode(buffer.getvalue()).decode(),
        "upi_id": upi_id,
    })


# =========================
# API CHECKOUT (ONLINE)
# =========================
@require_POST
def api_checkout(request):
    try:
        data = json.loads(request.body)
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    order = Order.objects.create(
        name=data.get("name", "Customer"),
        email=data.get("email", ""),
        mobile=data.get("mobile", ""),
        address=data.get("address", ""),
        items=data.get("items", []),
        total_amount=Decimal(str(data.get("total", "0"))),
        payment_method="ONLINE",
        status="Confirmed",
    )

    return JsonResponse({"success": True, "order_id": order.id})


# =========================
# OTHER PAGES
# =========================
def return_request(request): return render(request, "return_request.html")
def order_tracking(request): return render(request, "order_tracking.html")
def shipping_policy(request): return render(request, "shipping_policy.html")
def help_center(request): return render(request, "help_center.html")
def return_policy(request): return render(request, "return_policy.html")
from django.contrib.admin.views.decorators import staff_member_required

from django.contrib.admin.views.decorators import staff_member_required


# =========================
# ADMIN ORDERS DASHBOARD
# =========================
@staff_member_required
def admin_orders(request):
    orders = Order.objects.all().order_by("-created_at")
    return render(request, "admin/orders.html", {"orders": orders})


# =========================
# UPDATE ORDER STATUS
# =========================
@staff_member_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")

        if new_status in dict(Order.ORDER_STATUS):
            order.status = new_status
            order.save()

            # ---------- CUSTOMER STATUS EMAIL ----------
            send_brevo_email(
                subject=f"Order #{order.id} Status Updated",
                html_content=f"""
                    <h2>Order Status Updated</h2>
                    <p>Hello {order.name},</p>
                    <p>Your order <b>#{order.id}</b> status has been updated to:</p>
                    <h3>{order.status}</h3>
                    <p>Thank you for shopping with RCShop.</p>
                """,
                to_emails=[order.email]
            )

    return redirect("admin_orders")

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

    return render(request, "track_order.html", {
        "order": order,
        "error": error
    })
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

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

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=name
        )
        user.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "register.html")
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import UserProfile, Order


# =========================
# ✅ FINAL CHECKOUT (AUTO-FILL + SESSION SAVE + PAYMENT FLOW)
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

        # Save mobile to profile
        if mobile:
            profile.mobile = mobile
            profile.save()

        # Save checkout session
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

        # 🚀 Redirect to payment
        return redirect("payment")

    # Auto-fill user data
    return render(request, "checkout.html", {
        "user_name": user.first_name,
        "user_email": user.email,
        "user_mobile": profile.mobile or "",
    })

# ✅ MY ACCOUNT
# =========================
@login_required(login_url="login")
def my_account(request):
    return render(request, "account.html")
from django.contrib.auth import logout

def logout_user(request):
    logout(request)
    return redirect("logout_page")

def logout_page(request):
    return render(request, "logout.html")

# =========================
# 🧾 MY ORDERS (ORDER HISTORY)
# =========================
@login_required(login_url="login")
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "my_orders.html", {"orders": orders})
@login_required(login_url="login")
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = order.items.all()  # assuming related_name="items"

    return render(request, "order_detail.html", {
        "order": order,
        "items": items
    })
@login_required
def save_address(request):
    if request.method == "POST":
        UserAddress.objects.create(
            user=request.user,
            name=request.POST["name"],
            mobile=request.POST["mobile"],
            address=request.POST["address"],
            pincode=request.POST["pincode"]
        )
    return redirect("checkout")

from django.shortcuts import render, redirect, get_object_or_404
from .models import PaymentProof
from .utils import send_brevo_email


# ===============================
# UPLOAD PAYMENT PROOF
# ===============================
def upload_payment_proof(request):
    data = request.session.get("checkout_data")

    if not data:
        return redirect("checkout")

    if request.method == "POST":
        PaymentProof.objects.create(
            order_id = data.get("order_id"),
            name     = data.get("name"),
            phone    = data.get("phone"),
            email    = data.get("email"),
            amount   = data.get("total"),
            screenshot = request.FILES.get("screenshot")
        )
        return redirect("payment_pending")

    return render(request, "upload-proof.html", {"data": data})


# ===============================
# PAYMENT PENDING (THANK YOU)
# ===============================
def payment_pending(request):
    return render(request, "payment_pending.html")


# ===============================
# ADMIN VERIFY PAYMENT
# ===============================
def verify_payment(request, id):
    p = get_object_or_404(PaymentProof, id=id)

    p.verified = True
    p.save()

    # Auto Email
    send_brevo_email(
        subject = "Payment Successful - RCShop",
        html_content = f"""
        <h2>Payment Successful</h2>
        <p>Hello {p.name},</p>
        <p>Your payment of <b>₹{p.amount}</b> has been verified.</p>
        <p>Order ID: <b>{p.order_id}</b></p>
        <p>Your order is now confirmed and will be processed shortly.</p>
        """,
        to_emails = [p.email]
    )

    # Success Page
    return render(request, "payment_success.html", {"payment": p})
