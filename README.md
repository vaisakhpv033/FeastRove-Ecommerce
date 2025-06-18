# Feastrove – Multi-Vendor Food Ordering Platform

Feastrove is a comprehensive multi-vendor food ordering platform designed to connect customers with a variety of restaurants. It provides a seamless experience for users to discover local restaurants, browse menus, place orders, and make payments. The platform also offers dedicated dashboards for vendors to manage their menus, orders, and track sales, as well as an admin dashboard for overall platform management.

## Tech Stack

Feastrove is built with a robust and scalable tech stack:

*   **Backend:**
    *   Python
    *   Django
    *   PostgreSQL with PostGIS (for geospatial data)
    *   Gunicorn (for production deployment)
*   **Frontend:**
    *   HTML
    *   CSS
    *   Bootstrap
    *   JavaScript
    *   jQuery
    *   Ajax
*   **APIs & Services:**
    *   Google Maps API (for location services and autocomplete)
    *   Razorpay (payment gateway)
    *   PayPal (payment gateway)
    *   Google OAuth (for authentication)
*   **Deployment & Infrastructure:**
    *   AWS EC2
    *   Nginx
    *   Certbot (for SSL/TLS certificates)
*   **Other Tools:**
    *   `django-allauth` (for social authentication)
    *   `python-decouple` (for managing environment variables)
    *   `Pillow` (for image processing)
    *   `pdfkit` (for PDF generation)
    *   `psycopg2-binary` (PostgreSQL adapter)
    *   `virtualenv` (for environment isolation)

## Key Features

Feastrove offers a rich set of features for all user roles:

*   **Role-Based Access Control:**
    *   Separate interfaces and functionalities for Admins, Vendors, and Customers.
*   **Location-Based Services:**
    *   Restaurant search based on user's location using Google Maps API.
    *   Geospatial queries powered by GeoDjango and PostGIS.
*   **Vendor Management:**
    *   Vendor dashboard with menu builder (categories and food items).
    *   Order management (view orders, update status).
    *   Sales tracking and analytics (popular dishes, revenue reports, customer behavior).
    *   Dynamic business hours module.
*   **Customer Experience:**
    *   User-friendly interface for browsing restaurants and menus.
    *   Advanced cart operations with AJAX for a smooth experience.
    *   Order history and profile management.
    *   Wallet system for payments and refunds.
    *   Ability to mark favorite restaurants.
    *   Review and rating system for vendors.
*   **Admin Dashboard:**
    *   Platform performance monitoring.
    *   User management (customers and vendors).
    *   Vendor approval workflows.
*   **Payment & Authentication:**
    *   Secure payment processing with Razorpay and PayPal.
    *   Google OAuth for easy user authentication and registration.
*   **Order & Notifications:**
    *   Comprehensive order management system.
    *   Automated email notifications for order updates (e.g., order confirmation, status changes).
*   **Search & Discovery:**
    *   Smart search functionalities with Google Autocomplete.
*   **Promotions:**
    *   Coupon management system.

## Prerequisites

Before you begin, ensure you have the following software installed on your system:

*   **Python:** Version 3.8 or higher (as Django 5.1 is used).
*   **pip:** Python package installer (usually comes with Python).
*   **virtualenv:** (Recommended) For creating isolated Python environments.
    ```bash
    pip install virtualenv
    ```
*   **PostgreSQL:** The database used by the project.
*   **PostGIS:** The geospatial extension for PostgreSQL. Ensure this is enabled for your database.
*   **GDAL:** Geospatial Data Abstraction Library. This is a crucial dependency for GeoDjango. Installation methods vary by operating system:
    *   **Ubuntu/Debian:**
        ```bash
        sudo apt-get update
        sudo apt-get install gdal-bin libgdal-dev
        ```
    *   **macOS (using Homebrew):**
        ```bash
        brew install gdal
        ```
    *   **Windows:** This can be more complex. Consider using OSGeo4W installer or Windows Subsystem for Linux (WSL). Refer to the official GDAL and GeoDjango documentation for detailed instructions.
*   **Git:** For cloning the repository.

## Setup and Installation

Follow these steps to get the Feastrove platform running on your local machine:

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd feastrove 
    ```
    *(Replace `<repository_url>` with the actual URL of the Feastrove repository.)*

2.  **Create and Activate a Virtual Environment:**
    (Recommended to keep dependencies isolated)
    ```bash
    python -m venv env 
    # On Windows
    env\Scripts\activate
    # On macOS/Linux
    source env/bin/activate
    ```

3.  **Install Python Dependencies:**
    Navigate to the project root (where `requirements.txt` is located) and run:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure PostgreSQL Database:**
    *   Ensure PostgreSQL is running.
    *   Create a new PostgreSQL database. For example, named `feastrove_db`.
    *   Enable the PostGIS extension for the newly created database:
        ```sql
        CREATE EXTENSION postgis;
        ```
        You can run this command using `psql` or a database management tool like pgAdmin.

5.  **Set Up Environment Variables:**
    The project uses `python-decouple` to manage sensitive settings. Create a `.env` file in the project root directory (alongside `manage.py`). Add the following environment variables to this file, replacing the placeholder values with your actual credentials and settings:

    ```env
    SECRET_KEY=your_django_secret_key_here
    DEBUG=True

    # Database Configuration
    DB_NAME=feastrove_db
    DB_USER=your_db_user
    DB_PASSWORD=your_db_password
    DB_HOST=localhost # Or your DB host
    DB_PORT=5432 # Or your DB port

    # Email Configuration (Example for Gmail SMTP)
    EMAIL_HOST=smtp.gmail.com
    EMAIL_PORT=587
    EMAIL_HOST_USER=your_email@gmail.com
    EMAIL_HOST_PASSWORD=your_email_app_password
    DEFAULT_FROM_EMAIL=your_email@gmail.com

    # Google OAuth Configuration
    # These will be obtained from your Google Cloud Console
    SOCIALACCOUNT_PROVIDERS='{        "google": {            "APP": {                "client_id": "your_google_client_id",                "secret": "your_google_client_secret",                "key": ""            },            "SCOPE": ["profile", "email"],            "AUTH_PARAMS": {"access_type": "online"}        }    }'


    # PayPal Configuration
    PAYPAL_CLIENT_ID=your_paypal_client_id

    # Razorpay Configuration
    RZP_KEY_ID=your_razorpay_key_id
    RZP_KEY_SECRET=your_razorpay_key_secret

    # Exchange Rate API (if used, based on settings)
    # API_KEY=your_exchange_rate_api_key

    # Google Maps API Key
    GOOGLE_API_KEY=your_google_maps_api_key
    ```
    **Note on GDAL for Development (Windows):**
    If you are on Windows and followed a specific local GDAL setup (like OSGeo4W or direct binary placement), ensure the GDAL paths in `feastrove/settings.py` under the `if DEBUG is True:` block are correctly pointing to your GDAL installation, or adjust your system's PATH environment variable accordingly. The provided settings attempt to configure this for a `env/Lib/site-packages/osgeo` layout.

6.  **Run Database Migrations:**
    Apply the database schema and any pending migrations:
    ```bash
    python manage.py migrate
    ```

7.  **Create a Superuser:**
    This will allow you to access the Django admin panel:
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set up a username, email, and password.

8.  **Collect Static Files (Optional for Development, but good practice):**
    ```bash
    python manage.py collectstatic
    ```

9.  **Run the Development Server:**
    ```bash
    python manage.py runserver
    ```
    The application should now be running at `http://127.0.0.1:8000/`.

You should now be able to access the Feastrove platform in your browser and log in to the admin panel at `http://127.0.0.1:8000/admin/` with the superuser credentials.

## Deployment

The Feastrove platform is designed to be deployed on a production environment like AWS EC2. The typical production setup involves:

*   **WSGI Server:** Gunicorn is used to serve the Django application.
*   **Web Server/Reverse Proxy:** Nginx is used as a web server and reverse proxy to handle incoming HTTP requests, serve static files, and forward dynamic requests to Gunicorn.
*   **SSL/TLS:** Certbot is used to obtain and manage SSL/TLS certificates from Let's Encrypt, enabling HTTPS for secure communication.
*   **Database:** A production-grade PostgreSQL server with PostGIS enabled.
*   **Static & Media Files:** Typically served by Nginx or a cloud storage service like AWS S3 in a production environment.

This setup ensures a scalable, secure, and robust deployment of the Feastrove platform. Detailed deployment steps would involve configuring each of these components on the chosen server infrastructure.

