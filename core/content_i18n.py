"""German translations for the display content.

The English source content lives in ``core/content.py``. Only translated values
are kept here; ``get_content()`` merges them over the English base for the
active language.
"""

from copy import deepcopy

from . import content

_DE = {
    "SITE": {
        "name": "ParsStore",
        "name_en": "PARSSTORE",
        "slogan": "Ersatzteile für Webmaschinen",
        "description": "Fachlieferant für Ersatzteile von Picanol, Itema, Somet, Vamatex, Dornier und anderen führenden Webmaschinenmarken.",
        "phone": "+98 21 5500 0000",
        "mobile": "+98 912 000 0000",
        "email": "info@parsstore.ir",
        "address": "Teheran, Jomhouri-Straße, vor dem Hassanabad-Platz, Textil-Passage, 2. Stock, Einheit 24",
        "address_short": "Teheran, Jomhouri-Straße",
        "hours": "Samstag–Mittwoch 09:00–17:30 — Donnerstag 09:00–13:00",
    },
    "BRANDS": [
        {"name": "Picanol", "latin": "PICANOL", "country": "Belgien", "models": ["GTX", "GAMMA", "OMNIplus", "OPTIMAX", "PAT"], "note": "Greifer- und Luftdüsen-Webmaschinen"},
        {"name": "Itema", "latin": "ITEMA", "country": "Italien", "models": ["ALPHA", "MYTHOS", "SOMET", "VAMATEX"], "note": "Vollständige Abdeckung der Somet- und Vamatex-Familien"},
        {"name": "Somet", "latin": "SOMET", "country": "Italien", "models": ["SM92", "SM93", "THEMA", "SUPEREXCEL"], "note": "Mechanische Teile und Steuerplatinen"},
        {"name": "Vamatex", "latin": "VAMATEX", "country": "Italien", "models": ["P1001", "P401S", "LEONARDO", "SILVER"], "note": "Verschleiß- und Verbrauchsteile"},
        {"name": "Dornier", "latin": "DORNIER", "country": "Deutschland", "models": ["HTV", "ATV", "PS", "AWS"], "note": "Teile für Kraftübertragung und Schusseintrag"},
        {"name": "Sulzer", "latin": "SULZER", "country": "Schweiz", "models": ["G6100", "G6200", "G6300"], "note": "Projektil- und Riementeile"},
        {"name": "Toyota", "latin": "TOYOTA", "country": "Japan", "models": ["JAT", "LWT", "LX"], "note": "Düsen, Pumpen und Luftdüsen-Teile"},
        {"name": "Tsudakoma", "latin": "TSUDAKOMA", "country": "Japan", "models": ["ZA", "ZW", "ZAX"], "note": "Elektronische und mechanische Teile"},
    ],
    "CATEGORIES": [
        {"title": "Mechanik & Verschleißteile", "icon": "gear", "desc": "Zahnräder, Buchsen, Wellen, Lager, Hebel und alle bewegten Verschleißteile.", "tags": ["Buchse", "Welle", "Zahnrad"]},
        {"title": "Elektronik & Platinen", "icon": "chip", "desc": "Steuerplatinen, Umrichter, Sensoren, Geber und Original-Elektronikkomponenten.", "tags": ["Platine", "Sensor", "Umrichter"]},
        {"title": "Schuss, Düsen & Pumpen", "icon": "nozzle", "desc": "Einspritzdüsen, Ventile, Wasser- und Ölpumpen, Verteiler und komplette Schusssysteme.", "tags": ["Düse", "Ventil", "Pumpe"]},
        {"title": "Riemen, Motoren & Getriebe", "icon": "belt", "desc": "Antriebsriemen, Antriebsmotoren, Getriebe und industrielle Kupplungen.", "tags": ["Riemen", "Getriebe", "Motor"]},
        {"title": "Weberei & Verbrauchsmaterial", "icon": "thread", "desc": "Webblätter, Litzen, Schaftbäume, Webkämme, Projektile und Verbrauchsartikel.", "tags": ["Webblatt", "Litze", "Webkamm"]},
        {"title": "Werkzeuge & Zubehör", "icon": "tool", "desc": "Werkzeuge für Einstellung und Wartung, Standardteile und Zubehör.", "tags": ["Werkzeug", "Wartung", "Standard"]},
    ],
    "FEATURES": [
        {"icon": "shield", "title": "Originalteile", "desc": "Bezug aus zuverlässigen Quellen, mit Nachweisen und technischen Daten."},
        {"icon": "box", "title": "Große Lagerauswahl", "desc": "Über 12.000 Teile auf Lager für führende Webmaschinenmarken."},
        {"icon": "truck", "title": "Schneller Versand", "desc": "Versand im ganzen Land und internationaler Versand für Kunden im Ausland."},
        {"icon": "headset", "title": "Technischer Support", "desc": "Hilfe bei der Identifikation nach Maschinenmodell, Teilenummer oder Foto."},
        {"icon": "tag", "title": "Transparente Preise", "desc": "Genauer Preis vor dem Kauf, keine versteckten Kosten, offizielle Rechnung."},
        {"icon": "clock", "title": "Langjährige Erfahrung", "desc": "Jahrelange Zusammenarbeit mit Textilbetrieben und Webwerkstätten im ganzen Land."},
    ],
    "STATS": [
        {"value": "20", "label": "Jahre in der Textilindustrie"},
        {"value": "12.000+", "label": "Teile auf Lager"},
        {"value": "8", "label": "abgedeckte Marken"},
        {"value": "24", "label": "Stunden bis zur Antwort"},
    ],
    "STEPS": [
        {"title": "Anfrage senden", "desc": "Senden Sie uns Maschinenmodell, Teilenummer oder ein Foto des Teils."},
        {"title": "Technische Prüfung", "desc": "Unsere Experten identifizieren das Teil und nennen Bestand und Lieferzeit."},
        {"title": "Preisbestätigung", "desc": "Wir stellen eine offizielle Pro-forma-Rechnung mit Endpreis und Lieferbedingungen aus."},
        {"title": "Versand", "desc": "Nach Bestätigung wird die Bestellung verpackt und schnellstmöglich versendet."},
    ],
    "CLUB": {
        "eyebrow": "Kundenclub",
        "title": "Jeder Kauf bringt mehr Rabatt",
        "lead": "Wir betreiben keinen Online-Shop; Bestellungen erfolgen weiterhin telefonisch oder persönlich. Als Mitglied nennen Sie beim Kauf Ihren Mitgliedscode oder Ihre Mobilnummer, um den Rabatt auf der Pro-forma-Rechnung zu erhalten.",
        "perks": [
            {"icon": "tag", "title": "Rabatt auf jeden Kauf", "desc": "Ihr Mitgliederrabatt wird automatisch auf die Pro-forma-Rechnung angewendet."},
            {"icon": "shield", "title": "Mitgliederpreise", "desc": "Aktive Mitglieder erhalten Sonderpreise bei Anfragen und Folgebestellungen."},
            {"icon": "headset", "title": "Priorisierter Support", "desc": "Club-Anfragen werden in der technischen Prüfung bevorzugt bearbeitet."},
            {"icon": "truck", "title": "Bestandsinfos", "desc": "Mitglieder werden früher über stark nachgefragte Teile und Lieferbedingungen informiert."},
        ],
        "tiers": [
            {"name": "Bronze", "discount": "5 %", "desc": "Ab dem ersten Kauf"},
            {"name": "Silber", "discount": "8 %", "desc": "Jahreskäufe über 500 Mio. Rial"},
            {"name": "Gold", "discount": "12 %", "desc": "Jahreskäufe über 2 Mrd. Rial"},
        ],
        "note": "Die Mitgliedschaft ist kostenlos. Nach Bestätigung erhalten Sie Ihren Code für den Einkauf.",
    },
    "FAQ": [
        {"q": "Ich kenne das benötigte Teil nicht – welche Angaben brauchen Sie?", "a": "Das genaue Webmaschinenmodell, das Baujahr und möglichst ein Foto oder die Teilenummer genügen. Unsere Experten identifizieren das Teil anhand dieser Angaben."},
        {"q": "Versenden Sie auch in andere Städte oder ins Ausland?", "a": "Ja. Der Versand im Inland erfolgt per Fracht und Post, für Kunden außerhalb Irans organisieren wir den internationalen Transport."},
        {"q": "Haben die Teile eine Garantie?", "a": "Elektronische Teile und einige mechanische Artikel haben eine Funktionsgarantie; die genauen Bedingungen stehen in der Pro-forma-Rechnung."},
        {"q": "Gibt es eine Mindestbestellmenge?", "a": "Nein – auch ein einzelnes Teil kann versendet werden. Bei größeren Bestellungen gibt es Mengenrabatte."},
        {"q": "Wie funktioniert der Kundenclub?", "a": "Füllen Sie das Mitgliedsformular auf dieser Seite aus. Nach Bestätigung erhalten Sie Code und Rabattsatz; nennen Sie den Code oder die Mobilnummer bei der Bestellung telefonisch oder persönlich, damit der Rabatt auf der Pro-forma-Rechnung erscheint. Es gibt keinen Online-Shop und keine Online-Zahlung."},
    ],
}

_BASE = {
    "SITE": content.SITE,
    "BRANDS": content.BRANDS,
    "CATEGORIES": content.CATEGORIES,
    "FEATURES": content.FEATURES,
    "STATS": content.STATS,
    "STEPS": content.STEPS,
    "CLUB": content.CLUB,
    "FAQ": content.FAQ,
}


def get_content(lang: str = "en") -> dict:
    """Return the complete content structure for the requested language.

    English is the source language. Shared values (links, phone numbers, etc.)
    are inherited; only translated text fields are overridden for German.
    """
    code = (lang or "en").split("-")[0]
    result = deepcopy(_BASE)
    if code != "de":
        return result
    for key, value in _DE.items():
        if key == "SITE":
            result["SITE"].update({field: text for field, text in value.items() if text})
        else:
            result[key] = deepcopy(value)
    return result
