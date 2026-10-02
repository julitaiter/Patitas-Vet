from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include

from app.sitemaps import ProductoSitemap, ServicioSitemap, StaticViewSitemap
from contacto.sitemaps import ContactoSitemap
from .views import robots_txt


sitemaps = {
    "static": StaticViewSitemap,
    "productos": ProductoSitemap,
    "servicios": ServicioSitemap,
    "contacto": ContactoSitemap,
}

urlpatterns = [
    path("robots.txt", robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
    path('accounts/', include('allauth.urls')),
    path('captcha/', include('captcha.urls')),
    path('contacto/', include('contacto.urls')),
    path("api/v1/", include("api.urls", namespace="api")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
