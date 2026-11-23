"""
All display copy and demo data for the site lives in this file.
To change the store name, phone numbers, brands, categories and so on, edit
only this file. The German translations are kept in ``content_i18n.py``.
"""

SITE = {
    "name": "ParsStore",
    "name_en": "PARSSTORE",
    "slogan": "Weaving machine spare parts",
    "since": "2006",
    "description": (
        "Specialised supplier of spare parts for Picanol, Itema, Somet, "
        "Vamatex, Dornier and other leading weaving machine brands."
    ),
    "phone": "+98 21 5500 0000",
    "phone_link": "+982155000000",
    "mobile": "+98 912 000 0000",
    "mobile_link": "+989120000000",
    "whatsapp": "https://wa.me/989120000000",
    "email": "info@parsstore.ir",
    "address": "Tehran, Jomhouri Street, before Hassanabad Square, Textile Passage, 2nd floor, unit 24",
    "address_short": "Tehran, Jomhouri Street",
    "hours": "Saturday–Wednesday 09:00–17:30 — Thursday 09:00–13:00",
    "instagram": "https://instagram.com/",
    "map_url": "https://maps.google.com/?q=Tehran+Jomhouri+Street",
}

# ---------------------------------------------------------------- brands
BRANDS = [
    {
        "name": "Picanol",
        "latin": "PICANOL",
        "country": "Belgium",
        "models": ["GTX", "GAMMA", "OMNIplus", "OPTIMAX", "PAT"],
        "note": "Rapier and air-jet weaving machines",
    },
    {
        "name": "Itema",
        "latin": "ITEMA",
        "country": "Italy",
        "models": ["ALPHA", "MYTHOS", "SOMET", "VAMATEX"],
        "note": "Full coverage of the Somet and Vamatex families",
    },
    {
        "name": "Somet",
        "latin": "SOMET",
        "country": "Italy",
        "models": ["SM92", "SM93", "THEMA", "SUPEREXCEL"],
        "note": "Mechanical parts and control boards",
    },
    {
        "name": "Vamatex",
        "latin": "VAMATEX",
        "country": "Italy",
        "models": ["P1001", "P401S", "LEONARDO", "SILVER"],
        "note": "Wear parts and consumables",
    },
    {
        "name": "Dornier",
        "latin": "DORNIER",
        "country": "Germany",
        "models": ["HTV", "ATV", "PS", "AWS"],
        "note": "Power transmission and weft system parts",
    },
    {
        "name": "Sulzer",
        "latin": "SULZER",
        "country": "Switzerland",
        "models": ["G6100", "G6200", "G6300"],
        "note": "Projectile and belt parts",
    },
    {
        "name": "Toyota",
        "latin": "TOYOTA",
        "country": "Japan",
        "models": ["JAT", "LWT", "LX"],
        "note": "Nozzles, pumps and air-jet parts",
    },
    {
        "name": "Tsudakoma",
        "latin": "TSUDAKOMA",
        "country": "Japan",
        "models": ["ZA", "ZW", "ZAX"],
        "note": "Electronic and mechanical parts",
    },
]

# ---------------------------------------------------------------- product categories
CATEGORIES = [
    {
        "title": "Mechanical & wear parts",
        "icon": "gear",
        "desc": "Gears, bushes, shafts, bearings, levers and all moving wear parts.",
        "tags": ["bush", "shaft", "gear"],
    },
    {
        "title": "Electronics & boards",
        "icon": "chip",
        "desc": "Control boards, inverters, sensors, encoders and genuine electronic components.",
        "tags": ["board", "sensor", "inverter"],
    },
    {
        "title": "Weft, nozzles & pumps",
        "icon": "nozzle",
        "desc": "Injection nozzles, valves, water and oil pumps, manifolds and complete weft systems.",
        "tags": ["nozzle", "valve", "pump"],
    },
    {
        "title": "Belts, motors & gearboxes",
        "icon": "belt",
        "desc": "Drive belts, motors, gearboxes and industrial couplings.",
        "tags": ["belt", "gearbox", "motor"],
    },
    {
        "title": "Weaving & consumables",
        "icon": "thread",
        "desc": "Reeds, heddles, heald shafts, drop wires, projectiles and line consumables.",
        "tags": ["reed", "heddle", "drop wire"],
    },
    {
        "title": "Tools & technical supplies",
        "icon": "tool",
        "desc": "Tools for adjustment and service, standard parts and accessories.",
        "tags": ["tools", "service", "standard"],
    },
]

# ---------------------------------------------------------------- benefits
FEATURES = [
    {
        "icon": "shield",
        "title": "Genuine parts",
        "desc": "Sourced from reliable channels with documents and technical data available.",
    },
    {
        "icon": "box",
        "title": "Wide stock",
        "desc": "More than 12,000 parts ready in stock for leading weaving brands.",
    },
    {
        "icon": "truck",
        "title": "Fast delivery",
        "desc": "Nationwide shipping and international shipping arranged for customers abroad.",
    },
    {
        "icon": "headset",
        "title": "Technical support",
        "desc": "Help identifying parts by machine model, part number or photo.",
    },
    {
        "icon": "tag",
        "title": "Transparent pricing",
        "desc": "Exact quotation before purchase, no hidden costs, official invoice.",
    },
    {
        "icon": "clock",
        "title": "Long-standing record",
        "desc": "Years of cooperation with textile mills and weaving workshops nationwide.",
    },
]

# ---------------------------------------------------------------- statistics
STATS = [
    {"value": "20", "label": "years in the textile industry"},
    {"value": "12,000+", "label": "parts in stock"},
    {"value": "8", "label": "brands covered"},
    {"value": "24", "label": "hours to answer an inquiry"},
]

# ---------------------------------------------------------------- ordering steps
STEPS = [
    {
        "title": "Send an inquiry",
        "desc": "Send us the machine model, part number or a photo of the part.",
    },
    {
        "title": "Technical review",
        "desc": "Our experts identify the part and confirm stock and lead time.",
    },
    {
        "title": "Price confirmation",
        "desc": "We issue an official proforma invoice with the final price and delivery terms.",
    },
    {
        "title": "Dispatch",
        "desc": "Once confirmed, the order is packed and shipped as quickly as possible.",
    },
]

# ---------------------------------------------------------------- customer club
CLUB = {
    "eyebrow": "Customer club",
    "title": "Every purchase earns more discount",
    "lead": (
        "We do not run an online shop; orders are still placed by phone or in person. "
        "As a member, quote your membership code or mobile number when buying to get "
        "your discount on the proforma invoice."
    ),
    "perks": [
        {
            "icon": "tag",
            "title": "Discount on every purchase",
            "desc": "Your member discount is applied automatically to the proforma invoice.",
        },
        {
            "icon": "shield",
            "title": "Member prices",
            "desc": "Active members receive special prices on inquiries and repeat orders.",
        },
        {
            "icon": "headset",
            "title": "Priority support",
            "desc": "Club requests are prioritised in the technical review queue.",
        },
        {
            "icon": "truck",
            "title": "Stock updates",
            "desc": "Members are informed earlier about fast-moving items and delivery terms.",
        },
    ],
    "tiers": [
        {"name": "Bronze", "discount": "5%", "desc": "From your first purchase"},
        {"name": "Silver", "discount": "8%", "desc": "Annual purchases over 500 million rials"},
        {"name": "Gold", "discount": "12%", "desc": "Annual purchases over 2 billion rials"},
    ],
    "note": "Membership is free. After approval, your membership code is issued for quoting at purchase.",
}

# ---------------------------------------------------------------- FAQ
FAQ = [
    {
        "q": "I don't know the part I need — what information do you need?",
        "a": "The exact weaving machine model, year of manufacture and, if possible, a photo or the part number are enough. Our experts identify the part from this information.",
    },
    {
        "q": "Can you ship to other cities or abroad?",
        "a": "Yes. We ship nationwide by freight and post, and arrange international transport for customers outside Iran.",
    },
    {
        "q": "Do the parts come with a warranty?",
        "a": "Electronic parts and some mechanical items come with a health/defect warranty; exact terms are stated in the proforma invoice.",
    },
    {
        "q": "Is there a minimum order?",
        "a": "There is no minimum order — even a single part can be shipped. Volume discounts are available for larger orders.",
    },
    {
        "q": "How does the customer club work?",
        "a": "Fill in the membership form on this page. After approval you receive your code and discount rate; quote the code or mobile number when ordering by phone or in person so the discount appears on the proforma invoice. There is no online shop and no online payment.",
    },
]
