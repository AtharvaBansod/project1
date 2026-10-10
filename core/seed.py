from django.conf import settings
from django.core.files.base import ContentFile

from accounts.models import BuyerProfile, User
from catalog.models import Brand, Category, Document, Product, Specification
from core.models import FAQ, TeamMember


def tiny_pdf(title):
    """Build a minimal valid one-page PDF containing the title."""
    text = title.replace("(", "").replace(")", "")
    stream = f"BT /F1 20 Tf 60 740 Td ({text}) Tj ET"
    objs = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        "/Resources << /Font << /F1 5 0 R >> >> >>",
        f"<< /Length {len(stream)} >>\nstream\n{stream}\nendstream",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = "%PDF-1.4\n"
    offsets = []
    for i, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n{o}\nendobj\n"
    xref = len(out)
    out += f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n"
    out += "".join(f"{off:010d} 00000 n \n" for off in offsets)
    out += f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return out.encode("latin-1")


CATEGORIES = [
    ("CNC & Machining", "bi-cpu", "Lathes, mills, machining centres"),
    ("Compressors", "bi-wind", "Screw and piston air compressors"),
    ("Pumps & Hydraulics", "bi-droplet", "Industrial pumps and power packs"),
    ("Packaging", "bi-box-seam", "Filling, sealing and wrapping lines"),
    ("Power Tools", "bi-tools", "Heavy duty industrial tools"),
    ("Bearings & Drives", "bi-gear", "Bearings, belts, gearboxes"),
]
BRANDS = [("Haas-Tek", "USA"), ("Kraftwerk", "Germany"), ("Sumida", "Japan"), ("Nordpump", "Sweden"), ("TianGong", "China")]

# kind, name, sku, brand, category, summary, price, stock, qty, lead, featured, specs
PRODUCTS = [
    ("machine", "VMC-850 Vertical Machining Centre", "HT-VMC850", "Haas-Tek", "CNC & Machining",
     "3-axis vertical machining centre with 24-tool changer.", 48500, "in_stock", 3, 0, True,
     [("Travel X/Y/Z", "850 / 510 / 510 mm"), ("Spindle speed", "12,000 rpm"), ("Tool magazine", "24 tools"), ("Power", "15 kW, 400 V")]),
    ("machine", "TL-200 CNC Turning Lathe", "SU-TL200", "Sumida", "CNC & Machining",
     "Slant-bed CNC lathe for high-precision turning.", 36900, "on_order", 0, 45, True,
     [("Swing over bed", "420 mm"), ("Max turning length", "500 mm"), ("Spindle bore", "62 mm"), ("Power", "11 kW")]),
    ("machine", "GA-37 Screw Compressor", "KW-GA37", "Kraftwerk", "Compressors",
     "37 kW oil-injected rotary screw compressor with VSD.", 21800, "in_stock", 5, 0, True,
     [("Motor power", "37 kW"), ("Free air delivery", "6.9 m3/min"), ("Working pressure", "8 bar"), ("Noise level", "69 dB(A)")]),
    ("machine", "CP-500 Centrifugal Pump", "NP-CP500", "Nordpump", "Pumps & Hydraulics",
     "Stainless steel centrifugal pump for process fluids.", 3200, "low", 2, 14, False,
     [("Flow rate", "500 L/min"), ("Head", "55 m"), ("Material", "SS316"), ("Motor", "7.5 kW")]),
    ("machine", "FM-60 Auto Filling Machine", "TG-FM60", "TianGong", "Packaging",
     "Automatic liquid filling line, up to 60 bottles per minute.", None, "on_order", 0, 60, True,
     [("Speed", "60 bpm"), ("Fill range", "100-1000 ml"), ("Heads", "8"), ("Power", "3 kW")]),
    ("machine", "HP-40 Hydraulic Power Pack", "NP-HP40", "Nordpump", "Pumps & Hydraulics",
     "Compact hydraulic power unit, 40 L tank.", 2750, "in_stock", 8, 0, False,
     [("Tank capacity", "40 L"), ("Pressure", "250 bar"), ("Motor", "4 kW")]),
    ("machine", "AG-230 Heavy Angle Grinder", "KW-AG230", "Kraftwerk", "Power Tools",
     "2400 W industrial angle grinder, 230 mm disc.", 189, "in_stock", 60, 0, False,
     [("Power", "2400 W"), ("Disc", "230 mm"), ("No-load speed", "6,500 rpm")]),
    ("spare", "Main Spindle Bearing Set", "HT-SB850", "Haas-Tek", "Bearings & Drives",
     "Matched angular contact bearing set for VMC-850 spindle.", 640, "in_stock", 12, 0, False,
     [("Type", "Angular contact, P4"), ("Bore", "70 mm"), ("Qty per set", "4")]),
    ("spare", "Air-Oil Separator Element", "KW-AOS37", "Kraftwerk", "Compressors",
     "Replacement separator element for GA-37 compressors.", 210, "in_stock", 25, 0, False,
     [("Rated flow", "7 m3/min"), ("Service life", "4,000 h")]),
    ("spare", "Compressor Intake Filter Kit", "KW-IF37", "Kraftwerk", "Compressors",
     "Intake filter kit, includes element and seals.", 85, "low", 4, 10, False,
     [("Filtration", "3 micron"), ("Kit contents", "Element, gasket")]),
    ("spare", "Pump Mechanical Seal", "NP-MS500", "Nordpump", "Pumps & Hydraulics",
     "SiC/SiC mechanical seal for CP-500 pumps.", 142, "in_stock", 18, 0, False,
     [("Shaft size", "35 mm"), ("Material", "SiC / SiC")]),
    ("spare", "Lathe Chuck Jaw Set", "SU-CJ200", "Sumida", "CNC & Machining",
     "Hardened soft jaw set for TL-200 hydraulic chuck.", 175, "on_order", 0, 30, False,
     [("Chuck size", "8 inch"), ("Hardness", "HRC 58")]),
    ("spare", "Filling Nozzle Assembly", "TG-FN60", "TianGong", "Packaging",
     "Anti-drip filling nozzle for FM-60 machines.", None, "out", 0, 40, False,
     [("Material", "SS304"), ("Fit", "FM-60, 8 heads")]),
    ("spare", "Poly-V Drive Belt Pack", "KW-PV10", "Kraftwerk", "Bearings & Drives",
     "Pack of 3 drive belts for GA-series compressors.", 48, "in_stock", 40, 0, False,
     [("Profile", "PJ"), ("Length", "1,250 mm"), ("Pack", "3 pcs")]),
]
COMPAT = {
    "HT-SB850": ["HT-VMC850"], "KW-AOS37": ["KW-GA37"], "KW-IF37": ["KW-GA37"], "KW-PV10": ["KW-GA37"],
    "NP-MS500": ["NP-CP500"], "SU-CJ200": ["SU-TL200"], "TG-FN60": ["TG-FM60"],
}

FAQS = [
    ("How do I get a price?", "Open any product and choose Price enquiry. Our team replies with a formal quotation, usually within one business day."),
    ("Can I check if a part fits my machine?", "Yes. Use the Spare Part Compatibility enquiry or see the compatibility charts in the Technical library."),
    ("Do I need an account?", "No. Guests can browse, view datasheets and send enquiries. A buyer account adds saved products, enquiry history, service requests and manuals."),
    ("Who installs the machines?", "Our factory-trained technicians handle installation, commissioning and operator training. Submit a service request from your account."),
    ("What warranty do you offer?", "Machines carry a 12-24 month manufacturer warranty. Spare parts carry 6 months."),
]
TEAM = [
    ("Marta Keller", "Managing Director", "20 years in industrial equipment trading."),
    ("Rohan Mehta", "Head of Sourcing", "Manages manufacturer relations across Asia and Europe."),
    ("Elena Petrova", "Technical Lead", "Maintains our datasheet and compatibility library."),
    ("Samuel Okoye", "Service Manager", "Leads the installation and field service team."),
]



def run():
    DEMO_PASSWORD = settings.SEED_PASSWORD
    cats = {n: Category.objects.get_or_create(name=n, defaults={"icon": i, "description": d})[0] for n, i, d in CATEGORIES}
    brands = {n: Brand.objects.get_or_create(name=n, defaults={"country": c})[0] for n, c in BRANDS}
    by_sku = {}
    for kind, name, sku, brand, cat, summary, price, stock, qty, lead, feat, specs in PRODUCTS:
        p, created = Product.objects.get_or_create(sku=sku, defaults=dict(
            kind=kind, name=name, brand=brands[brand], category=cats[cat], summary=summary,
            description=f"{summary} Supplied with factory documentation and available with optional installation and training.",
            indicative_price=price, stock_status=stock, stock_qty=qty, lead_time_days=lead, is_featured=feat))
        by_sku[sku] = p
        if created:
            for n, v in specs:
                Specification.objects.create(product=p, name=n, value=v)
            ds = Document(product=p, doc_type="datasheet", title=f"{name} Datasheet")
            ds.file.save(f"{sku}-datasheet.pdf", ContentFile(tiny_pdf(f"{name} - Datasheet")), save=True)
            if kind == "machine":
                mn = Document(product=p, doc_type="manual", title=f"{name} Operation Manual")
                mn.file.save(f"{sku}-manual.pdf", ContentFile(tiny_pdf(f"{name} - Operation Manual")), save=True)
    for part, machines in COMPAT.items():
        by_sku[part].compatible_machines.set([by_sku[m] for m in machines])

    for i, (q, a) in enumerate(FAQS):
        FAQ.objects.get_or_create(question=q, defaults={"answer": a, "order": i})
    for i, (n, r, b) in enumerate(TEAM):
        TeamMember.objects.get_or_create(name=n, defaults={"role": r, "bio": b, "order": i})

    if not User.objects.filter(username="admin").exists():
        User.objects.create_superuser("admin", "admin@industrolink.example", DEMO_PASSWORD, first_name="Site", last_name="Admin")
    if not User.objects.filter(username="buyer").exists():
        u = User.objects.create_user("buyer", "buyer@industrolink.example", DEMO_PASSWORD,
                                     first_name="Priya", last_name="Nair", role="buyer", phone="+91 98765 43210")
        BuyerProfile.objects.create(user=u, company_name="Nair Precision Works", industry="Manufacturing",
                                    address="Plot 14, MIDC Industrial Area", city="Pune", country="India")
    if not User.objects.filter(username="technician").exists():
        User.objects.create_user("technician", "tech@industrolink.example", DEMO_PASSWORD,
                                 first_name="Tom", last_name="Becker", role="technician")
