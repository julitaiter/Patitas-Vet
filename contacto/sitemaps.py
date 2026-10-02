from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class ContactoSitemap(Sitemap):
    protocol = "https"
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return ("contacto:index",)

    def location(self, item):
        return reverse(item)
