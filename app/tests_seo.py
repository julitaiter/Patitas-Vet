from decimal import Decimal
from xml.etree import ElementTree

from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import TestCase
from django.urls import reverse

from .models import Categoria, Producto, Servicio


class SeoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        Site.objects.update_or_create(pk=1, defaults={"domain": "jtaiter.com", "name": "Patitas Vet"})
        Site.objects.clear_cache()
        categoria = Categoria.objects.create(nombre="Mascotas")
        cls.producto = Producto.objects.create(
            nombre="Alimento premium", descripcion="Alimento saludable para mascotas",
            precio=Decimal("1000"), categoria=categoria, activo=True,
        )
        cls.producto_inactivo = Producto.objects.create(
            nombre="Producto oculto", descripcion="No publicar",
            precio=Decimal("500"), categoria=categoria, activo=False,
        )
        cls.servicio = Servicio.objects.create(
            nombre="Consulta veterinaria", descripcion="Atención para tu mascota",
            precio=Decimal("2000"), categoria=categoria, activo=True,
        )
        cls.servicio_inactivo = Servicio.objects.create(
            nombre="Servicio oculto", descripcion="No publicar",
            precio=Decimal("500"), categoria=categoria, activo=False,
        )

    @classmethod
    def tearDownClass(cls):
        Site.objects.clear_cache()
        super().tearDownClass()

    def test_robots_txt_usa_dominio_del_site_y_bloquea_privadas(self):
        response = self.client.get(reverse("robots_txt"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        body = response.content.decode()
        self.assertIn("User-agent: *", body)
        self.assertIn("Sitemap: https://jtaiter.com/sitemap.xml", body)
        for ruta in ("/admin/", "/accounts/", "/checkout/", "/mis-pedidos/", "/empleado/", "/api/"):
            self.assertIn(f"Disallow: {ruta}", body)
        self.assertNotIn("Disallow: /catalogo/\n", body)

    def test_sitemap_xml_solo_contiene_paginas_publicas_activas(self):
        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/xml"))
        root = ElementTree.fromstring(response.content)
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {node.text for node in root.findall("s:url/s:loc", namespace)}
        dominio = "https://jtaiter.com"
        for ruta in (reverse("index"), reverse("listar_catalogo"), reverse("contacto:index"),
                     reverse("detalle_producto", args=[self.producto.pk]),
                     reverse("detalle_servicio", args=[self.servicio.pk])):
            self.assertIn(dominio + ruta, urls)
        self.assertNotIn(dominio + reverse("detalle_producto", args=[self.producto_inactivo.pk]), urls)
        self.assertNotIn(dominio + reverse("detalle_servicio", args=[self.servicio_inactivo.pk]), urls)
        for url in urls:
            for privada in ("/admin/", "/checkout/", "/mis-pedidos/", "/mi-perfil/", "/empleado/", "/api/"):
                self.assertNotIn(privada, url)
        self.assertEqual(len(urls), 5)

    def test_metadatos_publicos_y_detalle_dinamico(self):
        home = self.client.get(reverse("index"))
        self.assertContains(home, '<meta charset="utf-8">')
        self.assertContains(home, 'name="viewport"')
        self.assertContains(home, 'name="description"')
        self.assertContains(home, 'name="author"')
        self.assertContains(home, 'content="index, follow"')
        detalle = self.client.get(reverse("detalle_producto", args=[self.producto.pk]))
        self.assertContains(detalle, self.producto.descripcion)
        self.assertContains(detalle, self.producto.nombre)
        self.assertContains(self.client.get(reverse("contacto:index")), "contacto veterinaria")

    def test_paginas_privadas_muestran_noindex(self):
        user = get_user_model().objects.create_user(username="cliente-seo", password="clave-seo")
        self.client.force_login(user)
        for nombre in ("mi_perfil", "checkout", "mis_pedidos"):
            self.assertContains(self.client.get(reverse(nombre)), 'content="noindex, nofollow"')
        self.client.logout()
        self.assertContains(self.client.get(reverse("account_login")), 'content="noindex, nofollow"')
