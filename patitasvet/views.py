from django.contrib.sites.models import Site
from django.shortcuts import render
from django.views.decorators.http import require_GET


@require_GET
def robots_txt(request):
    site = Site.objects.get_current()
    return render(request, "robots.txt", {"domain": site.domain}, content_type="text/plain")
