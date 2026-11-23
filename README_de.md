[🇬🇧 English](README.md) | [Persian](README_fa.md) | [🇩🇪 Deutsch](README_de.md)

# parsstore

**Ersatzteile für Webmaschinen — Katalog, Angebotsanfragen und Kundenclub, entwickelt mit Django 5.**

[![CI](https://github.com/AliAEbrahimian/parsstore/actions/workflows/ci.yml/badge.svg)](https://github.com/AliAEbrahimian/parsstore/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-3776ab?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/django-5.2-092e20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/license-MIT-eda33f)](LICENSE)

[![AliAEbrahimian's GitHub stats](https://github-readme-stats.vercel.app/api?username=AliAEbrahimian&show_icons=true&theme=radical)](https://github.com/AliAEbrahimian)
[![Top languages](https://github-readme-stats.vercel.app/api/top-langs/?username=AliAEbrahimian&layout=compact&theme=radical)](https://github.com/AliAEbrahimian)

> Ersetzen Sie `AliAEbrahimian` in den Badge-URLs durch Ihren eigenen GitHub-Benutzernamen, wenn Sie das Repository forken.

---

## 👤 Über den Maintainer

Hallo, ich bin **Ali** aus dem **Iran**. **Persisch ist meine Muttersprache**, ich besitze ein **B2-Zertifikat in Deutsch** und arbeite auf eine berufliche Zukunft in **Deutschland** hin. Neben dem Programmieren interessiere ich mich für **Spieleentwicklung** und **Videospiele**.

- LinkedIn: <https://www.linkedin.com/in/ali-aghaebrahimian/>
- E-Mail: <2aaghaebrahimian@gmail.com>
- Telegram: <https://t.me/AliAEbrahimian>

### Sprachen und Werkzeuge

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

## 📦 Was ist parsstore?

`parsstore` ist der umbenannte Nachfolger des früheren Projekts `parstextile`. Es ist eine **zweisprachige** (Englisch / Deutsch), links-nach-rechts Website für einen Lieferanten von **Ersatzteilen für Webmaschinen**: durchsuchbarer, paginierter Katalog, Detailseiten, Angebotsformulare, Kundenclub mit Rabatt und ein gehärtetes Django-Admin.

Es ist **kein Online-Shop**: Es gibt weder Warenkorb noch Online-Zahlung. Preis und Bestand werden telefonisch oder per E-Mail bestätigt.

---

## ✨ Funktionen

- **Zwei Sprachen**: Englisch (`en`, Standard) und Deutsch (`de`), beide links-nach-rechts. Die Sprachwahl im Header wird über `?lang=` und ein Jahres-Cookie gespeichert; Such- und Filterparameter bleiben erhalten.
- **Vollständiger Katalog** unter `/products/`: Suche nach Name, Marke, Maschinenmodell und Kurztext; Kategorie-/Markenfilter; serverseitige Pagination (standardmäßig 24 Teile); Datenbankindizes. Die Startseite zeigt nur ausgewählte Teile.
- **Detailseiten** unter `/products/<id>/` mit technischen Daten, Bild, ähnlichen Teilen und einer Anfrage-Schaltfläche, die das Kontaktformular über `?product=<id>#contact` vorbelegt.
- **Kundenclub**: Öffentliche Anmeldung erzeugt ein wartendes Mitglied; Aktivierung und Rabattprozentsatz werden im Admin für Offline-/Telefon-Proformarechnungen festgelegt.
- **Automatische WebP-Miniaturbilder** aus Admin-Uploads mit sicherem Austausch/Löschen nach dem Transaktions-Commit.
- **Drei Anzeigemodi** (dunkel / hell / automatisch), lokale Vazirmatn-Schrift, kein CDN, keine Inline-Skripte, strikte CSP.
- **Zweistufiger E-Mail-Versand**: Bestätigung an den Kunden und optionale Benachrichtigung an den Manager; SMTP-Fehler werden protokolliert, ohne die Formularspeicherung zu verlieren.
- **Sichere Voreinstellungen**: `DEBUG=False`, Secret Key außerhalb des Debug-Modus erforderlich, atomare Ratenbegrenzung, optionales Proxy-Vertrauen, konfigurierbarer Admin-Pfad und Unterstützung für gemeinsamen Cache/Redis.
- **Automatische Tests** für Seiten, i18n, Formulare, Katalog, Miniaturbilder, Ratenbegrenzung, Sicherheitsheader und 404/500-Seiten.

---

## 🚀 Schnellstart

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux / macOS

pip install -r requirements.txt
cp .env.example .env
# Nur für die lokale Entwicklung: DJANGO_DEBUG=1 und einen lokalen DJANGO_SECRET_KEY setzen.

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Website: <http://127.0.0.1:8000> — Admin: <http://127.0.0.1:8000/admin/> (sofern `DJANGO_ADMIN_PATH` nicht geändert wurde).

### Prüfen und testen

```bash
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

Produktionsnahe Prüfung:

```bash
DJANGO_DEBUG=0 \
DJANGO_SECRET_KEY="<zufälliger Schlüssel mit 50+ Zeichen>" \
DJANGO_ALLOWED_HOSTS="example.com" \
DJANGO_SECURE_SSL_REDIRECT=1 \
DJANGO_SECURE_HSTS_SECONDS=31536000 \
DJANGO_SECURE_HSTS_PRELOAD=1 \
python manage.py check --deploy
```

---

## ⚙️ Umgebungsvariablen

Die Einstellungen werden aus der Umgebung oder einer lokalen `.env`-Datei gelesen (ohne zusätzliche Abhängigkeit). Vollständiges Beispiel: [`.env.example`](.env.example).

| Variable | Standard | Zweck |
| --- | --- | --- |
| `DJANGO_DEBUG` | `0` | Nur lokal auf `1` setzen |
| `DJANGO_SECRET_KEY` | — | Bei `DEBUG=0` erforderlich |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1,[::1]` | Kommagetrennte Hostnamen |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | leer | z. B. `https://example.com` |
| `DJANGO_ADMIN_PATH` | `admin` | Admin-URL-Slug ändern |
| `DJANGO_DB_PATH` | `db.sqlite3` | SQLite-Datenbankpfad |
| `DJANGO_CACHE_BACKEND` | LocMemCache | Benutzerdefiniertes Django-Cache-Backend |
| `DJANGO_REDIS_URL` | leer | z. B. `redis://127.0.0.1:6379/1` für gemeinsame Ratenbegrenzung |
| `DJANGO_TRUST_PROXY_HEADERS` | `0` | Nur hinter einem vertrauenswürdigen Proxy aktivieren |
| `DJANGO_TRUSTED_PROXY_COUNT` | `1` | Anzahl vertrauenswürdiger Proxy-Hops für `X-Forwarded-For` |
| `INQUIRY_RATE_LIMIT` / `INQUIRY_RATE_WINDOW` | `6` / `600` | Begrenzung der Angebotsanfragen |
| `CLUB_RATE_LIMIT` / `CLUB_RATE_WINDOW` | `4` / `3600` | Begrenzung der Mitgliedsanfragen |
| `PRODUCTS_HOME_LIMIT` / `PRODUCTS_PAGE_SIZE` | `6` / `24` | Anzeigegrenzen des Katalogs |
| `CONTACT_NOTIFY_EMAIL` / `CLUB_NOTIFY_EMAIL` | leer | Empfänger der Manager-Benachrichtigungen |
| `DJANGO_EMAIL_*` | Console-Backend | SMTP-Konfiguration; `EMAIL_TIMEOUT` standardmäßig 10 s |
| `DJANGO_LOG_LEVEL` | `INFO` | Root-Loglevel |

> `.env`, `db.sqlite3` und `media/` niemals committen.

---

## 🗂 Projektstruktur

```text
parsstore/
├─ manage.py
├─ requirements.txt
├─ README.md / README_fa.md / README_de.md
├─ DOCUMENTATION.txt / RESUME.txt
├─ parsstore/                 Einstellungen und URLs
│  ├─ settings.py             Umgebung, Sicherheit, i18n, Cache, E-Mail, Logging
│  └─ urls.py                 Admin + eigene 404/500-Handler
├─ core/
│  ├─ content.py              englische Inhaltsquelle
│  ├─ content_i18n.py         deutsche Inhalte und Zusammenführung
│  ├─ i18n.py                 zweisprachige UI-Texte und Helfer
│  ├─ middleware.py           Sprache + Sicherheitsheader
│  ├─ context_processors.py   SITE, NAV, T und Sprachwechsel-URLs
│  ├─ models.py / forms.py / views.py / admin.py
│  ├─ images.py / utils.py    WebP-Miniaturbilder / Telefonnummern-Normalisierung
│  ├─ tests.py                automatisierte Tests
│  └─ templates/core/         base, home, Katalog, Detail, Karten, Fehlerseiten
└─ static/core/               CSS, JS, lokale Schrift, Favicon
```

---

## 🌐 Hinweise zur Übersetzung

- UI-Texte liegen in `core/i18n.py`; längere Inhalte in `core/content.py` (englische Quelle) und `core/content_i18n.py` (deutsche Übersetzungen).
- Neue Schlüssel in beiden Sprachen in `UI` ergänzen und in Templates mit `{{ T.key }}` oder in Python mit `t("key")` verwenden.
- Sprachlinks behalten den aktuellen Pfad und alle nicht-sprachlichen Query-Parameter; Filter bleiben nach dem Wechsel erhalten.

---

## 🔐 Sicherheit

Strikte CSP ohne externe Quellen, CSRF, Honeypot-Felder, atomare IP-Ratenbegrenzung, validierte GET-Filter, serverseitige Validierung, sichere Bildverarbeitung, optionales Proxy-Vertrauen und Produktionsprüfungen sind enthalten. Die vollständige Konfigurationsreferenz steht in `DOCUMENTATION.txt`.

---

## 🚢 Hinweise zum Deployment

1. `DEBUG=0`, einen zufälligen `SECRET_KEY`, echte `ALLOWED_HOSTS` und `CSRF_TRUSTED_ORIGINS` setzen.
2. Bei mehreren Workern einen gemeinsamen Cache (Redis) verwenden, damit die Ratenbegrenzung konsistent bleibt.
3. `collectstatic` ausführen, `staticfiles/` und `media/` über Nginx ausliefern und Skriptausführung in `media/` deaktivieren.
4. Gunicorn/uvicorn hinter HTTPS betreiben; `SECURE_SSL_REDIRECT` und HSTS aktivieren.
5. Datenbank, `media/` und `.env` getrennt sichern.

---

## 🤝 Mitwirken und Lizenz

Veröffentlicht unter der [MIT-Lizenz](LICENSE). Fehler und Vorschläge können über die GitHub-Issue-Vorlagen gemeldet werden. Die Shop-Daten im Demo-Inhalt sind Beispiele.
