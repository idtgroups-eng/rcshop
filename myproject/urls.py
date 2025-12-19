from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path("admin/", admin.site.urls),

    # ================= BASIC PAGES =================
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("products/", views.products, name="products"),
    path("product_details/", views.product_details, name="product_details"),
    path("contact/", views.contact, name="contact"),
    path("cart/", views.cart, name="cart"),
    path("checkout/", views.checkout, name="checkout"),

    # ================= SUPPORT PAGES =================
    path("return-policy/", views.return_policy, name="return_policy"),  # ✅ ADDED
    path("return-request/", views.return_request, name="return_request"),
    path("order-tracking/", views.order_tracking, name="order_tracking"),
    path("shipping-policy/", views.shipping_policy, name="shipping_policy"),
    path("help-center/", views.help_center, name="help_center"),

    # ================= PAYMENT FLOW =================
    path("payment/", views.payment, name="payment"),
    path("payment/upi/", views.payment_upi, name="payment_upi"),
    path("payment/online/", views.payment_online, name="payment_online"),

    # ================= COD FLOW =================
    path("payment/cod/", views.cod_details, name="cod_details"),

    # ================= SUCCESS & INVOICE =================
    path("thankyou/", views.thankyou, name="thankyou"),
    path("invoice/", views.invoice, name="invoice"),

    # ================= API =================
    path("api/checkout/", views.api_checkout, name="api_checkout"),
    path(
        "googlea564d4978a897b47.html",
        TemplateView.as_view(template_name="googlea564d4978a897b47.html"),
    ),
]
