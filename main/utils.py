# main/utils.py

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
BREVO_FROM_EMAIL = settings.DEFAULT_FROM_EMAIL


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
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=20
        )

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
