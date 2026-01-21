from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            'home',
            'about',
            'products',
            'contact',
            'cart',
            'checkout',
            'return_policy',
            'return_request',
            'order_tracking',
            'shipping_policy',
            'help_center',
        ]

    def location(self, item):
        return reverse(item)
