from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaymentProof, Order
from .utils import send_order_emails, send_sms, send_whatsapp


@receiver(post_save, sender=PaymentProof)
def auto_confirm_after_payment(sender, instance, **kwargs):
    if instance.verified:
        try:
            order = Order.objects.get(id=instance.order_id)

            # Update order status
            order.status = "Confirmed"
            order.payment_method = "UPI"
            order.save()

            # Send Email
            send_order_emails(order, admin_email="support@rcshop.co.in")

            # Send SMS
            send_sms(
                order.mobile,
                f"RCShop: Payment for Order #{order.id} verified. Invoice emailed."
            )

            # Send WhatsApp
            send_whatsapp(
                order.mobile,
                f"RCShop: Payment received for Order #{order.id}. Your order is confirmed. Thank you!"
            )

        except Exception as e:
            print("❌ Auto confirm error:", e)
