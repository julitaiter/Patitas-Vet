from django.urls import NoReverseMatch, reverse


def build_absolute_detail_url(request, url_name, pk):
    """Devuelve la URL absoluta de una vista web si existe."""
    try:
        path = reverse(url_name, kwargs={"pk": pk})
    except NoReverseMatch:
        return None

    if request is None:
        return path
    return request.build_absolute_uri(path)
