import shutil
import tempfile

from django.conf import settings
from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings

from accounts.models import User
from catalog.models import Product
from core.models import ContactMessage
from enquiries.models import Enquiry
from services.models import ServiceRequest

MEDIA = tempfile.mkdtemp()


def login(username):
    client = Client()
    assert client.login(username=username, password=settings.SEED_PASSWORD)
    return client


@override_settings(MEDIA_ROOT=MEDIA)
class ManagerFlowTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA, ignore_errors=True)

    def setUp(self):
        self.admin = login("admin")
        self.buyer = login("buyer")
        self.technician = login("technician")
        self.product = Product.objects.first()

    def test_enquiry_reply_with_quotation(self):
        guest = Client()
        guest.post("/enquiry/", {"enquiry_type": "price", "product": self.product.pk, "quantity": 2,
                                 "name": "Guest", "email": "guest@example.com", "message": "Need a quote"})
        enquiry = Enquiry.objects.get(email="guest@example.com")
        self.assertContains(self.admin.get("/manage/enquiries/"), enquiry.reference)
        response = self.admin.post(f"/manage/enquiries/{enquiry.reference}/", {
            "status": "quoted", "admin_response": "Price attached",
            "quotation": SimpleUploadedFile("quote.pdf", b"%PDF-1.4 test")})
        self.assertEqual(response.status_code, 302)
        enquiry.refresh_from_db()
        self.assertEqual(enquiry.status, "quoted")
        self.assertTrue(enquiry.quotation)
        self.assertEqual(mail.outbox[-1].to, ["guest@example.com"])

    def test_buyer_sees_enquiry_reply(self):
        self.buyer.post("/enquiry/", {"enquiry_type": "availability", "product": self.product.pk, "quantity": 1,
                                      "name": "Priya", "email": "buyer@industrolink.example", "message": "In stock?"})
        enquiry = Enquiry.objects.get(user__username="buyer")
        self.admin.post(f"/manage/enquiries/{enquiry.reference}/", {"status": "in_progress", "admin_response": "Yes, in stock"})
        self.assertContains(self.buyer.get(f"/enquiry/history/{enquiry.reference}/"), "Yes, in stock")

    def test_service_request_assign_and_complete(self):
        self.buyer.post("/services/request/", {"service_type": "installation", "site_address": "Pune plant",
                                               "description": "Install lathe", "preferred_date": "2099-01-01"})
        service = ServiceRequest.objects.get()
        self.assertContains(self.admin.get("/manage/services/"), service.reference)
        self.assertContains(self.technician.get("/services/technician/?scope=open"), service.reference)
        technician = User.objects.get(username="technician")
        self.admin.post(f"/manage/services/{service.pk}/", {"technician": technician.pk, "status": "assigned"})
        self.assertContains(self.technician.get("/services/technician/"), service.reference)
        self.technician.post(f"/services/technician/{service.pk}/", {"status": "completed", "technician_notes": "Installed"})
        service.refresh_from_db()
        self.assertEqual(service.status, "completed")
        self.assertContains(self.buyer.get("/services/my-requests/"), "Installed")

    def test_technician_can_take_open_request(self):
        self.buyer.post("/services/request/", {"service_type": "training", "site_address": "Plant", "description": "Train"})
        service = ServiceRequest.objects.get()
        self.technician.post(f"/services/technician/{service.pk}/claim/")
        service.refresh_from_db()
        self.assertEqual(service.technician.username, "technician")
        self.assertEqual(service.status, "assigned")

    def test_contact_message_reply_and_resolve(self):
        self.buyer.post("/contact/", {"name": "Priya", "email": "buyer@industrolink.example",
                                      "subject": "Delivery time", "message": "How long?"})
        item = ContactMessage.objects.get()
        self.assertEqual(item.user.username, "buyer")
        self.assertContains(self.admin.get("/manage/messages/?state=open"), "Delivery time")
        self.admin.post(f"/manage/messages/{item.pk}/", {"reply": "About 6 weeks", "is_resolved": "on"})
        item.refresh_from_db()
        self.assertTrue(item.is_resolved)
        self.assertIsNotNone(item.replied_at)
        self.assertContains(self.buyer.get("/my-messages/"), "About 6 weeks")
        self.assertNotContains(self.admin.get("/manage/messages/?state=open"), "Delivery time")

    def test_manage_screens_are_admin_only(self):
        for client in (self.buyer, self.technician):
            self.assertEqual(client.get("/manage/").status_code, 403)
        self.assertEqual(Client().get("/manage/").status_code, 302)
        self.assertEqual(self.admin.get("/manage/").status_code, 200)
        self.assertEqual(self.admin.get("/accounts/dashboard/").headers["Location"], "/manage/")
