import base64
import requests
from io import BytesIO
from django.conf import settings
from django.template.loader import render_to_string

try:
    from xhtml2pdf import pisa
except:
    pisa = None


BREVO_API_KEY = settings.BREVO_API_KEY
BREVO_FROM_EMAIL = getattr(settings, "DEFAULT_FROM_EMAIL", "support@rcshop.co.in")


def render_to_pdf_bytes(template_name, context=None):
    if not pisa:
        return None

    html = render_to_string(template_name, context or {})
    result = BytesIO()
    pisa.CreatePDF(html, dest=result)
    return result.getvalue()


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


def send_invoice_mail(order):

    pdf = render_to_pdf_bytes("emails/invoice_pdf.html", {"order": order})
    attachments = []

    if pdf:
        attachments.append({
            "content": base64.b64encode(pdf).decode(),
            "name": f"Invoice_RC{order.id}.pdf",
            "type": "application/pdf",
        })

    # Customer
    customer_html = render_to_string("emails/order_success.html", {"order": order})
    send_brevo_email(
        subject=f"Order Confirmed - #{order.id}",
        html_content=customer_html,
        to_emails=[order.email],
        attachments=attachments
    )

    # Admin Copy
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
