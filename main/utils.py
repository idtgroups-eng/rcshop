import base64
import requests
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string
from fpdf import FPDF


BREVO_API_KEY = getattr(settings, "BREVO_API_KEY", None)
BREVO_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "support@rcshop.co.in")


# ===============================
# PDF INVOICE GENERATOR (Render Compatible & Unicode Safe)
# ===============================
def generate_invoice_pdf(order):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.cell(0, 10, "RCShop Invoice", ln=True, align="C")
    pdf.ln(5)

    pdf.cell(0, 8, f"Order ID: {order.id}", ln=True)
    pdf.cell(0, 8, f"Name: {order.name}", ln=True)
    pdf.cell(0, 8, f"Phone: {order.mobile}", ln=True)
    pdf.cell(0, 8, f"Email: {order.email}", ln=True)

    # Rupee symbol hata kar INR use kiya – encoding safe
    pdf.cell(0, 8, f"Total Amount: INR {order.total_amount}", ln=True)

    pdf.ln(8)

    pdf.multi_cell(
        0,
        8,
        "Thank you for shopping with RCShop.\nYour order has been successfully placed."
    )

    buffer = BytesIO()

    try:
        pdf_output = pdf.output(dest='S').encode('latin-1', errors='ignore')
        buffer.write(pdf_output)
        buffer.seek(0)
        return buffer.read()
    except Exception as e:
        print("PDF Write Error:", e)
        return None


import requests
from django.conf import settings

# ===============================
# BREVO EMAIL SENDER (Production Safe)
# ===============================

BREVO_API_KEY = getattr(settings, "BREVO_API_KEY", None)
BREVO_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "idtgroups@gmail.com")


def send_brevo_email(subject, html_content, to_emails, attachments=None):

    if not BREVO_API_KEY:
        print("❌ BREVO_API_KEY not configured")
        return False

    if not to_emails:
        print("❌ No recipient emails")
        return False

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {
            "name": "RCStore",
            "email": BREVO_FROM_EMAIL
        },
        "to": [{"email": e} for e in to_emails if e],
        "subject": subject,
        "htmlContent": html_content,
    }

    if attachments:
        payload["attachment"] = attachments

    headers = {
        "api-key": BREVO_API_KEY,
        "accept": "application/json",
        "content-type": "application/json"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15
        )

        # 🔍 DEBUG OUTPUT (VERY IMPORTANT)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)

        if response.status_code in (200, 201):
            return True
        return False

    except Exception as e:
        print("❌ Brevo Email Exception:", e)
        return False

# ===============================
# ORDER INVOICE MAIL
# ===============================
def send_invoice_mail(order):

    pdf_bytes = None

    try:
        pdf_bytes = generate_invoice_pdf(order)
    except Exception as e:
        print("PDF Generation Error:", e)

    attachments = []

    if pdf_bytes:
        attachments.append({
            "content": base64.b64encode(pdf_bytes).decode(),
            "name": f"Invoice_RC{order.id}.pdf",
            "type": "application/pdf",
        })

    # CUSTOMER MAIL
    customer_html = render_to_string(
        "emails/order_success.html",
        {"order": order}
    )

    if order.email:
        send_brevo_email(
            subject=f"Order Confirmed - #{order.id}",
            html_content=customer_html,
            to_emails=[order.email],
            attachments=attachments
        )

    # ADMIN COPY
    admin_html = f"""
        <h3>New Paid Order</h3>
        <p>Order ID: {order.id}</p>
        <p>Name: {order.name}</p>
        <p>Mobile: {order.mobile}</p>
        <p>Total: INR {order.total_amount}</p>
    """

    admin_email = getattr(settings, "ADMIN_EMAIL", "support@rcshop.co.in")

    if admin_email:
        send_brevo_email(
            subject=f"New Paid Order - #{order.id}",
            html_content=admin_html,
            to_emails=[admin_email],
            attachments=attachments
        )


# ===============================
# SUPPORT TICKET MAIL
# ===============================
def send_support_ticket_email(ticket):

    attachments = []

    try:
        if ticket.photo:
            attachments.append({
                "content": base64.b64encode(ticket.photo.read()).decode(),
                "name": ticket.photo.name,
                "type": "image/jpeg"
            })
    except Exception as e:
        print("Attachment Error:", e)

    html = f"""
        <h3>New Support Ticket</h3>
        <p>Ticket ID: {ticket.ticket_id}</p>
        <p>Name: {ticket.name}</p>
        <p>Phone: {ticket.phone}</p>
        <p>Email: {ticket.email}</p>
        <p>Issue: {ticket.issue_type}</p>
        <p>Message: {ticket.message}</p>
    """

    admin_email = getattr(settings, "ADMIN_EMAIL", "support@rcshop.co.in")

    send_brevo_email(
        subject=f"Support Ticket - {ticket.ticket_id}",
        html_content=html,
        to_emails=[admin_email],
        attachments=attachments
    )


# ===============================
# SIGNALS COMPATIBILITY FUNCTIONS
# ===============================

def send_order_emails(order, admin_email=None):
    """
    Used by signals.py
    """
    send_invoice_mail(order)


# ===============================
# PLACEHOLDER NOTIFICATION FUNCTIONS
# ===============================

def send_sms(mobile, message):
    """
    Placeholder SMS function
    """
    print(f"SMS to {mobile}: {message}")
    return True


def send_whatsapp(mobile, message):
    """
    Placeholder WhatsApp function
    """
    print(f"WhatsApp to {mobile}: {message}")
    return True


# ===============================
# OTP PLACEHOLDER FUNCTIONS
# ===============================

def send_sms_otp(mobile, otp):
    print(f"Sending SMS OTP {otp} to {mobile}")
    return True


def send_whatsapp_otp(mobile, otp):
    print(f"Sending WhatsApp OTP {otp} to {mobile}")
    return True
