[🇬🇧 English](README.md) | [Persian](README_fa.md) | [🇩🇪 Deutsch](README_de.md)

# parsstore

**Weaving machine spare parts — catalogue, quote requests and a customer club, built with Django 5.**

[![CI](https://github.com/AliAEbrahimian/parsstore/actions/workflows/ci.yml/badge.svg)](https://github.com/AliAEbrahimian/parsstore/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-eda33f)](LICENSE)

[![AliAEbrahimian's GitHub stats](https://github-readme-stats.vercel.app/api?username=AliAEbrahimian&show_icons=true&theme=radical)](https://github.com/AliAEbrahimian)
[![Top languages](https://github-readme-stats.vercel.app/api/top-langs/?username=AliAEbrahimian&layout=compact&theme=radical)](https://github.com/AliAEbrahimian)

> Replace `AliAEbrahimian` in the badge URLs with your own GitHub username if you fork this repository.

---

## 👤 About the maintainer

Hi, I'm **Ali** from **Iran**. I'm a **native Persian speaker**, hold a **German B2 certificate**, and am working towards a professional career in **Germany**. Outside of code I enjoy **game development** and **video games**.

- LinkedIn: <https://www.linkedin.com/in/ali-aghaebrahimian/>
- Email: <2aaghaebrahimian@gmail.com>
- Telegram: <https://t.me/AliAEbrahimian>

### Languages and tools

<p align="center">
  <a href="https://www.python.org/" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="Python" width="40" height="40"/></a>
  <a href="https://www.djangoproject.com/" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/django/django-original.svg" alt="Django" width="40" height="40"/></a>
  <a href="https://developer.mozilla.org/en-US/docs/Web/HTML" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/html5/html5-original.svg" alt="HTML5" width="40" height="40"/></a>
  <a href="https://developer.mozilla.org/en-US/docs/Web/CSS" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/css3/css3-original.svg" alt="CSS3" width="40" height="40"/></a>
  <a href="https://developer.mozilla.org/en-US/docs/Web/JavaScript" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" alt="JavaScript" width="40" height="40"/></a>
  <a href="https://www.sqlite.org/" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/sqlite/sqlite-original.svg" alt="SQLite" width="40" height="40"/></a>
  <a href="https://git-scm.com/" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/git/git-original.svg" alt="Git" width="40" height="40"/></a>
  <a href="https://github.com/" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/github/github-original.svg" alt="GitHub" width="40" height="40"/></a>
  <a href="https://www.postgresql.org/" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/postgresql/postgresql-original.svg" alt="PostgreSQL" width="40" height="40"/></a>
  <a href="https://redis.io/" target="_blank" rel="noreferrer"><img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/redis/redis-original.svg" alt="Redis" width="40" height="40"/></a>
</p>

---

## 📦 What is parsstore?

`parsstore` is the renamed successor of the former `parstextile` project. It is a **bilingual** (English / German), left-to-right brochure site for a supplier of **weaving-machine spare parts**. It includes a searchable, paginated catalogue, part detail pages, quote forms, a customer club with discounts, and a hardened Django admin.

It is **not** an online shop: there is no cart and no online payment. Prices and stock are confirmed by phone or email.

---

## ✨ Features

- **Two languages**: English (`en`, default) and German (`de`), both left-to-right. Visitors can switch with the header language selector; `?lang=` and a one-year cookie remember the choice, while search/filter query strings are preserved.
- **Complete catalogue** at `/products/`: search by name, brand, machine model and summary; category/brand filters; server-side pagination (24 items by default); sortable admin with DB indexes. The home page shows only featured parts.
- **Part detail pages** at `/products/<id>/` with specifications, images, related parts and a quote button that prefills the contact form via `?product=<id>#contact`.
- **Customer club**: public sign-up creates a pending member; the admin activates the member and sets the discount used on offline/phone proformas.
- **Automatic WebP thumbnails** generated from admin uploads, with safe file replacement/deletion after transaction commit.
- **Three display modes** (dark / light / auto), local Vazirmatn font, no CDN, no inline scripts, strict CSP.
- **Two-layer email flow**: confirmation to the customer and optional notification to the manager; SMTP failures are logged without losing the form submission.
- **Hardened defaults**: `DEBUG=False`, secret key required outside debug, atomic rate limiting, trusted-proxy opt-in, configurable admin path and shared-cache/Redis support.
- **Automated tests** covering pages, i18n, forms, catalogue, thumbnails, rate limits, security headers and 404/500 pages.

---

## 🚀 Quick start

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
cp .env.example .env
# For local development only: set DJANGO_DEBUG=1 and a local DJANGO_SECRET_KEY.

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000>. The admin is at <http://127.0.0.1:8000/admin/> unless `DJANGO_ADMIN_PATH` is changed.

### Verification

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

For a production-like check:

```bash
DJANGO_DEBUG=0 \
DJANGO_SECRET_KEY="<random-50+-character-key>" \
DJANGO_ALLOWED_HOSTS="example.com" \
DJANGO_SECURE_SSL_REDIRECT=1 \
DJANGO_SECURE_HSTS_SECONDS=31536000 \
DJANGO_SECURE_HSTS_PRELOAD=1 \
python manage.py check --deploy
```

---

## ⚙️ Environment variables

Settings are read from the real environment or a local `.env` file (no extra dependency). See [`.env.example`](.env.example).

| Variable | Default | Purpose |
| --- | --- | --- |
| `DJANGO_DEBUG` | `0` | Set to `1` only for local development |
| `DJANGO_SECRET_KEY` | — | Required when `DEBUG=0` |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | Comma-separated hostnames |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | empty | e.g. `https://example.com` |
| `DJANGO_ADMIN_PATH` | `admin` | Change the admin URL slug |
| `DJANGO_DB_PATH` | `db.sqlite3` | SQLite database path |
| `DJANGO_CACHE_BACKEND` | LocMemCache | Custom Django cache backend |
| `DJANGO_REDIS_URL` | empty | e.g. `redis://127.0.0.1:6379/1` for shared rate limits |
| `DJANGO_TRUST_PROXY_HEADERS` | `0` | Enable only behind a trusted reverse proxy |
| `DJANGO_TRUSTED_PROXY_COUNT` | `1` | Number of trusted proxy hops for `X-Forwarded-For` |
| `INQUIRY_RATE_LIMIT` / `INQUIRY_RATE_WINDOW` | `6` / `600` | Quote-request throttle |
| `CLUB_RATE_LIMIT` / `CLUB_RATE_WINDOW` | `4` / `3600` | Membership throttle |
| `PRODUCTS_HOME_LIMIT` / `PRODUCTS_PAGE_SIZE` | `6` / `24` | Catalogue display limits |
| `CONTACT_NOTIFY_EMAIL` / `CLUB_NOTIFY_EMAIL` | empty | Manager notification recipients |
| `DJANGO_EMAIL_*` | console backend | SMTP configuration; `EMAIL_TIMEOUT` defaults to 10s |
| `DJANGO_LOG_LEVEL` | `INFO` | Root log level |

> Never commit `.env`, `db.sqlite3` or `media/`.

---

## 🗂 Project structure

```text
parsstore/
├─ manage.py
├─ requirements.txt
├─ README.md / README_fa.md / README_de.md
├─ DOCUMENTATION.txt / RESUME.txt
├─ parsstore/                 project settings and URLs
│  ├─ settings.py             env, security, i18n, cache, email, logging
│  └─ urls.py                 admin + custom 404/500 handlers
├─ core/
│  ├─ content.py              English source content
│  ├─ content_i18n.py         German content and merge logic
│  ├─ i18n.py                 bilingual UI strings and helpers
│  ├─ middleware.py           language + security headers
│  ├─ context_processors.py   SITE, NAV, T, language-switch URLs
│  ├─ models.py / forms.py / views.py / admin.py
│  ├─ images.py / utils.py    WebP thumbnails / phone normalisation
│  ├─ tests.py                automated test suite
│  └─ templates/core/         base, home, catalogue, detail, cards, errors
└─ static/core/               CSS, JS, local fonts, favicon
```

---

## 🌐 Translation notes

- UI strings live in `core/i18n.py`; longer display content lives in `core/content.py` (English source) and `core/content_i18n.py` (German overrides).
- Add a key to both languages in `UI` and use `{{ T.key }}` in templates or `t("key")` in Python.
- Language links keep the current path and non-language query parameters, so filtering still works after a switch.

---

## 🔐 Security

Strict CSP without external origins, CSRF, honeypot fields, atomic per-IP throttling, validated GET filters, server-side validation, safe image handling, opt-in proxy trust, and production deployment checks are included. The full configuration reference is in `DOCUMENTATION.txt`.

---

## 🚢 Deployment notes

1. Set `DEBUG=0`, a random `SECRET_KEY`, real `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`.
2. Use a shared cache (Redis) when running more than one worker so rate limits are consistent.
3. Run `collectstatic`, serve `staticfiles/` and `media/` through Nginx, and disable script execution in `media/`.
4. Run Gunicorn/uvicorn behind HTTPS; enable `SECURE_SSL_REDIRECT` and HSTS.
5. Back up the database, `media/` and `.env` separately.

---

## 🤝 Contributing & licence

Released under the [MIT licence](LICENSE). Report bugs or suggest features with the GitHub issue templates. The shop details shown in the demo content are examples.
