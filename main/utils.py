from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from io import BytesIO

# Optional PDF support
try:
    from xhtml2pdf import pisa
except Exception:
    pisa = None


# ==============================
# PDF GENERATOR
# ==============================
def render_to_pdf_bytes(template_name, context=None):
    if not pisa:
        return None
    try:
        html = render_to_string(template_name, context or {})
        result = BytesIO()
        pisa.CreatePDF(html, dest=result)
        return result.getvalue()
    except Exception as e:
        print("PDF error:", e)
        return None


# ==============================
# GENERIC EMAIL SENDER
# ==============================
def send_email(subject, html_content, to_emails, attachments=None):
    email = EmailMessage(
        subject=subject,
        body=html_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=to_emails,
    )
    email.content_subtype = "html"

    if attachments:
        for att in attachments:
            email.attach(att["name"], att["content"], att["type"])

    email.send(fail_silently=False)
    return True


# ==============================
# ORDER EMAILS (CUSTOMER + ADMIN)
# ==============================
def send_order_emails(order, admin_email):

    order_id = order.id

    # ---------- PDF INVOICE ----------
    pdf_bytes = render_to_pdf_bytes("emails/invoice_pdf.html", {"order": order})

    attachments = []
    if pdf_bytes:
        attachments.append({
            "name": f"Invoice_{order_id}.pdf",
            "content": pdf_bytes,
            "type": "application/pdf",
        })

    # ---------- CUSTOMER EMAIL ----------
    customer_html = render_to_string("emails/order_success.html", {"order": order})

    send_email(
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

    send_email(
        subject=f"New Order - #{order_id}",
        html_content=admin_html,
        to_emails=[admin_email]
    )

    return True
