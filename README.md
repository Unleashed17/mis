# WINNIE HARDWARE — Inventory Management System

A full-stack inventory, sales and customer management system built for
**Winnie Hardware**, a hardware retail business in Kenya. Built with
Python (Flask), SQLite, and vanilla HTML/CSS/JavaScript.

## Features
- Secure login (bcrypt password hashing + server-side sessions)
- Two roles: **Administrator** and **Sales Attendant**, each with protected routes
- Product management (CRUD, categories, brand, unit of measure, low/out-of-stock detection)
- Stock receiving (increases quantity) and point-of-sale selling (decreases quantity)
- Stock can never go negative — oversells are blocked server-side
- Customer management
- Point-of-sale screen with cart, Cash / M-Pesa / Card payment
- Dashboard with live stats and a 7-day sales chart
- Reports: daily / weekly / monthly / custom sales, product sales, current inventory
- Input validation (Kenyan phone numbers, email, prices, quantities, duplicates)
- Responsive UI (desktop, tablet, mobile)

## Tech stack
- Backend: Python 3, Flask, SQLite3 (built into Python), bcrypt
- Frontend: HTML5, CSS3, vanilla JavaScript, Chart.js (via CDN, for the dashboard chart)

## Project structure
```
winnie-hardware/
├── app.py                 # Flask app entry point
├── config.py               # App configuration
├── database.py              # SQLite connection helper
├── schema.sql               # Database schema
├── init_db.py                # Creates tables + seed/admin data
├── requirements.txt
├── routes/
│   ├── auth.py              # Login / logout
│   ├── pages.py              # HTML page routes
│   ├── decorators.py          # @login_required / @roles_required
│   ├── validators.py           # Shared validation helpers
│   ├── api_products.py          # Products + categories API
│   ├── api_customers.py          # Customers API
│   ├── api_sales.py             # Sales / POS API (stock logic lives here)
│   ├── api_reports.py            # Dashboard stats + reports API
│   └── api_users.py              # User management API (admin only)
├── static/
│   ├── css/style.css
│   └── js/ (main.js, login.js, dashboard.js, products.js, customers.js, sales.js, reports.js, users.js)
├── templates/                 # Jinja2 HTML templates
└── database/                  # winnie_hardware.db is created here on first run
```

## KRA eTIMS integration

This system can submit sales to KRA's eTIMS (OSCU) system as fiscal tax
invoices. **This requires real KRA-issued credentials — it will not work
out of the box.** Before it can submit anything:

1. Register Winnie Hardware for eTIMS **OSCU** (Online Sales Control Unit)
   integration on the KRA eTIMS Taxpayer portal (itax.kra.go.ke → eTIMS →
   Service Request → select "OSCU"), and get KRA's approval.
2. Sign up separately at the eTIMS **sandbox** portal
   (https://etims-sbx.kra.go.ke) to get test credentials first. Never test
   against Production.
3. In this app, log in as admin and open the **KRA eTIMS** page in the
   sidebar. Enter your TIN (KRA PIN), Branch ID, and a device serial
   number you choose, then click **Activate Device with KRA** — this is a
   one-time call that exchanges your details for a communication key
   (`cmcKey`), which the app stores and reuses automatically after that.
4. Before a product can appear on a real eTIMS invoice, KRA requires it to
   be registered (classified) with them first. Use the **KRA eTIMS** page
   to register each product, or set its KRA Item Classification Code in
   the product's edit form if you need something more specific than the
   general-merchandise default.
5. Once products are registered and the device is active, every completed
   sale is automatically submitted to eTIMS in the background. The sale
   always completes locally first — eTIMS submission never blocks or
   fails a sale. If a submission fails (bad network, wrong credentials,
   etc.), it's marked `FAILED` and shown on the KRA eTIMS page with a
   **Resubmit** button, rather than being retried silently.

**Important honesty note:** `routes/etims_service.py` was built from KRA's
own published OSCU Specification Document (v2.0) and community reference
implementations, because real KRA sandbox credentials were not available
while building this. The server addresses
(`https://etims-api-sbx.kra.go.ke/etims-api` for sandbox,
`https://etims-api.kra.go.ke/etims-api` for production) and the device
activation path (`/selectInitOsdcInfo`) are confirmed from KRA's own
documents. Other paths/field names should be double-checked against the
official Postman collection KRA provides once you have sandbox access,
before relying on this for real tax filings. Test thoroughly in Sandbox
before ever switching Environment to Production.

## Default accounts (CHANGE BEFORE REAL USE)
| Role       | Username  | Password      |
|------------|-----------|---------------|
| Admin      | admin     | admin123      |
| Attendant  | attendant | attendant123  |

See the setup guide provided separately for how to run this in VS Code.
