from django.contrib import admin
from django.http import HttpResponse
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from .models import Order, PaymentProof


# =========================
# INVOICE PDF GENERATOR (ADMIN)
# =========================
def generate_invoice_pdf_admin(order):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    # ---------- HEADER ----------
    y = height - 40
    p.setFont("Helvetica-Bold", 16)
    p.drawString(40, y, "RCShop - Tax Invoice")

    y -= 20
    p.setFont("Helvetica", 9)
    p.drawString(40, y, "GSTIN: 02WRWPK1356B1Z0")
    y -= 12
    p.drawString(40, y, "PAN: BRWPK1356B")

    # ---------- ORDER DETAILS ----------
    y -= 20
    p.setFont("Helvetica", 9)
    p.drawString(40, y, f"Order ID: {order.id}")
    y -= 12
    p.drawString(40, y, f"Customer: {order.name}")
    y -= 12
    p.drawString(40, y, f"Mobile: {order.mobile}")
    y -= 12
    p.drawString(40, y, f"Email: {order.email}")
    y -= 12
    p.drawString(40, y, f"Address: {order.address}")

    # ---------- PRODUCTS ----------
    y -= 25
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, "Products")

    y -= 15
    p.setFont("Helvetica", 9)

    subtotal = 0
    for item in order.items:
        qty = int(item.get("quantity", 1))
        price = float(item.get("price", 0))
        line_total = qty * price
        subtotal += line_total
        p.drawString(45, y, f"{item.get('name')}  x{qty}  ₹{line_total}")
        y -= 12

    # ---------- TOTAL ----------
    gst = round(subtotal * 0.18, 2)
    grand_total = round(subtotal + gst, 2)

    y -= 15
    p.setFont("Helvetica-Bold", 10)
    p.drawString(40, y, f"Subtotal: ₹{subtotal}")
    y -= 12
    p.drawString(40, y, f"GST (18%): ₹{gst}")
    y -= 14
    p.drawString(40, y, f"Grand Total: ₹{grand_total}")

    # ---------- FOOTER ----------
    y -= 30
    p.setFont("Helvetica", 8)
    p.drawString(40, y, "This is a computer generated tax invoice.")

    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer


# =========================
# ADMIN ACTION
# =========================
def download_invoice(modeladmin, request, queryset):
    if queryset.count() != 1:
        modeladmin.message_user(
            request,
            "Please select exactly ONE order to download invoice.",
            level="error",
        )
        return

    order = queryset.first()
    pdf = generate_invoice_pdf_admin(order)

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="Invoice_{order.id}.pdf"'
    return response

download_invoice.short_description = "📄 Download Invoice PDF"


# =========================
# ORDER ADMIN
# =========================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","name","email","mobile","payment_method","total_amount","status","created_at")
    search_fields = ("name","email","mobile")
    list_filter = ("payment_method","status","created_at")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    actions = [download_invoice]


# =========================
# PAYMENT PROOF ADMIN (SAFE)
# =========================
@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    list_display = ("order_id", "name", "phone", "amount", "verified")
    list_filter = ("verified",)
    search_fields = ("order_id", "name", "phone")
