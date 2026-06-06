# DÖNERIMPERIUM™ - Constants & Configuration
# ============================================

import os

# Paths
SRC_DIR   = os.path.dirname(os.path.abspath(__file__))
BASE_DIR  = os.path.dirname(SRC_DIR)          # project root (one level above src/)
SAVES_DIR = os.path.join(BASE_DIR, "saves")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
DATA_DIR  = os.path.join(BASE_DIR, "data")

# Screen
_BASE_W = 1280
_BASE_H = 720
FPS = 60
TITLE = "DÖNERIMPERIUM™"

import pygame as _pygame

def SCREEN_W():
    surf = _pygame.display.get_surface()
    return surf.get_width() if surf else _BASE_W

def SCREEN_H():
    surf = _pygame.display.get_surface()
    return surf.get_height() if surf else _BASE_H

# Colors - Turkish/Mediterranean palette
C_BG         = (18, 14, 10)
C_BG2        = (28, 22, 16)
C_PANEL      = (35, 28, 20)
C_PANEL2     = (45, 36, 25)
C_BORDER     = (90, 70, 45)
C_BORDER2    = (120, 95, 60)
C_GOLD       = (220, 175, 60)
C_GOLD2      = (255, 210, 80)
C_RED        = (210, 60, 55)
C_RED2       = (240, 80, 70)
C_GREEN      = (80, 180, 80)
C_GREEN2     = (100, 220, 100)
C_BLUE       = (60, 130, 200)
C_BLUE2      = (80, 160, 240)
C_WHITE      = (240, 230, 215)
C_GRAY       = (140, 125, 105)
C_GRAY2      = (90, 80, 65)
C_ORANGE     = (220, 130, 40)
C_ORANGE2    = (255, 160, 60)
C_PURPLE     = (150, 80, 200)
C_TEAL       = (50, 170, 155)
C_DARK_RED   = (140, 30, 25)
C_TEXT       = (240, 230, 215)
C_TEXT2      = (185, 170, 145)
C_TEXT3      = (120, 110, 90)
C_ACCENT     = (230, 180, 50)
C_SUCCESS    = (70, 200, 110)
C_WARN       = (230, 165, 40)
C_DANGER     = (210, 55, 55)
C_INFO       = (60, 165, 230)
C_HIGHLIGHT  = (255, 220, 80)

# Emojis/Symbols (text fallbacks)
EURO = "€"
STAR = "★"
ARROW_UP = "▲"
ARROW_DOWN = "▼"
BULLET = "●"
CHECK = "✓"
CROSS = "✗"
FLAME = "🔥"

# Game balance
STARTING_MONEY = 15000.0
TICK_RATE = 1.0          # seconds per game tick
TICKS_PER_HOUR = 6       # 6 ticks = 1 in-game hour
HOURS_PER_DAY = 24
TICKS_PER_DAY = TICKS_PER_HOUR * HOURS_PER_DAY

# Customer spawn rates (per hour, by type)
CUSTOMER_RATES = {
    "schueler":    {"peak": [11, 12, 13], "rate": 8},
    "student":     {"peak": [12, 13, 19, 20], "rate": 6},
    "bueroangest": {"peak": [12, 13], "rate": 10},
    "handwerker":  {"peak": [11, 12, 13, 17], "rate": 7},
    "familie":     {"peak": [12, 13, 18, 19], "rate": 5},
    "tourist":     {"peak": [11, 12, 13, 14, 15], "rate": 4},
    "stammkunde":  {"peak": [12, 13, 18, 19], "rate": 9},
}

# Döner ingredients base costs (per unit)
INGREDIENT_COSTS = {
    "fleisch_basis":    1.20,
    "fleisch_premium":  2.50,
    "brot_normal":      0.25,
    "brot_vollkorn":    0.40,
    "brot_wrap":        0.30,
    "salat":            0.15,
    "tomate":           0.20,
    "zwiebel":          0.10,
    "kraut":            0.12,
    "gurke":            0.15,
    "sosse_knoblauch":  0.08,
    "sosse_scharf":     0.08,
    "sosse_kraeuterkaese": 0.12,
    "sosse_joghurt":    0.10,
    "sosse_tomaten":    0.09,
}

# Staff attributes ranges
STAFF_ATTR_MIN = 1
STAFF_ATTR_MAX = 10

# Research tree node IDs
RESEARCH_NODES = [
    "schnittmaschine",
    "premium_zutaten",
    "ki_kasse",
    "schnelle_lieferung",
    "eigene_logistik",
    "franchise",
    "brotfabrik",
    "fleischproduktion",
    "solar_energie",
    "loyalty_app",
    "geheimrezept",
    "mega_grill",
]

# Location types and their properties
LOCATION_TYPES = {
    "kleinststadt":     {"rent": 800,   "foot_traffic": 200,  "unlock_branches": 0},
    "grossstadt":       {"rent": 2500,  "foot_traffic": 500, "unlock_branches": 3},
    "bahnhof":          {"rent": 3500,  "foot_traffic": 800, "unlock_branches": 5},
    "einkaufszentrum":  {"rent": 4500,  "foot_traffic": 1100, "unlock_branches": 8},
    "flughafen":        {"rent": 8000,  "foot_traffic": 1600, "unlock_branches": 15},
}

# Competitor types
COMPETITOR_TYPES = [
    {"name": "Billig-Döner Baris",    "quality": 3, "price_mod": 0.7,  "color": C_RED},
    {"name": "Premium Kebab Palace",  "quality": 9, "price_mod": 1.6,  "color": C_GOLD},
    {"name": "McBurger Fusion",       "quality": 5, "price_mod": 1.0,  "color": C_ORANGE},
    {"name": "Geheimtipp Dönerbude",  "quality": 8, "price_mod": 0.9,  "color": C_GREEN},
]

# Humor messages
HUMOR_MESSAGES = [
    ("info", "Ein Kunde behauptet, früher seien die Döner größer gewesen."),
    ("warn", "Knoblauchsoße verursacht erneut Lieferprobleme beim Fahrer."),
    ("success", "Wallah bester Döner! Umsatz +15%!"),
    ("info", "Ein Stammkunde fragt: 'Machst du auch Döner ohne Döner?'"),
    ("warn", "Mitarbeiter Mehmet tanzt statt Döner zu schneiden."),
    ("success", "Influencer postet: 'Das ist kein Döner, das ist KUNST!' +200 Kunden!"),
    ("info", "Ein Veganer möchte 'Gemüse-Döner' ohne Gemüse, nur Soße."),
    ("warn", "Zwiebeln fehlen! Notfalllieferung wurde bestellt."),
    ("success", "Lokale Zeitung: 'Beste Pommes in der Stadt' - Ihr verkauft keinen."),
    ("info", "Azubi Cem hat zum dritten Mal das Besteck verloren."),
    ("warn", "Das Schild 'FRISCH' leuchtet nicht mehr. Kunden misstrauisch."),
    ("success", "Busladung Touristen aus Japan fotografiert jeden Döner!"),
    ("info", "Kundenbewertung: '5 Sterne, weil ich nicht weiter zählen konnte.'"),
    ("warn", "Jemand hat versucht, mit Döner zu bezahlen. Abgelehnt."),
    ("success", "TikTok-Video viral: 'Das ASMR des Dönerschneidens!' +500 Kunden!"),
    ("info", "Regulärer Kunde: 'Kleiner bitte, aber mehr davon.'"),
    ("danger", "Gesundheitsamt kündigt Inspektion an! Schnell aufräumen!"),
    ("success", "Fußballspiel vorbei - Ansturm von 80 Hungrigen!"),
    ("warn", "Schärfste Soße wurde versehentlich als Kinderspeise serviert."),
    ("info", "Wissenschaftler untersuchen: Warum ist Döner nachts besser?"),
    ("success", "Sternekoch besucht dein Lokal: 'Interessant... sehr interessant.'"),
    ("warn", "Strom fällt aus! Alle Grills offline für 2 Stunden."),
    ("info", "Ein Kunde möchte einen 'kleinen Döner' - erklärt 20min seine Vision."),
    ("success", "Radio: 'Bester Döner Deutschlands gefunden!' +1000 Anrufe!"),
    ("danger", "Konkurrenz bietet Gratisgetränke an! Kunden laufen über!"),
]

# Random events
RANDOM_EVENTS = [
    {
        "id": "tiktok_viral",
        "name": "TikTok-Virus!",
        "desc": "Ein Video von deinem Döner geht viral! Massiver Kundenansturm!",
        "effect": {"reputation": 15, "daily_customers": 1.5},
        "duration": 7,
        "probability": 0.002,
        "type": "positive"
    },
    {
        "id": "lebensmittelkontrolle",
        "name": "Lebensmittelkontrolle!",
        "desc": "Das Gesundheitsamt steht vor der Tür! Hygiene wird geprüft!",
        "effect": {"hygiene_check": True},
        "duration": 1,
        "probability": 0.003,
        "type": "negative"
    },
    {
        "id": "fussball_ansturm",
        "name": "Fußballspiel!",
        "desc": "Ein Großes Spiel ist vorbei - massenhaft hungrige Fans!",
        "effect": {"daily_customers": 2.0},
        "duration": 1,
        "probability": 0.005,
        "type": "positive"
    },
    {
        "id": "konkurrenz_eroeffnet",
        "name": "Neue Konkurrenz!",
        "desc": "Ein neuer Dönerladen eröffnet genau gegenüber!",
        "effect": {"daily_customers": 0.8, "reputation": -5},
        "duration": 30,
        "probability": 0.002,
        "type": "negative"
    },
    {
        "id": "stromausfall",
        "name": "Stromausfall!",
        "desc": "Kein Strom - alle Grills aus! Notbetrieb!",
        "effect": {"capacity_mod": 0.2},
        "duration": 1,
        "probability": 0.004,
        "type": "negative"
    },
    {
        "id": "tomaten_knappheit",
        "name": "Tomatenknappheit!",
        "desc": "Tomatenmangel in der Region! Preise steigen!",
        "effect": {"ingredient_cost_mod": {"tomate": 3.0}},
        "duration": 14,
        "probability": 0.003,
        "type": "negative"
    },
    {
        "id": "gute_bewertung",
        "name": "Tripadvisor-Boom!",
        "desc": "100 Fünf-Sterne-Bewertungen über Nacht! Touristen strömen herein!",
        "effect": {"reputation": 10, "daily_customers": 1.3},
        "duration": 14,
        "probability": 0.003,
        "type": "positive"
    },
    {
        "id": "prominenter_besuch",
        "name": "Promi-Besuch!",
        "desc": "Ein bekannter Politiker genießt deinen Döner. Pressefoto!",
        "effect": {"reputation": 20, "daily_customers": 1.4},
        "duration": 7,
        "probability": 0.001,
        "type": "positive"
    },
]

# Sauce popularity tracking
SAUCE_NAMES = {
    "sosse_knoblauch": "Knoblauch",
    "sosse_scharf": "Scharf",
    "sosse_kraeuterkaese": "Kräuterquark",
    "sosse_joghurt": "Joghurt",
    "sosse_tomaten": "Tomate",
}

# Victory conditions
VICTORY_CONDITIONS = {
    "branches_500":     {"desc": "500 Filialen eröffnen",      "target": 500, "field": "total_branches"},
    "marktfuehrer":     {"desc": "Marktführer werden (>40%)",   "target": 0.40, "field": "market_share"},
    "milliarde":        {"desc": "1 Milliarde € Umsatz",        "target": 1_000_000_000, "field": "total_revenue"},
    "europa":           {"desc": "Europaweit expandieren",      "target": 20, "field": "countries"},
}