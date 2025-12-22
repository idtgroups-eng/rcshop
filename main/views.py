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
from .utils import send_brevo_email   # ✅ Brevo API only


# =========================
# BASIC PAGES
# =========================
def index(request): return render(request, "index.html")
def about(request): return render(request, "about.html")
def products(request): return render(request, "products.html")
def product_details(request): return render(request, "product_details.html")
def cart(request): return render(request, "cart.html")
def contact(request): return render(request, "contact.html")


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
            "gst": str(request.POST.get("gst", "0")),
            "flat_discount": str(request.POST.get("flat_discount", "0")),
            "extra_discount": str(request.POST.get("extra_discount", "0")),
            "total": str(request.POST.get("total", "0")),
        }
        return redirect("payment")

    return render(request, "checkout.html")


# =========================
# PAYMENT OPTIONS
# =========================
def payment(request):
    data = request.session.get("checkout_data")
    if not data:
        return redirect("checkout")
    return render(request, "payment.html", {"total": data.get("total")})


def payment_upi(request):
    data = request.session.get("checkout_data")
    if not data:
        return redirect("checkout")

    amount = data.get("total", "0")
    upi_id = "9625252254@ybl"
    name = "RCShop"

    upi_url = f"upi://pay?pa={upi_id}&pn={name}&am={amount}&cu=INR"
    qr = qrcode.make(upi_url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")

    return render(request, "payment-upi.html", {
        "qr_code": base64.b64encode(buffer.getvalue()).decode(),
        "amount": amount,
        "upi_id": upi_id,
    })


def payment_online(request):
    data = request.session.get("checkout_data")
    if not data:
        return redirect("checkout")
    return render(request, "payment-online.html", {"total": data.get("total")})



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
    p.drawString(40, y - 28, "Phone: +91 7018677970")
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
    gst = float(order.gst or 0)
    flat_discount = float(order.flat_discount or 0)
    extra_discount = float(order.extra_discount or 0)
    total_amount = float(order.total_amount or 0)

    p.drawRightString(width - 155, y, "Subtotal:")
    p.drawRightString(width - 80, y, f"Rs. {subtotal:,.2f}")

    y -= 15
    p.drawRightString(width - 155, y, "GST:")
    p.drawRightString(width - 80, y, f"Rs. {gst:,.2f}")

    if flat_discount > 0:
        y -= 15
        p.drawRightString(width - 155, y, "Flat Discount:")
        p.drawRightString(width - 80, y, f"- Rs. {flat_discount:,.2f}")

    if extra_discount > 0:
        y -= 15
        p.drawRightString(width - 155, y, "Extra Discount:")
        p.drawRightString(width - 80, y, f"- Rs. {extra_discount:,.2f}")

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

# =========================
# COD CONFIRM (EMAIL + PDF)
# =========================
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
            gst=Decimal(data.get("gst", "0")),
            flat_discount=Decimal(data.get("flat_discount", "0")),
            extra_discount=Decimal(data.get("extra_discount", "0")),
            total_amount=Decimal(data.get("total", "0")),

            payment_method="COD",
            status="Placed",
        )

        # ---------- PDF (Render-safe) ----------
        pdf_buffer = generate_invoice_pdf(order)
        pdf_bytes = pdf_buffer.getvalue() if pdf_buffer else None

        attachments = []
        if pdf_bytes:
            attachments.append({
                "content": base64.b64encode(pdf_bytes).decode(),
                "name": f"Invoice_{order.id}.pdf",
                "type": "application/pdf",
            })

        # ---------- CUSTOMER EMAIL ----------
        send_brevo_email(
            subject=f"Order Confirmed - #{order.id}",
            html_content=f"""
                <h2>Order Confirmed (Cash on Delivery)</h2>
                <p>Hi {order.name},</p>
                <p>Your order <b>#{order.id}</b> has been placed successfully.</p>
                <p><b>Total Amount:</b> ₹{order.total_amount}</p>
                <p>Invoice is attached with this email.</p>
            """,
            to_emails=[order.email],
            attachments=attachments
        )

        # ---------- ADMIN EMAIL ----------
        send_brevo_email(
            subject=f"New COD Order - #{order.id}",
            html_content=f"""
                <h3>New COD Order Received</h3>
                <p><b>Order ID:</b> {order.id}</p>
                <p><b>Name:</b> {order.name}</p>
                <p><b>Mobile:</b> {order.mobile}</p>
                <p><b>Email:</b> {order.email}</p>
                <p><b>Total:</b> ₹{order.total_amount}</p>
                <p><b>Payment Mode:</b> Cash on Delivery</p>
                <hr>
                <p>Invoice PDF attached for verification.</p>
            """,
            to_emails=[settings.ADMIN_EMAIL],
            attachments=attachments
        )

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
        "gst": order.gst,
        "flat_discount": order.flat_discount,
        "extra_discount": order.extra_discount,
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
                    <h3>Your Order Status Updated</h3>
                    <p>Hi {order.name},</p>
                    <p>Your order <b>#{order.id}</b> status is now:</p>
                    <h2>{order.status}</h2>
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
