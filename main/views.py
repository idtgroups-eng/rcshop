# =========================
# IMPORTS
# =========================

import json, base64, os, uuid, qrcode
from io import BytesIO
from decimal import Decimal

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import logout
from django.contrib.auth.models import User

from .models import (
    Product, Order, OrderItem, SupportTicket,
    UserProfile, PaymentProof
)

from .utils import (
    send_support_ticket_email,
    send_brevo_email,
    send_invoice_mail,
)

import razorpay

# Razorpay Client Setup
client = None
try:
    if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )
except Exception as e:
    print("Razorpay Config Error:", e)

# =========================
# BASIC PAGES
# =========================
def index(request): return render(request, "index.html")
def about(request): return render(request, "about.html")
from django.shortcuts import get_object_or_404
from .models import Product

def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)

    return render(request, "product_details.html", {
        "product": product
    })

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

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile


@login_required(login_url="login")
def checkout(request):

    # ✅ Profile get/create
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    # ❌ IMPORTANT: DB cart check hata diya (warna redirect loop hota hai)
    # cart_items = CartItem.objects.filter(user=request.user)
    # if not cart_items.exists():
    #     return redirect("cart")

    # =========================
    # POST (Form Submit)
    # =========================
    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")

        subtotal = request.POST.get("subtotal")
        total = request.POST.get("total")

        # ✅ Save/update profile
        profile.full_name = name
        profile.email = email
        profile.mobile = mobile
        profile.address = address
        profile.pincode = pincode
        profile.save()

        # ✅ Save checkout data in session
        request.session["checkout_data"] = {
            "name": name,
            "email": email,
            "mobile": mobile,
            "address": address,
            "pincode": pincode,
            "subtotal": subtotal,
            "total": total,
        }

        # 🚀 Go to payment page
        return redirect("payment")

    # =========================
    # GET (Open page)
    # =========================
    return render(request, "checkout.html", {
        "profile": profile
    })
    # =========================
    # ✅ NORMAL PAGE LOAD (GET)
    # =========================
    context = {
        "profile": profile,
        "cart_items": cart_items,
    }

    return render(request, "checkout.html", context)

    # =========================
    # ✅ HANDLE FORM SUBMIT
    # =========================
    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        mobile = request.POST.get("mobile")
        address = request.POST.get("address")
        pincode = request.POST.get("pincode")

        subtotal = request.POST.get("subtotal")
        total = request.POST.get("total")

        # 👉 Optional: profile update
        profile.full_name = name
        profile.email = email
        profile.mobile = mobile
        profile.address = address
        profile.pincode = pincode
        profile.save()

        # 👉 आगे payment page पर भेजो
        return redirect("payment")

    # =========================
    # ✅ NORMAL GET REQUEST
    # =========================
    context = {
        "profile": profile,
        "cart_items": cart_items,
    }

    return render(request, "checkout.html", context)

    # =========================
    # ✅ POST REQUEST (Form Submit)
    # =========================
    if request.method == "POST":

        # ✅ Items safe load
        try:
            items = json.loads(request.POST.get("items", "[]"))
        except Exception:
            items = []

        mobile = request.POST.get("mobile", "")

        # ✅ Save mobile in profile safely
        if mobile:
            profile.mobile = mobile
            profile.save()

        # ✅ Store checkout data in session safely
        request.session["checkout_data"] = {
            "name": request.POST.get("name", ""),
            "email": request.POST.get("email", ""),
            "mobile": mobile,
            "address": request.POST.get("address", ""),
            "pincode": request.POST.get("pincode", ""),
            "items": items,
            "subtotal": request.POST.get("subtotal", "0").replace(",", ""),
            "total": request.POST.get("total", "0").replace(",", ""),
        }

        # ✅ Redirect to payment page
        return redirect("payment")

    # =========================
    # ✅ GET REQUEST (Page Open)
    # =========================
    return render(request, "checkout.html", {
        "profile": profile,
        "cart_items": cart_items,
    })

    # =========================
    # ✅ GET REQUEST (Open Checkout Page)
    # =========================
    return render(request, "checkout.html", {
        "user_name": user.first_name or user.username,
        "user_email": user.email,
        "user_mobile": profile.mobile or "",
    })

# =========================
# PAYMENT SELECTION PAGE
# =========================
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from decimal import Decimal
import uuid

def payment(request):
    data = request.session.get("checkout_data")

    # 🔴 अगर session data नहीं है → वापस checkout
    if not data:
        return redirect("checkout")

    return render(request, "payment.html", {
        "total": data.get("total"),
        "user": data
    })


# =========================
# CREATE RAZORPAY ORDER
# =========================
@csrf_exempt
def create_razorpay_order(request):

    # 🔴 Razorpay client check
    if not client:
        return JsonResponse({"error": "Payment gateway not configured"}, status=500)

    data = request.session.get("checkout_data")

    # 🔴 Session missing
    if not data:
        return JsonResponse({"error": "No checkout session"}, status=400)

    try:
        # 💰 amount convert (₹ → paise)
        amount = int(Decimal(data["total"]) * 100)

        # 🔥 Razorpay order create
        rp_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "receipt": "RC-" + uuid.uuid4().hex[:10],
            "payment_capture": 1
        })

        # 🧾 Order save in DB
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            name=data.get("name"),
            email=data.get("email"),
            mobile=data.get("mobile"),
            address=data.get("address"),

            # 🔥 FIX: items safe handling
            items=json.dumps(data.get("items", "[]")),

            subtotal=Decimal(data.get("subtotal", 0)),
            total_amount=Decimal(data.get("total", 0)),

            payment_method="ONLINE",
            status="Pending",
            is_paid=False,
            razorpay_order_id=rp_order["id"]
        )

        return JsonResponse({
            "key": settings.RAZORPAY_KEY_ID,
            "order_id": rp_order["id"],
            "amount": amount,
            "currency": "INR",
            "email": data.get("email"),
            "contact": data.get("mobile"),
        })

    except Exception as e:
        print("RAZORPAY CREATE ERROR:", e)
        return JsonResponse({"error": "Failed to create order"}, status=500)


# =========================
# PAYMENT SUCCESS HANDLER
# =========================
@csrf_exempt
def razorpay_success(request):

    payment_id = request.GET.get("razorpay_payment_id")
    order_id = request.GET.get("razorpay_order_id")
    signature = request.GET.get("razorpay_signature")

    # 🔴 Missing params
    if not payment_id or not order_id or not signature:
        return redirect("checkout")

    try:
        # 🔐 Signature verify
        client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        # 🧾 Order fetch
        order = Order.objects.get(razorpay_order_id=order_id)

        # ✅ Update payment status
        order.razorpay_payment_id = payment_id
        order.razorpay_signature = signature
        order.is_paid = True
        order.status = "Placed"
        order.save()

        # 📩 Send invoice
        try:
            send_invoice_mail(order)
        except Exception as mail_error:
            print("EMAIL ERROR:", mail_error)

        # 🧹 OPTIONAL: session clear (best practice)
        if "checkout_data" in request.session:
            del request.session["checkout_data"]

        return redirect(reverse("thankyou") + f"?order_id={order.id}")

    except Exception as e:
        print("RAZORPAY VERIFY ERROR:", e)
        return redirect("checkout")
    
# =========================
# THANK YOU
# =========================
def thankyou(request):
    order_id = request.GET.get("order_id")
    order = get_object_or_404(Order, id=order_id)
    return render(request, "thankyou.html", {"order": order})


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

        # =======================
        # SEND INVOICE EMAIL
        # =======================
        try:
            send_invoice_mail(order)
        except Exception as e:
            print("COD Invoice Email Error:", e)

        request.session.pop("checkout_data", None)

        return redirect(reverse("thankyou") + f"?order_id={order.id}")

    return render(request, "cod_details.html", {"data": data})

# =========================
# VIEW INVOICE PAGE
# =========================
def view_invoice(request):
    order_id = request.GET.get("order_id")

    if not order_id:
        return redirect("my_orders")

    order = get_object_or_404(Order, id=order_id)

    # Security: user sirf apna invoice dekh sake
    if not request.user.is_staff and order.user != request.user:
        return HttpResponseBadRequest("Not allowed")

    return render(request, "invoice.html", {"order": order})


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


def logout_user(request):
    logout(request)
    return redirect("logout_page")


def logout_page(request):
    return render(request, "logout.html")


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

