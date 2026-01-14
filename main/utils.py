import base64
import requests
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string
from fpdf import FPDF


BREVO_API_KEY = settings.BREVO_API_KEY
BREVO_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "support@rcshop.co.in")


# ===============================
# PDF INVOICE GENERATOR (Railway Safe)
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
    pdf.cell(0, 8, f"Total Amount: ₹{order.total_amount}", ln=True)
    pdf.ln(8)

    pdf.multi_cell(0, 8, "Thank you for shopping with RCShop.\nYour order has been successfully placed.")

    buffer = BytesIO()
    pdf.output(buffer)
    buffer.seek(0)
    return buffer.read()


# ===============================
# BREVO EMAIL SENDER
# ===============================
def send_brevo_email(subject, html_content, to_emails, attachments=None):

    if not BREVO_API_KEY:
        return

    url = "https://api.brevo.com/v3/smtp/email"

    payload = {
        "sender": {"name": "RCStore", "email": BREVO_FROM_EMAIL},
        "to": [{"email": e} for e in to_emails],
        "subject": subject,
        "htmlContent": html_content,
    }

    if attachments:
        payload["attachment"] = attachments

    headers = {
        "api-key": BREVO_API_KEY,
        "content-type": "application/json"
    }

    requests.post(url, json=payload, headers=headers, timeout=10)


# ===============================
# ORDER INVOICE MAIL
# ===============================
def send_invoice_mail(order):

    pdf_bytes = generate_invoice_pdf(order)

    attachments = [{
        "content": base64.b64encode(pdf_bytes).decode(),
        "name": f"Invoice_RC{order.id}.pdf",
        "type": "application/pdf",
    }]

    # CUSTOMER MAIL
    customer_html = render_to_string("emails/order_success.html", {"order": order})

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
        <p>Total: ₹{order.total_amount}</p>
    """

    send_brevo_email(
        subject=f"New Paid Order - #{order.id}",
        html_content=admin_html,
        to_emails=[settings.ADMIN_EMAIL],
        attachments=attachments
    )


# ===============================
# SUPPORT TICKET MAIL
# ===============================
def send_support_ticket_email(ticket):

    attachments = []

    if ticket.photo:
        attachments.append({
            "content": base64.b64encode(ticket.photo.read()).decode(),
            "name": ticket.photo.name,
            "type": "image/jpeg"
        })

    html = f"""
        <h3>New Support Ticket</h3>
        <p>Ticket ID: {ticket.ticket_id}</p>
        <p>Name: {ticket.name}</p>
        <p>Phone: {ticket.phone}</p>
        <p>Email: {ticket.email}</p>
        <p>Issue: {ticket.issue_type}</p>
        <p>Message: {ticket.message}</p>
    """

    send_brevo_email(
        subject=f"Support Ticket - {ticket.ticket_id}",
        html_content=html,
        to_emails=[settings.ADMIN_EMAIL],
        attachments=attachments
    )
