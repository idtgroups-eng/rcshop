from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.models import User
from django.http import HttpResponse

from main import views
from main.sitemaps import StaticViewSitemap


# ================= TEMP LIVE ADMIN CREATOR =================
def create_live_admin(request):
    if User.objects.filter(username="admin").exists():
        return HttpResponse("Admin already exists")

    User.objects.create_superuser(
        username="admin",
        email="admin@rcshop.co.in",
        password="Admin@123"
    )
    return HttpResponse("Live admin created")


urlpatterns = [

    # ================= ADMIN =================
    path("admin/", admin.site.urls),

    # ================= BASIC PAGES =================
    path("", views.index, name="home"),
    path("about/", views.about, name="about"),
    path("products/", views.products, name="products"),
    path("product_details/", views.product_details, name="product_details"),
    path("contact/", views.contact, name="contact"),
    path("cart/", views.cart, name="cart"),
    path("return-policy/", views.return_policy, name="return_policy"),
    path("return-request/", views.return_request, name="return_request"),
    path("website-policy/", views.website_policy, name="website_policy"),
    path("railway-ping/", views.railway_ping),

    # ================= LIVE ADMIN CREATOR =================
    path("create-live-admin/", create_live_admin),

    # ================= SERVICES =================
    path("computer-sales/", views.computer_sales, name="computer_sales"),
    path("repair-maintenance/", views.repair_maintenance, name="repair_maintenance"),
    path("printer-toner/", views.printer_toner, name="printer_toner"),
    path("cctv-fitting/", views.cctv_fitting, name="cctv_fitting"),
    path("lokmitra-services/", views.lokmitra_services, name="lokmitra_services"),
    path("hp-retailer/", views.hp_retailer, name="hp_retailer"),

    # ================= SUPPORT =================
    path("support/", views.support, name="support"),
    path("track-ticket/", views.track_ticket, name="track_ticket"),

    # ================= CHECKOUT =================
    path("checkout/", views.checkout, name="checkout"),

    # ================= PAYMENT FLOW =================
    path("payment/", views.payment, name="payment"),
    path("create-order/", views.create_razorpay_order, name="create_razorpay_order"),
    path("razorpay-success/", views.razorpay_success, name="razorpay_success"),
    path("payment/cod/", views.cod_details, name="cod_details"),

    # ================= ORDER SUCCESS =================
    path("thankyou/", views.thankyou, name="thankyou"),

    # ================= USER ACCOUNT =================
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html", redirect_authenticated_user=True), name="login"),
    path("logout/", views.logout_user, name="logout"),
    path("logout-success/", views.logout_page, name="logout_page"),
    path("account/", views.my_account, name="my_account"),
    path("my-orders/", views.my_orders, name="my_orders"),
    path("order/<int:order_id>/", views.order_detail, name="order_detail"),

    # ================= ADMIN DASHBOARD =================
    path("dashboard/orders/", views.admin_orders, name="admin_orders"),
    path("dashboard/order/<int:order_id>/status/", views.update_order_status, name="update_order_status"),

    # ================= GOOGLE VERIFY =================
    path("googlea56d4978a897b47.html", TemplateView.as_view(template_name="googlea56d4978a897b47.html")),
]

# ================= SITEMAP =================
sitemaps = {"static": StaticViewSitemap}
urlpatterns += [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

# ================= PASSWORD RESET =================
urlpatterns += [
    path("password-reset/", auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="password_reset"),
    path("password-reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="password_reset_done.html"), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_confirm.html"), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_complete.html"), name="password_reset_complete"),
]

# ================= STATIC & MEDIA =================
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
