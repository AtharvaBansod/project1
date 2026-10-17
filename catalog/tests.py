import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from .models import Brand, Category, Product

MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=MEDIA)
class ProductAdminTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.login(username="admin", password=settings.SEED_PASSWORD)
        self.brand = Brand.objects.first()
        self.category = Category.objects.first()

    def add_page_text(self):
        return self.client.get("/admin/catalog/product/add/").content.decode()

    def test_add_page_shows_compatibility_specs_and_documents(self):
        html = self.add_page_text()
        for text in ("Compatible spare parts", "Compatible machines", "Specifications", "Datasheets and manuals"):
            self.assertIn(text, html)

    def test_add_machine_with_parts_spec_and_datasheet(self):
        parts = list(Product.objects.filter(kind="spare")[:2])
        data = {
            "kind": "machine", "name": "Test Press", "slug": "test-press", "sku": "TP-100",
            "brand": self.brand.pk, "category": self.category.pk, "stock_status": "in_stock",
            "stock_qty": 1, "lead_time_days": 0, "compatible_parts": [p.pk for p in parts],
            "specs-TOTAL_FORMS": 1, "specs-INITIAL_FORMS": 0, "specs-MIN_NUM_FORMS": 0, "specs-MAX_NUM_FORMS": 1000,
            "specs-0-name": "Power", "specs-0-value": "5 kW",
            "documents-TOTAL_FORMS": 1, "documents-INITIAL_FORMS": 0, "documents-MIN_NUM_FORMS": 0, "documents-MAX_NUM_FORMS": 1000,
            "documents-0-doc_type": "datasheet", "documents-0-title": "Test Press Datasheet",
            "documents-0-file": SimpleUploadedFile("tp.pdf", b"%PDF-1.4"),
        }
        response = self.client.post("/admin/catalog/product/add/", data)
        self.assertEqual(response.status_code, 302, getattr(response, "context", None) and response.context["adminform"].form.errors)
        machine = Product.objects.get(sku="TP-100")
        self.assertEqual(set(machine.compatible_parts.all()), set(parts))
        self.assertEqual(machine.specs.count(), 1)
        self.assertEqual(machine.documents.count(), 1)
        edit_html = self.client.get(f"/admin/catalog/product/{machine.pk}/change/").content.decode()
        self.assertIn(parts[0].name, edit_html)

    def test_add_spare_part_with_compatible_machine(self):
        machine = Product.objects.filter(kind="machine").first()
        data = {
            "kind": "spare", "name": "Test Seal", "slug": "test-seal", "sku": "TS-1",
            "brand": self.brand.pk, "category": self.category.pk, "stock_status": "in_stock",
            "stock_qty": 5, "lead_time_days": 0, "compatible_machines": [machine.pk],
            "specs-TOTAL_FORMS": 0, "specs-INITIAL_FORMS": 0, "specs-MIN_NUM_FORMS": 0, "specs-MAX_NUM_FORMS": 1000,
            "documents-TOTAL_FORMS": 0, "documents-INITIAL_FORMS": 0, "documents-MIN_NUM_FORMS": 0, "documents-MAX_NUM_FORMS": 1000,
        }
        self.assertEqual(self.client.post("/admin/catalog/product/add/", data).status_code, 302)
        self.assertIn(machine, Product.objects.get(sku="TS-1").compatible_machines.all())
