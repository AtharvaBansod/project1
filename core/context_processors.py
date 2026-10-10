from django.conf import settings


def site(request):
    return {
        "SITE_NAME": settings.SITE_NAME,
        "NAV_LINKS": [
            ("Home", "core:home"),
            ("Products", "catalog:list"),
            ("Enquiry", "enquiries:create"),
            ("Technical", "catalog:technical"),
            ("Services", "services:list"),
            ("About", "core:about"),
            ("Contact", "core:contact"),
        ],
    }
