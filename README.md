# IndustroLink

Django project (Django 5.2, SQLite, Bootstrap 5 via CDN).

## Requirements

- Python 3.10 or newer
- pip
- Internet access in the browser (Bootstrap and icons load from a CDN)

## Installation

Windows (PowerShell):

    git clone https://github.com/AtharvaBansod/project1.git
    cd project1
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    copy .env.example .env
    python manage.py migrate

Linux / macOS:

    git clone https://github.com/AtharvaBansod/project1.git
    cd project1
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cp .env.example .env
    python3 manage.py migrate

`migrate` creates the database and automatically creates the default users and
sample data listed below. Running it again does not duplicate anything.

## Running

    python manage.py runserver

Open http://127.0.0.1:8000/ in a browser.
Admin panel: http://127.0.0.1:8000/admin/

## Configuration (.env)

| Variable | Purpose | Default |
|---|---|---|
| DJANGO_SECRET_KEY | Django secret key. Change it for any real deployment. | dev key |
| DJANGO_DEBUG | Debug mode (True / False) | True |
| DJANGO_ALLOWED_HOSTS | Comma separated host names | localhost,127.0.0.1 |
| DATABASE_PATH | Custom SQLite file location | db.sqlite3 in project root |
| SEED_ON_MIGRATE | Create default users and sample data after migrate | True |
| SEED_PASSWORD | Password given to the default users | password@123 |

Settings modules: `config/settings/base.py`, `development.py` (used by manage.py),
`production.py` (used by wsgi.py / asgi.py).

To load the sample data manually: `python manage.py seed_demo`

## Default users

| Role | Username | Password |
|---|---|---|
| Admin | admin | password@123 |
| Buyer | buyer | password@123 |
| Technician | technician | password@123 |

Sign in at http://127.0.0.1:8000/accounts/login/
Change these passwords before using the project anywhere other than a local machine.

## Roles and functionality

### Guest (not signed in)
- Browse machines and spare parts, filter by brand and category, search
- View product details, specifications and stock status
- Download datasheets
- Send Price Enquiry, Availability Check and Spare Part Compatibility enquiries
- Read Services, About, Contact (contact form and FAQ)
- Register a buyer account

### Buyer
- Company profile and password change
- Save and remove products
- Enquiry history with admin responses and quotation downloads
- Create service requests (installation, maintenance, warranty, training) and track status
- Download manuals

### Technician
- View service requests assigned to them, filter by status
- Update status (assigned, in progress, completed) and add notes

### Admin
Uses the Django admin panel at /admin/:
- Products: details, price, stock status and quantity, images, specifications, datasheets, manuals, compatible machines
- Brands and categories
- Enquiries: inbox, status, written response, quotation upload
- Service requests: assign technicians, change status
- Technicians: add and manage technician accounts
- Users: all accounts and roles
- FAQs, team members, contact form messages

## Screens

| Screen | URL |
|---|---|
| Home | / |
| Products | /products/ |
| Product details | /products/<slug>/ |
| Technical (datasheets, manuals, compatibility) | /products/technical/ |
| Enquiry | /enquiry/ |
| Services | /services/ |
| About | /about/ |
| Contact | /contact/ |
| Sign in / Register | /accounts/login/, /accounts/register/ |
| Buyer dashboard | /accounts/dashboard/ |
| Company profile | /accounts/profile/ |
| Saved products | /products/saved/ |
| Enquiry history | /enquiry/history/ |
| Service requests (buyer) | /services/my-requests/ |
| New service request | /services/request/ |
| Technician assignments | /services/technician/ |
| Admin panel | /admin/ |

## Project structure

    config/        settings, urls, wsgi/asgi
    accounts/      users, roles, buyer profile, login/register
    catalog/       brands, categories, products, documents, saved products
    enquiries/     enquiries and quotations
    services/      service requests, technician screens
    core/          home, about, contact, FAQ, team, seed data
    templates/     base layout, header, footer, error pages
    static/        css and images

## Where to change content

| What | Where |
|---|---|
| Products, stock, images, documents, brands, categories, FAQs, team | Admin panel |
| Site name | SITE_NAME in config/settings/base.py |
| Menu links | NAV_LINKS in core/context_processors.py |
| Header and footer | templates/partials/header.html, footer.html |
| Colours and styling | static/css/site.css |
| Home hero image | static/img/hero-unsplash.jpg |
| Page text | core/templates/core/ (home, about, contact) |
| Services list | SERVICES in services/views.py |
| Sample data | core/seed.py |
