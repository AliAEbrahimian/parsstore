[🇬🇧 English](README.md) | [🇮🇷 فارسی](README_fa.md) | [🇩🇪 Deutsch](README_de.md)

# parsstore

**قطعات یدکی ماشین‌های بافندگی — کاتالوگ، استعلام قیمت و باشگاه مشتریان، ساخته‌شده با جنگو ۵.**

[![CI](https://github.com/AliAEbrahimian/parsstore/actions/workflows/ci.yml/badge.svg)](https://github.com/AliAEbrahimian/parsstore/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-eda33f)](LICENSE)

[![AliAEbrahimian's GitHub stats](https://github-readme-stats.vercel.app/api?username=AliAEbrahimian&show_icons=true&theme=radical)](https://github.com/AliAEbrahimian)
[![Top languages](https://github-readme-stats.vercel.app/api/top-langs/?username=AliAEbrahimian&layout=compact&theme=radical)](https://github.com/AliAEbrahimian)

> اگر مخزن را Fork کردید، نام کاربری `AliAEbrahimian` را در نشانی نشان‌ها با نام کاربری خودتان جایگزین کنید.

---

## 👤 دربارهٔ نگه‌دارنده

سلام، من **علی** از **ایران** هستم. **زبان مادری‌ام فارسی** است، **مدرک B2 آلمانی** دارم و برای کار حرفه‌ای در **آلمان** تلاش می‌کنم. خارج از برنامه‌نویسی به **توسعهٔ بازی** و **بازی‌های ویدیویی** علاقه دارم.

- لینکدین: <https://www.linkedin.com/in/ali-aghaebrahimian/>
- ایمیل: <2aaghaebrahimian@gmail.com>
- تلگرام: <https://t.me/AliAEbrahimian>

### زبان‌ها و ابزارها

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

## 📦 parsstore چیست؟

`parsstore` نسخهٔ تغییرنامیافتهٔ پروژهٔ قبلی `parstextile` است. یک سایت معرفی **دوزبانه** (انگلیسی / آلمانی) با جهت چپبه راست برای تأمینکنندهٔ **قطعات یدکی ماشینهای بافندگی** است؛ با کاتالوگ جستجوپذیر و صفحهبندیشده، صفحهٔ جزئیات قطعات، فرم استعلام قیمت، باشگاه مشتریان با تخفیف و پنل مدیریت سختسازیشده.

این پروژه **فروشگاه اینترنتی نیست**: سبد خرید و پرداخت آنلاین ندارد و قیمت و موجودی تلفنی یا ایمیلی اعلام می‌شود.

---

## ✨ ویژگی‌ها

- **دو زبان**: انگلیسی (`en`، پیشفرض) و آلمانی (`de`)، هر دو چپبه راست. انتخاب زبان در هدر، با `?lang=` و کوکی یکساله ذخیره میشود و پارامترهای جستجو/فیلتر حفظ میشوند.
- **کاتالوگ کامل** در `/products/`: جست‌وجو در نام، برند، مدل ماشین و خلاصه؛ فیلتر دسته‌بندی و برند؛ صفحه‌بندی سمت سرور (پیش‌فرض ۲۴ قطعه)؛ ایندکس‌های پایگاه‌داده. صفحهٔ اصلی فقط قطعات منتخب را نشان می‌دهد.
- **صفحهٔ جزئیات هر قطعه** در `/products/<id>/` با مشخصات فنی، تصویر، قطعات مشابه و دکمهٔ استعلام که فرم تماس را با `?product=<id>#contact` پیش‌پر می‌کند.
- **باشگاه مشتریان**: ثبت‌نام عمومی با وضعیت «در انتظار تأیید»؛ فعال‌سازی و تعیین درصد تخفیف در ادمین برای پیش‌فاکتور خرید حضوری/تلفنی.
- **بندانگشتی خودکار WebP** برای تصاویر آپلودشده از ادمین، با جایگزینی/حذف ایمن فایل‌ها پس از commit تراکنش.
- **سه حالت نمایش** تاریک/روشن/خودکار، فونت محلی وزیرمتن، بدون CDN، بدون اسکریپت inline و CSP سخت‌گیرانه.
- **ایمیل دوگانه**: تأیید برای مشتری و اطلاع اختیاری برای مدیر؛ خطای SMTP فقط لاگ می‌شود و ثبت فرم را از بین نمی‌برد.
- **پیش‌فرض‌های امن**: `DEBUG=False`، الزام کلید مخفی خارج از دیباگ، محدودیت نرخ اتمیک، اعتماد اختیاری به پراکسی، مسیر ادمین قابل تغییر و پشتیبانی از کش مشترک/Redis.
- **تست خودکار** برای صفحهها، دوزبانه بودن، فرمها، کاتالوگ، بندانگشتیها، محدودیت نرخ، هدرهای امنیتی و صفحههای ۴۰۴/۵۰۰.

---

## 🚀 اجرای سریع

```bash
python -m venv .venv
.venv\Scripts\activate        # ویندوز
# source .venv/bin/activate   # لینوکس / مک

pip install -r requirements.txt
cp .env.example .env
# فقط برای توسعهٔ محلی: DJANGO_DEBUG=1 و یک DJANGO_SECRET_KEY محلی بگذارید.

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

سایت: <http://127.0.0.1:8000> — پنل مدیریت: <http://127.0.0.1:8000/admin/> (مگر اینکه `DJANGO_ADMIN_PATH` را تغییر دهید).

### بررسی و آزمون

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

بررسی شبیه تولید:

```bash
DJANGO_DEBUG=0 \
DJANGO_SECRET_KEY="<کلید تصادفی ۵۰+ نویسه‌ای>" \
DJANGO_ALLOWED_HOSTS="example.com" \
DJANGO_SECURE_SSL_REDIRECT=1 \
DJANGO_SECURE_HSTS_SECONDS=31536000 \
DJANGO_SECURE_HSTS_PRELOAD=1 \
python manage.py check --deploy
```

---

## ⚙️ متغیرهای محیطی

تنظیمات از محیط یا فایل `.env` خوانده می‌شوند (بدون وابستگی اضافه). نمونهٔ کامل: [`.env.example`](.env.example).

| متغیر | پیش‌فرض | توضیح |
| --- | --- | --- |
| `DJANGO_DEBUG` | `0` | فقط برای توسعهٔ محلی `1` شود |
| `DJANGO_SECRET_KEY` | — | در `DEBUG=0` الزامی است |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | دامنه‌های مجاز، جداشده با کاما |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | خالی | مثل `https://example.com` |
| `DJANGO_ADMIN_PATH` | `admin` | تغییر مسیر پنل مدیریت |
| `DJANGO_DB_PATH` | `db.sqlite3` | مسیر پایگاه‌دادهٔ SQLite |
| `DJANGO_CACHE_BACKEND` | LocMemCache | بک‌اند کش سفارشی جنگو |
| `DJANGO_REDIS_URL` | خالی | مثل `redis://127.0.0.1:6379/1` برای محدودیت نرخ مشترک |
| `DJANGO_TRUST_PROXY_HEADERS` | `0` | فقط پشت پراکسی مطمئن فعال شود |
| `DJANGO_TRUSTED_PROXY_COUNT` | `1` | تعداد hopهای مطمئن برای `X-Forwarded-For` |
| `INQUIRY_RATE_LIMIT` / `INQUIRY_RATE_WINDOW` | `6` / `600` | محدودیت استعلام |
| `CLUB_RATE_LIMIT` / `CLUB_RATE_WINDOW` | `4` / `3600` | محدودیت عضویت |
| `PRODUCTS_HOME_LIMIT` / `PRODUCTS_PAGE_SIZE` | `6` / `24` | محدودیت نمایش کاتالوگ |
| `CONTACT_NOTIFY_EMAIL` / `CLUB_NOTIFY_EMAIL` | خالی | گیرندگان ایمیل مدیر |
| `DJANGO_EMAIL_*` | console backend | تنظیمات SMTP؛ `EMAIL_TIMEOUT` پیش‌فرض ۱۰ ثانیه |
| `DJANGO_LOG_LEVEL` | `INFO` | سطح لاگ |

> هرگز `.env`، `db.sqlite3` یا `media/` را کامیت نکنید.

---

## 🗂 ساختار پروژه

```text
parsstore/
├─ manage.py
├─ requirements.txt
├─ README.md / README_fa.md / README_de.md
├─ DOCUMENTATION.txt / RESUME.txt
├─ parsstore/                 تنظیمات و مسیرهای اصلی
│  ├─ settings.py             محیط، امنیت، دو زبان، کش، ایمیل و لاگ
│  └─ urls.py                 ادمین + ۴۰۴/۵۰۰
├─ core/
│  ├─ content.py              منبع محتوای انگلیسی
│  ├─ content_i18n.py         محتوای آلمانی و ادغام
│  ├─ i18n.py                 رشتههای رابط دوزبانه و کمکتابعها
│  ├─ middleware.py           زبان + هدرهای امنیتی
│  ├─ context_processors.py   SITE، NAV، T و لینک‌های تغییر زبان
│  ├─ models.py / forms.py / views.py / admin.py
│  ├─ images.py / utils.py    بندانگشتی WebP / نرمال‌سازی شماره
│  ├─ tests.py                تستهای خودکار
│  └─ templates/core/         base، home، کاتالوگ، جزئیات، کارت‌ها، خطاها
└─ static/core/               CSS، JS، فونت محلی و فاوآیکون
```

---

## 🌐 نکات ترجمه

- رشتههای رابط در `core/i18n.py` هستند؛ محتوای بلندتر در `core/content.py` (منبع انگلیسی) و `core/content_i18n.py` (ترجمهٔ آلمانی).
- هر کلید جدید را در هر دو زبان `UI` اضافه کنید و در قالب با `{{ T.key }}` یا در پایتون با `t("key")` استفاده کنید.
- لینک‌های تغییر زبان مسیر فعلی و پارامترهای غیرزبانی را نگه می‌دارند؛ بنابراین فیلترها پس از تغییر زبان حفظ می‌شوند.

---

## 🔐 امنیت

CSP سختگیرانه بدون منبع خارجی، CSRF، فیلد تله، محدودیت نرخ اتمیک بر اساس IP، اعتبارسنجی فیلترهای GET، اعتبارسنجی سمت سرور، پردازش ایمن تصویر، اعتماد اختیاری به پراکسی و بررسی استقرار تولید. جزئیات کامل در `DOCUMENTATION.txt`.

---

## 🚢 نکات استقرار

1. `DEBUG=0`، `SECRET_KEY` تصادفی، `ALLOWED_HOSTS` واقعی و `CSRF_TRUSTED_ORIGINS` را تنظیم کنید.
2. برای چند worker از کش مشترک (Redis) استفاده کنید تا محدودیت نرخ یکسان باشد.
3. `collectstatic` را اجرا کنید و `staticfiles/` و `media/` را با Nginx سرو کنید؛ اجرای اسکریپت در `media/` را ببندید.
4. برنامه را با Gunicorn/uvicorn پشت HTTPS اجرا کنید و `SECURE_SSL_REDIRECT` و HSTS را فعال کنید.
5. از پایگاه‌داده، `media/` و `.env` جداگانه پشتیبان بگیرید.

---

## 🤝 مشارکت و مجوز

مجوز: [MIT](LICENSE). اطلاعات فروشگاه در محتوای نمایشی نمونه است.
