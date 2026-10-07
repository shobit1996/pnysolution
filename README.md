# PNY Talent Solutions — Backend API

Django REST Framework backend for PNY Talent Solutions. Deployed on Vercel (serverless Python), backed by Supabase PostgreSQL, with resume storage on Supabase Storage (via the native supabase-py client — no AWS/S3).

---

## Local Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/pnysolution.git
cd pnysolution

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your local environment file
cp .env.example .env
# Edit .env and fill in your values (see Environment Variables below)

# 5. Run database migrations
python manage.py migrate

# 6. Create a Django superuser (for /admin access)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

## Supabase Setup

### 1. Create a Supabase project
Go to [https://supabase.com](https://supabase.com), create a new project, and note your project **reference ID** (`[ref]`).

### 2. Get the DATABASE_URL connection string
In your Supabase dashboard:
- Navigate to **Settings → Database → Connection string → URI**
- Copy the URI — it looks like:
  ```
  postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres
  ```
- Append `?sslmode=require` to the end.

### 3. Create the Storage bucket for resumes
- Navigate to **Storage** in the Supabase sidebar.
- Click **New bucket**, name it `resumes`, and set it to **Private**.

### 4. Get the Supabase service role key
- Navigate to **Settings → API** in the Supabase dashboard.
- Copy the **service_role** key (labelled "secret").
- This is your `SUPABASE_SERVICE_KEY` — keep it secret and never use it in frontend code.
- The **Project URL** (also on that page) is your `SUPABASE_URL`.

---

## Vercel Deployment

### 1. Connect your GitHub repository
- Push this project to a GitHub repository.
- Go to [https://vercel.com](https://vercel.com) and create a new project.
- Import the GitHub repository.

### 2. Set environment variables in Vercel
In your Vercel project dashboard, go to **Settings → Environment Variables** and add all variables listed in the table below.

### 3. Deploy
Vercel will automatically deploy on every push to your main branch. The `vercel.json` and `build_files.sh` at the project root handle the build process.

> **Important:** Run migrations and create a superuser against your Supabase database *before* the first deployment (see commands below).

---

## Running Migrations Against Supabase

Run these commands locally with your Supabase `DATABASE_URL`:

```bash
# Apply all migrations to Supabase PostgreSQL
DATABASE_URL="postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres?sslmode=require" python manage.py migrate

# Create an admin superuser in the Supabase database
DATABASE_URL="postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres?sslmode=require" python manage.py createsuperuser
```

On Windows (PowerShell):
```powershell
$env:DATABASE_URL="postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres?sslmode=require"
python manage.py migrate
python manage.py createsuperuser
```

---

## Media Files (Resume Uploads)

| Environment | Storage backend | Where files go |
|---|---|---|
| Local development (`DEBUG=True`) | Django `FileSystemStorage` | `media/` folder on disk |
| Production (`DEBUG=False`) | `SupabaseStorage` (custom, supabase-py) | Supabase Storage bucket `resumes` |

File URLs in production are **signed** (valid for 1 hour) and require authentication to access, keeping candidate CVs private.

---

## Resend API Key Rotation

The `RESEND_API_KEY` is a secret credential used to send email via the [Resend](https://resend.com) HTTP API. **This cannot be automated** — to rotate it:

1. Log in to your [Resend dashboard](https://resend.com/api-keys).
2. Create a new API key.
3. Update the `RESEND_API_KEY` environment variable in Vercel (Settings → Environment Variables).
4. Delete the old API key from the Resend dashboard.

---

## Environment Variables Reference

| Variable | Required | Description | Example |
|---|---|---|---|
| `SECRET_KEY` | ✅ Yes | Django secret key — generate a new one for production | `django-insecure-...` |
| `DEBUG` | ✅ Yes | Set to `False` in production | `False` |
| `ALLOWED_HOSTS` | ✅ Yes | Comma-separated list of allowed hostnames | `your-project.vercel.app,www.yourdomain.com` |
| `CSRF_TRUSTED_ORIGINS` | ✅ Yes | Comma-separated list of trusted origins (full URLs) | `https://your-project.vercel.app` |
| `DATABASE_URL` | ✅ Yes | Supabase PostgreSQL connection string with `sslmode=require` | `postgresql://postgres:pw@db.ref.supabase.co:5432/postgres?sslmode=require` |
| `RESEND_API_KEY` | ✅ Yes | API key for Resend email service | `re_abc123...` |
| `DEFAULT_FROM_EMAIL` | No | From address in outgoing emails | `PNY Talent Solutions <noreply@yourdomain.com>` |
| `EMAIL_HOST_USER` | No | SMTP username (fallback when RESEND_API_KEY is not set) | `you@gmail.com` |
| `EMAIL_HOST_PASSWORD` | No | SMTP app password (fallback) | `abcd efgh ijkl mnop` |
| `NOTIFICATION_RECIPIENTS` | ✅ Yes | Comma-separated list of email addresses for alerts | `admin@yourdomain.com,hr@yourdomain.com` |
| `ADMIN_URL` | No | Full URL to Django admin (used in email notifications) | `https://your-project.vercel.app/admin/` |
| `SUPABASE_URL` | ✅ Prod | Supabase project URL | `https://[ref].supabase.co` |
| `SUPABASE_SERVICE_KEY` | ✅ Prod | Supabase service role key (secret — never use in frontend) | `eyJ...` |
| `SUPABASE_STORAGE_BUCKET` | No | Supabase Storage bucket name (default: `resumes`) | `resumes` |

> **✅ Prod** = required when `DEBUG=False` (production deployment).

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/api/jobs/` | List all active job postings |
| `POST` | `/api/applications/` | Submit a job application (multipart/form-data with resume file) |
| `POST` | `/api/inquiries/` | Submit a client partnership inquiry |
| `GET/POST` | `/admin/` | Django admin panel |
