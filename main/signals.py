from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PaymentProof, Order
from .utils import send_order_emails

@receiver(post_save, sender=PaymentProof)
def auto_confirm_after_payment(sender, instance, **kwargs):

    # Sirf jab verified TRUE ho
    if instance.verified:

        try:
            order = Order.objects.get(id=instance.order_id)

            # Order Confirm
            order.status = "Confirmed"
            order.payment_method = "UPI"
            order.save()

            # Auto Invoice + Email (Customer + Admin)
            send_order_emails(order, admin_email="support@rcshop.co.in")

        except Exception as e:
            print("❌ Auto confirm error:", e)
from .utils import send_order_emails, send_sms

@receiver(post_save, sender=PaymentProof)
def auto_confirm_after_payment(sender, instance, **kwargs):
    if instance.verified:
        order = Order.objects.get(id=instance.order_id)
        order.status = "Confirmed"
        order.payment_method = "UPI"
        order.save()

        send_order_emails(order, admin_email="support@rcshop.co.in")

        # 📱 SMS
        send_sms(order.mobile, f"RCShop: Your payment for Order #{order.id} is verified. Invoice has been emailed. Thank you!")

from .utils import send_order_emails, send_sms, send_whatsapp

@receiver(post_save, sender=PaymentProof)
def auto_confirm_after_payment(sender, instance, **kwargs):
    if instance.verified:
        order = Order.objects.get(id=instance.order_id)
        order.status = "Confirmed"
        order.payment_method = "UPI"
        order.save()

        send_order_emails(order, admin_email="support@rcshop.co.in")

        send_sms(order.mobile, f"RCShop: Payment for Order #{order.id} verified. Invoice emailed.")

        send_whatsapp(order.mobile, f"RCShop: Payment received for Order #{order.id}. Your order is confirmed. Thank you for shopping with us!")
