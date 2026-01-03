import base64
import requests
from io import BytesIO

from django.conf import settings
from django.template.loader import render_to_string

# Optional PDF support
try:
    from xhtml2pdf import pisa
except Exception:
    pisa = None


# ==============================
# BREVO CONFIG (FROM SETTINGS)
# ==============================
BREVO_API_KEY = settings.BREVO_API_KEY
BREVO_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "support@rcshop.co.in")


# ==============================
# PDF GENERATOR (SAFE)
# ==============================
def render_to_pdf_bytes(template_name, context=None):
    if not pisa:
        return None

    try:
        html = render_to_string(template_name, context or {})
        result = BytesIO()
        status = pisa.CreatePDF(html, dest=result)

        if status.err:
            print("❌ PDF render error")
            return None

        return result.getvalue()

    except Exception as e:
        print("❌ PDF generation exception:", e)
        return None


# ==============================
# BREVO EMAIL SENDER (API)
# ==============================
def send_brevo_email(subject, html_content, to_emails, attachments=None):

    if not BREVO_API_KEY:
        print("❌ BREVO_API_KEY missing")
        return False

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {
            "name": "RCShop",
            "email": BREVO_FROM_EMAIL,
        },
        "to": [{"email": email} for email in to_emails],
        "subject": subject,
        "htmlContent": html_content,
    }

    if attachments:
        payload["attachment"] = attachments

    headers = {
        "accept": "application/json",
        "api-key": BREVO_API_KEY,
        "content-type": "application/json",
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=8)

        if response.status_code not in (200, 201, 202):
            print("❌ Brevo failed:", response.status_code, response.text)
            return False

        return True

    except Exception as e:
        print("❌ Brevo API exception:", e)
        return False


# ==============================
# ORDER EMAILS (CUSTOMER + ADMIN)
# ==============================
def send_order_emails(order, admin_email):

    order_id = order.id

    # ---------- PDF INVOICE ----------
    pdf_bytes = render_to_pdf_bytes(
        "emails/invoice_pdf.html",
        {"order": order}
    )

    attachments = []
    if pdf_bytes:
        attachments.append({
            "content": base64.b64encode(pdf_bytes).decode(),
            "name": f"Invoice_{order_id}.pdf",
            "type": "application/pdf",
        })

    # ---------- CUSTOMER EMAIL ----------
    try:
        customer_html = render_to_string(
            "emails/order_success.html",
            {"order": order}
        )
    except Exception as e:
        print("❌ Customer email template error:", e)
        return False

    send_brevo_email(
        subject=f"Order Confirmed - #{order_id}",
        html_content=customer_html,
        to_emails=[order.email],
        attachments=attachments
    )

    # ---------- ADMIN EMAIL ----------
    admin_html = f"""
        <h2>New Order Received</h2>
        <p><b>Order ID:</b> {order_id}</p>
        <p><b>Name:</b> {order.name}</p>
        <p><b>Mobile:</b> {order.mobile}</p>
        <p><b>Total:</b> ₹{order.total_amount}</p>
        <p><b>Payment:</b> {order.payment_method}</p>
    """

    send_brevo_email(
        subject=f"New Order - #{order_id}",
        html_content=admin_html,
        to_emails=[admin_email],
    )

    return True
# ==============================
# SUPPORT TICKET EMAIL (ADMIN)
# ==============================
def send_support_ticket_email(ticket):

    attachments = []

    if ticket.photo:
        try:
            photo_bytes = ticket.photo.read()
            attachments.append({
                "content": base64.b64encode(photo_bytes).decode(),
                "name": ticket.photo.name,
                "type": "image/jpeg"
            })
        except Exception as e:
            print("❌ Ticket photo attach error:", e)

    admin_html = f"""
        <h2>New Support Ticket</h2>
        <p><b>Ticket ID:</b> {ticket.ticket_id}</p>
        <p><b>Name:</b> {ticket.name}</p>
        <p><b>Phone:</b> {ticket.phone}</p>
        <p><b>Email:</b> {ticket.email}</p>
        <p><b>Issue:</b> {ticket.issue_type}</p>
        <p><b>Message:</b> {ticket.message}</p>
    """

    send_brevo_email(
        subject=f"New Support Ticket - {ticket.ticket_id}",
        html_content=admin_html,
        to_emails=[settings.ADMIN_EMAIL],
        attachments=attachments
    )
def send_sms(phone, message):
    import requests
    headers = {
        "authorization": settings.FAST2SMS_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "route": "q",
        "numbers": phone,
        "message": message,
        "sender_id": "RCSHOP"
    }
    try:
        requests.post("https://www.fast2sms.com/dev/bulkV2", json=payload, headers=headers, timeout=8)
    except Exception as e:
        print("❌ SMS Error:", e)
def send_whatsapp(phone, message):
    import requests, urllib.parse
    text = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={text}&apikey={settings.WHATSAPP_PHONE}"
    try:
        requests.get(url, timeout=8)
    except Exception as e:
        print("❌ WhatsApp error:", e)
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
import os
from django.conf import settings

def generate_invoice_pdf(order, items):
    file_path = os.path.join(settings.MEDIA_ROOT, f"invoice_{order.id}.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    styles = getSampleStyleSheet()

    data = [["Product", "Qty", "Price"]]
    for i in items:
        data.append([i.product.name, i.quantity, f"₹{i.price}"])

    doc.build([
        Paragraph("<b>RCShop Invoice</b>", styles["Title"]),
        Spacer(1,12),
        Paragraph(f"Order ID: {order.id}", styles["BodyText"]),
        Paragraph(f"Customer: {order.name}", styles["BodyText"]),
        Spacer(1,12),
        Table(data),
        Spacer(1,12),
        Paragraph(f"Total: ₹{order.total}", styles["BodyText"])
    ])

    return file_path
from django.core.mail import EmailMessage

def send_invoice_mail(subject, body, to, pdf_path):
    mail = EmailMessage(subject, body, settings.EMAIL_HOST_USER, to)
    mail.attach_file(pdf_path)
    mail.send()
