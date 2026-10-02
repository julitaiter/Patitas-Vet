import base64
from tempfile import TemporaryDirectory

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import resolve, reverse
from django.core.files.uploadedfile import SimpleUploadedFile

from .models import PreguntaFrecuente


class PreguntasFrecuentesTests(TestCase):
    def test_modelo_seeds_y_orden(self):
        self.assertEqual(PreguntaFrecuente.objects.count(), 6)
        faq = PreguntaFrecuente.objects.first()
        self.assertEqual(str(faq), faq.pregunta)
        self.assertEqual(faq.orden, 1)
        self.assertIsInstance(PreguntaFrecuente._meta.get_field("contenido"), RichTextUploadingField)
        PreguntaFrecuente.objects.create(
            pregunta="Pregunta prioritaria", descripcion="Descripción interna",
            contenido="<p>Respuesta</p>", orden=0,
        )
        self.assertEqual(PreguntaFrecuente.objects.first().pregunta, "Pregunta prioritaria")

    def test_vista_publica_muestra_solo_activos_colapsados(self):
        PreguntaFrecuente.objects.create(
            pregunta="Pregunta oculta", descripcion="No publicar",
            contenido="<p>Contenido oculto</p>", activo=False,
        )
        response = self.client.get(reverse("preguntas_frecuentes"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "¿Cómo solicito un turno?")
        self.assertNotContains(response, "Pregunta oculta")
        self.assertContains(response, 'data-bs-toggle="collapse"')
        self.assertContains(response, 'aria-expanded="false"')
        self.assertContains(response, 'aria-controls="faq-respuesta-')
        self.assertContains(response, 'class="collapse"')
        self.assertContains(response, 'col-12 col-md-6 col-xl-4')
        self.assertContains(response, 'name="description"')
        self.assertContains(response, reverse("preguntas_frecuentes"))

    def test_sitemap_incluye_faq(self):
        response = self.client.get(reverse("sitemap"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("preguntas_frecuentes"))

    def test_uploader_tiene_url_y_requiere_staff(self):
        self.assertEqual(resolve("/ckeditor/upload/").url_name, "ckeditor_upload")
        self.assertEqual(self.client.get("/ckeditor/browse/").status_code, 302)
        self.assertEqual(self.client.post("/ckeditor/upload/").status_code, 302)

    def test_admin_renderiza_editor_para_contenido(self):
        admin = get_user_model().objects.create_superuser(
            username="admin-faq", password="clave-segura", email="admin-faq@example.com",
        )
        self.client.force_login(admin)
        response = self.client.get(reverse("admin:app_preguntafrecuente_add"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="contenido"')
        self.assertContains(response, "ckeditor")

    def test_staff_sube_imagen_a_media_uploads(self):
        user = get_user_model().objects.create_user(username="editor-faq", password="clave-segura", is_staff=True)
        self.client.force_login(user)
        png = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/lXcAAAAASUVORK5CYII=")
        with TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
            response = self.client.post("/ckeditor/upload/", {
                "upload": SimpleUploadedFile("faq.png", png, content_type="image/png"),
            })
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["uploaded"], "1")
            self.assertIn("/media/uploads/", response.json()["url"])
