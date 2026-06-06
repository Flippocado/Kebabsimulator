# DÖNERIMPERIUM™ - Screens
# ==========================
from __future__ import annotations
import pygame
import math
import random
import time
from typing import Optional, Callable
from constants import *
from entities import Branch, StaffMember, DoenemRecipe, Supplier
from ui_components import (
    Fonts, Button, Panel, TabBar, ScrollList, NotificationSystem,
    draw_text, draw_rect_rounded, draw_bar, draw_mini_chart,
    draw_doener_icon, draw_gradient_rect, format_money, money_color,
    type_color, lerp_color, Modal
)


# ─────────────────────────────────────────────
#  BASE SCREEN
# ─────────────────────────────────────────────
class Screen:
    def __init__(self, game):
        self.game = game
        self.gs = game.gs
        self.notif = game.notif

    def handle_event(self, event: pygame.event.Event): pass
    def update(self, dt: float): pass
    def draw(self, surf: pygame.Surface): pass


# ─────────────────────────────────────────────
#  MAIN MENU SCREEN
# ─────────────────────────────────────────────
class MainMenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self._anim = 0.0
        self._particles = [self._make_particle() for _ in range(40)]
        cw, ch = SCREEN_W() // 2, SCREEN_H() // 2

        self.btn_new = Button((cw - 140, ch - 10, 280, 50), "Neues Spiel",
                               C_GOLD, C_BG, callback=self._new_game)
        self.btn_load = Button((cw - 140, ch + 70, 280, 50), "Spiel laden",
                                C_ORANGE, C_BG, callback=self._load_game)
        self.btn_quit = Button((cw - 140, ch + 150, 280, 50), "Beenden",
                                C_RED, C_WHITE, callback=self._quit)
        self.btn_load.enabled = any(game.gs.save_exists(i) for i in range(3))

        self._company_name = ""
        self._enter_name = False
        self._name_input = ""

    def _make_particle(self):
        return {
            "x": random.uniform(0, SCREEN_W()),
            "y": random.uniform(0, SCREEN_H()),
            "vx": random.uniform(-20, 20),
            "vy": random.uniform(-40, -10),
            "size": random.uniform(2, 6),
            "color": random.choice([C_GOLD, C_ORANGE, C_RED, C_GREEN]),
            "life": random.uniform(0, 3),
            "max_life": random.uniform(2, 5),
        }

    def handle_event(self, event):
        if self._enter_name:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and self._name_input.strip():
                    self.game.pending_company_name = self._name_input.strip()
                    self.game.set_screen("difficulty")
                elif event.key == pygame.K_ESCAPE:
                    self._enter_name = False
                    self._name_input = ""
                elif event.key == pygame.K_BACKSPACE:
                    self._name_input = self._name_input[:-1]
                else:
                    if len(self._name_input) < 30 and event.unicode.isprintable():
                        self._name_input += event.unicode
            return

        self.btn_new.handle_event(event)
        self.btn_load.handle_event(event)
        self.btn_quit.handle_event(event)

    def _new_game(self):
        self._enter_name = True
        self._name_input = "DÖNERIMPERIUM™"

    def _load_game(self):
        self.game.set_screen("load_menu")

    def _quit(self):
        self.game.running = False

    def update(self, dt):
        self._anim += dt
        for p in self._particles:
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["life"] += dt
            if p["life"] >= p["max_life"] or p["y"] < -10:
                p.update(self._make_particle())
                p["y"] = SCREEN_H() + 10

    def draw(self, surf):
        fonts = Fonts.get()
        # Background
        draw_gradient_rect(surf, (0, 0, SCREEN_W(), SCREEN_H()), C_BG, (30, 20, 10))

        # Particles
        for p in self._particles:
            alpha = 1.0 - p["life"] / p["max_life"]
            size = int(p["size"])
            if size > 0:
                pygame.draw.circle(surf, p["color"], (int(p["x"]), int(p["y"])), size)

        # Döner icon animated
        draw_doener_icon(surf, SCREEN_W() // 2, 160, 50, self._anim)

        # Title
        title_surf = fonts.title.render("DÖNER", True, C_GOLD)
        title_surf2 = fonts.title.render("IMPERIUM™", True, C_ORANGE)
        tw = title_surf.get_width()
        tw2 = title_surf2.get_width()
        surf.blit(title_surf, (SCREEN_W() // 2 - tw // 2, 230))
        surf.blit(title_surf2, (SCREEN_W() // 2 - tw2 // 2, 295))

        # Subtitle
        draw_text(surf, "Baue das größte Döner-Imperium der Welt!", fonts.md, C_TEXT2,
                  SCREEN_W() // 2, 370, "center")

        # Name input dialog
        if self._enter_name:
            overlay = pygame.Surface((SCREEN_W(), SCREEN_H()), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 140))
            surf.blit(overlay, (0, 0))
            bw, bh = 460, 180
            bx = SCREEN_W() // 2 - bw // 2
            by = SCREEN_H() // 2 - bh // 2
            draw_rect_rounded(surf, C_PANEL, (bx, by, bw, bh), 10, 2, C_GOLD)
            draw_text(surf, "Firmenname eingeben:", fonts.md, C_GOLD,
                      SCREEN_W() // 2, by + 30, "center")
            # Input box
            inp_rect = pygame.Rect(bx + 20, by + 65, bw - 40, 40)
            draw_rect_rounded(surf, C_BG2, inp_rect, 6, 1, C_GOLD)
            cursor = "|" if int(self._anim * 2) % 2 == 0 else ""
            draw_text(surf, self._name_input + cursor, fonts.md, C_WHITE,
                      inp_rect.x + 10, inp_rect.centery, "midleft")
            draw_text(surf, "ENTER = Starten   ESC = Abbrechen", fonts.xs, C_GRAY,
                      SCREEN_W() // 2, by + 140, "center")
            return

        # Buttons
        self.btn_new.draw(surf)
        self.btn_load.draw(surf)
        self.btn_quit.draw(surf)

        # Version
        draw_text(surf, "v1.0 | DÖNERIMPERIUM™  2026", fonts.xxs, C_GRAY,
                  SCREEN_W() // 2, SCREEN_H() - 20, "center")



# ─────────────────────────────────────────────
#  DIFFICULTY SCREEN
# ─────────────────────────────────────────────
DIFFICULTIES = [
    {
        "key": "easy",
        "label": "Einfach",
        "desc": "Kunden sind nachsichtig, Hygiene hält länger, Events seltener. Zum Reinschnuppern.",
        "icon": "🟢",
        "color": (80, 200, 80),
    },
    {
        "key": "normal",
        "label": "Normal",
        "desc": "Ausgewogene Herausforderung. Der klassische Döner-Weg.",
        "icon": "🟡",
        "color": C_GOLD,
    },
    {
        "key": "hard",
        "label": "Schwer",
        "desc": "Kunden sind anspruchsvoll, Hygiene verfällt schnell, Konkurrenz aggressiver.",
        "icon": "🔴",
        "color": C_RED,
    },
]

class DifficultyScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self._selected = 1  # Normal default
        cw, ch = SCREEN_W() // 2, SCREEN_H() // 2
        self.btn_back = Button((cw - 140, ch + 200, 130, 45), "Zurück",
                                C_PANEL2, C_TEXT, callback=lambda: game.set_screen("main_menu"))
        self.btn_start = Button((cw + 10, ch + 200, 130, 45), "Starten!",
                                 C_GOLD, C_BG, callback=self._start)

    def _start(self):
        diff = DIFFICULTIES[self._selected]
        self.game.start_new_game(self.game.pending_company_name, diff)

    def handle_event(self, event):
        self.btn_back.handle_event(event)
        self.btn_start.handle_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self._selected = max(0, self._selected - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self._selected = min(len(DIFFICULTIES) - 1, self._selected + 1)
            elif event.key == pygame.K_RETURN:
                self._start()
            elif event.key == pygame.K_ESCAPE:
                self.game.set_screen("main_menu")
        if event.type == pygame.MOUSEBUTTONDOWN:
            for i, card in enumerate(self._card_rects):
                if card.collidepoint(event.pos):
                    self._selected = i

    def update(self, dt):
        pass

    def draw(self, surf):
        fonts = Fonts.get()
        draw_gradient_rect(surf, (0, 0, SCREEN_W(), SCREEN_H()), C_BG, (30, 20, 10))

        draw_text(surf, "Schwierigkeitsgrad wählen", fonts.lg, C_GOLD,
                  SCREEN_W() // 2, 120, "center")
        name = getattr(self.game, "pending_company_name", "")
        draw_text(surf, f"Firma: {name}", fonts.md, C_TEXT2,
                  SCREEN_W() // 2, 175, "center")

        cw, ch = SCREEN_W() // 2, SCREEN_H() // 2
        card_w, card_h = 220, 190
        gap = 30
        total_w = len(DIFFICULTIES) * card_w + (len(DIFFICULTIES) - 1) * gap
        start_x = cw - total_w // 2
        self._card_rects = []

        for i, d in enumerate(DIFFICULTIES):
            cx = start_x + i * (card_w + gap)
            cy = ch - card_h // 2 - 20
            rect = pygame.Rect(cx, cy, card_w, card_h)
            self._card_rects.append(rect)
            is_sel = i == self._selected
            border_col = d["color"] if is_sel else C_PANEL2
            border_w = 3 if is_sel else 1
            bg_col = (40, 35, 25) if is_sel else C_PANEL
            draw_rect_rounded(surf, bg_col, rect, 10, border_w, border_col)

            # Label
            draw_text(surf, d["label"], fonts.lg, d["color"], cx + card_w // 2, cy + 35, "center")

            # Desc
            words = d["desc"].split()
            line, lines = "", []
            for w in words:
                test = (line + " " + w).strip()
                if fonts.xs.size(test)[0] < card_w - 20:
                    line = test
                else:
                    lines.append(line); line = w
            if line: lines.append(line)
            for j, ln in enumerate(lines):
                draw_text(surf, ln, fonts.xs, C_GRAY,
                          cx + card_w // 2, cy + 140 + j * 18, "center")

            if is_sel:
                pygame.draw.polygon(surf, d["color"], [
                    (cx + card_w // 2 - 10, cy - 14),
                    (cx + card_w // 2 + 10, cy - 14),
                    (cx + card_w // 2, cy - 4),
                ])

        self.btn_back.draw(surf)
        self.btn_start.draw(surf)
        draw_text(surf, "← → zum Wechseln   ENTER zum Starten", fonts.xs, C_GRAY,
                  SCREEN_W() // 2, SCREEN_H() - 25, "center")

# ─────────────────────────────────────────────
#  LOAD MENU SCREEN
# ─────────────────────────────────────────────
class LoadMenuScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self._slots: list[Optional[dict]] = []
        self._load_slots()
        self._btns_load = []
        self._btn_back = Button((20, 20, 100, 36), "← Zurück",
                                 C_PANEL2, C_TEXT, callback=lambda: self.game.set_screen("main_menu"))
        for i in range(3):
            self._btns_load.append(
                Button((SCREEN_W() // 2 - 150, 200 + i * 120, 300, 50),
                       f"Slot {i+1} laden", C_ORANGE, C_BG,
                       callback=self._make_load_cb(i))
            )
            self._btns_load[i].enabled = self._slots[i] is not None

    def _make_load_cb(self, slot: int):
        def cb():
            self.game.load_game(slot)
        return cb

    def _load_slots(self):
        from gamestate import GameState
        self._slots = []
        for i in range(3):
            if GameState.save_exists(i):
                gs = GameState.load(i)
                self._slots.append({
                    "day": gs.day, "money": gs.money,
                    "branches": len(gs.branches),
                    "company": gs.company_name
                })
            else:
                self._slots.append(None)

    def handle_event(self, event):
        self._btn_back.handle_event(event)
        for btn in self._btns_load:
            btn.handle_event(event)

    def draw(self, surf):
        fonts = Fonts.get()
        draw_gradient_rect(surf, (0, 0, SCREEN_W(), SCREEN_H()), C_BG, (30, 20, 10))
        draw_text(surf, "Spielstand laden", fonts.lg, C_GOLD, SCREEN_W() // 2, 80, "center")

        for i, (slot, btn) in enumerate(zip(self._slots, self._btns_load)):
            y = 200 + i * 120
            panel_rect = (SCREEN_W() // 2 - 200, y - 20, 400, 100)
            draw_rect_rounded(surf, C_PANEL, panel_rect, 8, 1, C_BORDER)
            if slot:
                draw_text(surf, f"Slot {i+1}: {slot['company']}", fonts.md, C_GOLD,
                          SCREEN_W() // 2, y, "center")
                draw_text(surf, f"Tag {slot['day']} | {format_money(slot['money'])} | {slot['branches']} Filialen",
                          fonts.sm, C_TEXT2, SCREEN_W() // 2, y + 28, "center")
            else:
                draw_text(surf, f"Slot {i+1}: Leer", fonts.md, C_GRAY,
                          SCREEN_W() // 2, y + 14, "center")
            btn.draw(surf)

        self._btn_back.draw(surf)


# ─────────────────────────────────────────────
#  HUD (Persistent Top Bar)
# ─────────────────────────────────────────────
class HUD:
    def __init__(self, game):
        self.game = game
        self._anim = 0.0
        self._last_size = (0, 0)
        self.btn_pause = None
        self.btn_achievements = None
        self.btn_1x = None
        self.btn_2x = None
        self.btn_3x = None
        self._nav_btns = []
        self._rebuild_buttons()

    def _rebuild_buttons(self):
        bw = 34
        self.btn_achievements = Button((SCREEN_W() - 260, 8, 90, 28), "Achievements", C_PANEL2, C_GOLD,
                                        callback=lambda: self.game.set_screen("achievements"))
        self.btn_pause = Button((SCREEN_W() - 160, 8, bw, 28), "⏸", C_PANEL2, C_GOLD,
                                 callback=self._toggle_pause)
        self.btn_1x = Button((SCREEN_W() - 122, 8, bw, 28), "1x", C_PANEL2, C_TEXT,
                               callback=lambda: self._set_speed(1.0))
        self.btn_2x = Button((SCREEN_W() - 84, 8, bw, 28), "2x", C_PANEL2, C_TEXT,
                               callback=lambda: self._set_speed(3.0))
        self.btn_3x = Button((SCREEN_W() - 46, 8, bw, 28), "3x", C_PANEL2, C_TEXT,
                               callback=lambda: self._set_speed(8.0))
        nav_y = 44
        nav_h = 30
        nav_labels = ["🏠 Übersicht", "🏪 Filialen", "👥 Personal", "🔬 Forschung",
                       "📊 Statistiken", "💰 Finanzen", "⚙ Optionen"]
        nav_screens = ["overview", "branches", "staff", "research", "stats", "finance", "options"]
        self._nav_btns = []
        nw = (SCREEN_W() - 20) // len(nav_labels)
        for i, (lbl, scr) in enumerate(zip(nav_labels, nav_screens)):
            def make_cb(s):
                return lambda: self.game.set_screen(s)
            self._nav_btns.append(
                Button((10 + i * nw, nav_y, nw - 4, nav_h), lbl, C_PANEL2, C_TEXT2,
                       font=Fonts.get().xs, callback=make_cb(scr))
            )
        self._last_size = (SCREEN_W(), SCREEN_H())

    def _toggle_pause(self):
        gs = self.game.gs
        gs.paused = not gs.paused
        self.btn_pause.label = "▶" if gs.paused else "⏸"

    def _set_speed(self, spd: float):
        self.game.gs.game_speed = spd

    def handle_event(self, event):
        self.btn_pause.handle_event(event)
        self.btn_achievements.handle_event(event)
        self.btn_1x.handle_event(event)
        self.btn_2x.handle_event(event)
        self.btn_3x.handle_event(event)
        for btn in self._nav_btns:
            btn.handle_event(event)

    def update(self, dt):
        self._anim += dt
        # Rebuild buttons if window was resized
        if (SCREEN_W(), SCREEN_H()) != self._last_size:
            self._rebuild_buttons()

    def draw(self, surf):
        fonts = Fonts.get()
        gs = self.game.gs
        # Top bar background
        bar_rect = pygame.Rect(0, 0, SCREEN_W(), 78)
        draw_gradient_rect(surf, bar_rect, C_PANEL, C_BG2)
        pygame.draw.line(surf, C_BORDER, (0, 78), (SCREEN_W(), 78))
        pygame.draw.line(surf, C_GOLD, (0, 42), (SCREEN_W(), 42), 1)

        # Company name
        draw_text(surf, gs.company_name, fonts.md, C_GOLD, 10, 14, "midleft")

        # Money
        mc = money_color(gs.money)
        draw_text(surf, format_money(gs.money), fonts.md, mc, 300, 14, "midleft")

        # Day / Time
        time_str = f"Tag {gs.day} | {gs.hour:02d}:{gs.minute:02d}"
        draw_text(surf, time_str, fonts.sm, C_TEXT2, 500, 14, "midleft")

        # Branch count
        draw_text(surf, f"🏪 {len(gs.branches)} Filialen", fonts.sm, C_TEXT2, 670, 14, "midleft")

        # Speed indicator
        spd_color = C_GOLD if not gs.paused else C_RED
        spd_str = "PAUSE" if gs.paused else f"{gs.game_speed:.0f}x"
        draw_text(surf, spd_str, fonts.sm, spd_color, SCREEN_W() - 170, 14, "midleft")

        self.btn_pause.draw(surf)
        self.btn_achievements.draw(surf)
        self.btn_1x.draw(surf)
        self.btn_2x.draw(surf)
        self.btn_3x.draw(surf)

        # Nav buttons
        current = self.game.current_screen_name
        for i, btn in enumerate(self._nav_btns):
            scr = ["overview", "branches", "staff", "research", "stats", "finance", "options"][i]
            btn.color = lerp_color(C_GOLD, C_PANEL2, 0.5) if scr == current else C_PANEL2
            btn.draw(surf)



# ─────────────────────────────────────────────
#  ACHIEVEMENTS SCREEN
# ─────────────────────────────────────────────

ACHIEVEMENTS = [
    # Serious
    {"id": "first_branch",      "name": "Der Anfang",           "desc": "Erste Filiale eröffnet.",                          "icon": "🏪", "check": lambda gs: len(gs.branches) >= 1},
    {"id": "five_branches",     "name": "Kleine Kette",         "desc": "5 Filialen gleichzeitig offen.",                   "icon": "🏪", "check": lambda gs: len(gs.branches) >= 5},
    {"id": "ten_branches",      "name": "Döner-Dynastie",       "desc": "10 Filialen. Respekt.",                            "icon": "👑", "check": lambda gs: len(gs.branches) >= 10},
    {"id": "milliardaer",       "name": "Döner-Milliardär",     "desc": "1 Milliarde € Gesamtumsatz.",                      "icon": "💰", "check": lambda gs: gs.total_revenue >= 1_000_000_000},
    {"id": "marktfuehrer",      "name": "Marktführer",          "desc": "Über 40% Marktanteil.",                            "icon": "📈", "check": lambda gs: gs.market_share >= 0.4},
    {"id": "europa",            "name": "Döner ohne Grenzen",   "desc": "In 5 Ländern vertreten.",                          "icon": "🌍", "check": lambda gs: len(gs.countries_present) >= 5},
    {"id": "million_kunden",    "name": "Eine Million Kunden",  "desc": "1.000.000 Kunden bedient.",                        "icon": "🧑‍🤝‍🧑", "check": lambda gs: gs.total_customers_served >= 1_000_000},
    # Lustig
    {"id": "knoblauch_king",    "name": "Knoblauch-König",      "desc": "500.000x Knoblauchsoße verkauft. Deine Nachbarn leiden.",  "icon": "🧄", "check": lambda gs: sum(b.sauce_popularity.get("sosse_knoblauch",0) for b in gs.branches) >= 500_000},
    {"id": "broke",             "name": "Döner auf Pump",       "desc": "Kontostand unter 100€. Läuft.",                    "icon": "💸", "check": lambda gs: gs.money < 100},
    {"id": "insomnia",          "name": "Döner schläft nie",    "desc": "Tag 365 erreicht. Ein ganzes Jahr Döner.",          "icon": "😴", "check": lambda gs: gs.day >= 365},
    {"id": "schnell",           "name": "Flash-Döner",          "desc": "8x Spielgeschwindigkeit aktiviert.",                "icon": "⚡", "check": lambda gs: gs.game_speed >= 8.0},
    {"id": "hygiene_zero",      "name": "Gesundheitsamt-Albtraum", "desc": "Hygiene einer Filiale auf 0. Mutig.",           "icon": "🦠", "check": lambda gs: any(b.hygiene <= 0 for b in gs.branches)},
    {"id": "three_countries",   "name": "Weltenbummler",        "desc": "In 3 Ländern eröffnet.",                           "icon": "✈️", "check": lambda gs: len(gs.countries_present) >= 3},
    {"id": "flughafen_only",    "name": "Mile-High Döner",      "desc": "3 Flughafen-Filialen gleichzeitig.",               "icon": "🛫", "check": lambda gs: sum(1 for b in gs.branches if b.location_type == "flughafen") >= 3},
    {"id": "all_research",      "name": "Döner-Wissenschaftler","desc": "Alle Forschungen abgeschlossen.",                  "icon": "🔬", "check": lambda gs: all(n.unlocked for n in gs.research_tree.values())},
    {"id": "no_loan",           "name": "Schuldenfrei",         "desc": "Kredit vollständig abbezahlt.",                    "icon": "🕊️", "check": lambda gs: gs.loan_debt <= 0 and gs.total_revenue > 0},
    {"id": "tausend_tage",      "name": "Rentner des Döners",   "desc": "Tag 1000. Du brauchst Urlaub.",                    "icon": "🏖️", "check": lambda gs: gs.day >= 1000},
    {"id": "paris",             "name": "Döner à Paris",        "desc": "Filiale in Paris eröffnet.",                       "icon": "🗼", "check": lambda gs: any(b.city == "Paris" for b in gs.branches)},
    {"id": "five_staff",        "name": "Personalchef",         "desc": "20 Mitarbeiter gleichzeitig beschäftigt.",         "icon": "👥", "check": lambda gs: sum(len(b.staff) for b in gs.branches) >= 20},
    {"id": "rep_100",           "name": "Legendärer Ruf",       "desc": "Reputation 100 in einer Filiale.",                 "icon": "⭐", "check": lambda gs: any(b.reputation >= 100 for b in gs.branches)},
    # Noch mehr
    {"id": "sosse_all",         "name": "Soßen-Sommelier",      "desc": "Alle 5 Soßen gleichzeitig im Angebot.",             "icon": "🫙", "check": lambda gs: any(len([r for r in b.recipes if r.sosse]) >= 5 for b in gs.branches)},
    {"id": "schweiz",           "name": "Käse trifft Döner",     "desc": "Filiale in der Schweiz eröffnet.",                  "icon": "🇨🇭", "check": lambda gs: any(b.country == "Schweiz" for b in gs.branches)},
    {"id": "spanien",           "name": "Hola Döner!",           "desc": "Filiale in Spanien eröffnet.",                      "icon": "🇪🇸", "check": lambda gs: any(b.country == "Spanien" for b in gs.branches)},
    {"id": "italien",           "name": "Mamma mia, Döner!",     "desc": "Filiale in Italien eröffnet.",                      "icon": "🇮🇹", "check": lambda gs: any(b.country == "Italien" for b in gs.branches)},
    {"id": "frankreich",        "name": "Sacré Döner!",          "desc": "Filiale in Frankreich eröffnet.",                   "icon": "🇫🇷", "check": lambda gs: any(b.country == "Frankreich" for b in gs.branches)},
    {"id": "100_tage",          "name": "Überlebt!",             "desc": "100 Tage durchgehalten.",                           "icon": "📅", "check": lambda gs: gs.day >= 100},
    {"id": "500_tage",          "name": "Halbzeit?",             "desc": "500 Tage. Wann schläfst du eigentlich?",             "icon": "😵", "check": lambda gs: gs.day >= 500},
    {"id": "zehn_mio",          "name": "Zehn Millionen!",       "desc": "10.000.000€ Gesamtumsatz.",                         "icon": "💵", "check": lambda gs: gs.total_revenue >= 10_000_000},
    {"id": "hundert_mio",       "name": "Hundert Millionen!",    "desc": "100.000.000€ Umsatz. Fast Milliardär.",             "icon": "💎", "check": lambda gs: gs.total_revenue >= 100_000_000},
    {"id": "zehn_mio_kunden",   "name": "Völkerwanderung",       "desc": "10 Millionen Kunden bedient.",                      "icon": "🌊", "check": lambda gs: gs.total_customers_served >= 10_000_000},
    {"id": "scharf_fanatic",    "name": "Feuer-Enthusiast",      "desc": "500.000x Scharfe Soße verkauft. Deine Toilette weint.", "icon": "🌶️", "check": lambda gs: sum(b.sauce_popularity.get("sosse_scharf",0) for b in gs.branches) >= 500_000},
    {"id": "reich",             "name": "Dagobert Duck",         "desc": "10.000.000€ auf dem Konto.",                        "icon": "🦆", "check": lambda gs: gs.money >= 10_000_000},
    {"id": "mega_reich",        "name": "Döner-Elon",            "desc": "100.000.000€ auf dem Konto.",                       "icon": "🚀", "check": lambda gs: gs.money >= 100_000_000},
    {"id": "einkaufszentrum3",  "name": "Shopping-König",        "desc": "3 Einkaufszentrum-Filialen gleichzeitig.",           "icon": "🛍️", "check": lambda gs: sum(1 for b in gs.branches if b.location_type == "einkaufszentrum") >= 3},
    {"id": "azubi_armee",       "name": "Ausbildungsbetrieb",    "desc": "5 Azubis gleichzeitig beschäftigt.",                "icon": "🎓", "check": lambda gs: sum(1 for b in gs.branches for s in b.staff if s.stype == "azubi") >= 5},
    {"id": "kein_kredit",       "name": "Banker hasst ihn",      "desc": "Nie einen Kredit aufgenommen.",                     "icon": "🙅", "check": lambda gs: gs.loan_debt == 0 and gs.total_revenue > 0, "permanent": False},
    {"id": "franchise3",        "name": "Franchise-König",       "desc": "3 Franchise-Filialen gleichzeitig.",                "icon": "📜", "check": lambda gs: sum(1 for b in gs.branches if b.is_franchise) >= 3},
    {"id": "alle_research",     "name": "Alles erforscht!",      "desc": "Kompletten Forschungsbaum abgeschlossen.",           "icon": "🧪", "check": lambda gs: all(n.unlocked for n in gs.research_tree.values())},
    {"id": "speed_demon",       "name": "YOLO-Modus",            "desc": "8x Spielgeschwindigkeit UND 50 Filialen gleichzeitig.", "icon": "💨", "check": lambda gs: gs.game_speed >= 8.0 and len(gs.branches) >= 50},
    # Noch mehr
    {"id": "nacht_schicht",      "name": "Nachtschicht",          "desc": "Um 3 Uhr nachts noch Kunden bedient.",              "icon": "🌙", "check": lambda gs: gs.hour == 3 and gs.total_customers_served > 0},
    {"id": "doenerhausen_only",  "name": "Lokalpatriot",          "desc": "5 Filialen in Dönerhausen.",                        "icon": "🏘️", "check": lambda gs: sum(1 for b in gs.branches if b.city == "Dönerhausen") >= 5},
    {"id": "frankfurt_boss",     "name": "Frankfurt-Boss",        "desc": "5 Filialen in Frankfurt.",                          "icon": "🏙️", "check": lambda gs: sum(1 for b in gs.branches if b.city == "Frankfurt") >= 5},
    {"id": "wiesbaden_boss",     "name": "Wiesbaden-Dominator",   "desc": "3 Filialen in Wiesbaden.",                          "icon": "🌆", "check": lambda gs: sum(1 for b in gs.branches if b.city == "Wiesbaden") >= 3},
    {"id": "guenstig",           "name": "Discounter-König",      "desc": "Preis unter 5€ in einer Filiale.",                  "icon": "🏷️", "check": lambda gs: any(r.price < 5.0 for b in gs.branches for r in b.recipes)},
    {"id": "teuer",              "name": "Premium-Döner",         "desc": "Preis über 12€. Wer kauft das??",                   "icon": "🎩", "check": lambda gs: any(r.price > 12.0 for b in gs.branches for r in b.recipes)},
    {"id": "keine_reiniger",     "name": "Chaos-Filiale",         "desc": "Filiale ohne Reiniger betreiben.",                  "icon": "🗑️", "check": lambda gs: any(not any(s.stype == "reiniger" for s in b.staff) for b in gs.branches)},
    {"id": "reiniger_armee",     "name": "Putz-Imperium",         "desc": "10 Reiniger gleichzeitig beschäftigt.",             "icon": "🧹", "check": lambda gs: sum(1 for b in gs.branches for s in b.staff if s.stype == "reiniger") >= 10},
    {"id": "low_morale",         "name": "Terrible Boss",         "desc": "Mitarbeiter-Moral unter 20% irgendwo.",             "icon": "😤", "check": lambda gs: any(s.morale < 0.2 for b in gs.branches for s in b.staff)},
    {"id": "high_morale",        "name": "Bester Chef",           "desc": "Alle Mitarbeiter über 90% Moral.",                  "icon": "🥳", "check": lambda gs: all(s.morale >= 0.9 for b in gs.branches for s in b.staff) and gs.total_customers_served > 0},
    {"id": "viral_dreimal",      "name": "TikTok-Star",           "desc": "3x TikTok viral gegangen.",                         "icon": "📱", "check": lambda gs: sum(1 for b in gs.branches for e in b.active_events if e["id"] == "tiktok_viral") >= 3},
    {"id": "pleite_fast",        "name": "Auf der Kippe",         "desc": "Kontostand unter 0€ überlebt.",                     "icon": "😰", "check": lambda gs: gs.money < 0 and gs.total_revenue > 0},
    {"id": "fuenf_laender",      "name": "Weltkonzern",           "desc": "In 5 verschiedenen Ländern aktiv.",                 "icon": "🌐", "check": lambda gs: len(gs.countries_present) >= 5},
    {"id": "rezept_5",           "name": "Rezept-Meister",        "desc": "5 verschiedene Rezepte in einer Filiale.",           "icon": "📋", "check": lambda gs: any(len(b.recipes) >= 5 for b in gs.branches)},
    {"id": "alles_marketing",    "name": "Marketing-Wahnsinn",    "desc": "Alle Marketing-Optionen einer Filiale aktiv.",       "icon": "📣", "check": lambda gs: any(all(b.marketing.values()) for b in gs.branches)},
    {"id": "25_filialen",        "name": "Ketten-Reaktion",       "desc": "25 Filialen gleichzeitig.",                         "icon": "⛓️", "check": lambda gs: len(gs.branches) >= 25},
    {"id": "50_filialen",        "name": "Halb-Tausend",          "desc": "50 Filialen gleichzeitig.",                         "icon": "🏗️", "check": lambda gs: len(gs.branches) >= 50},
    {"id": "100_filialen",       "name": "Jahrhundert-Kette",     "desc": "100 Filialen. Döner-McDonalds.",                    "icon": "💯", "check": lambda gs: len(gs.branches) >= 100},
    {"id": "joghurt_fan",        "name": "Joghurt-Junkie",        "desc": "100.000x Joghurt-Soße verkauft.",                   "icon": "🥛", "check": lambda gs: sum(b.sauce_popularity.get("sosse_joghurt",0) for b in gs.branches) >= 100_000},
    {"id": "kraeuterkaese_fan",  "name": "Kräuter-Hexe",          "desc": "100.000x Kräuterquark-Soße verkauft.",              "icon": "🌿", "check": lambda gs: sum(b.sauce_popularity.get("sosse_kraeuterkaese",0) for b in gs.branches) >= 100_000},
    {"id": "tomaten_fan",        "name": "Tomate-Enthusiast",     "desc": "100.000x Tomaten-Soße verkauft.",                   "icon": "🍅", "check": lambda gs: sum(b.sauce_popularity.get("sosse_tomaten",0) for b in gs.branches) >= 100_000},
    {"id": "senior_staff",       "name": "Erfahrungsstufe Max",   "desc": "Mitarbeiter mit Erfahrung 10 beschäftigt.",          "icon": "🧓", "check": lambda gs: any(s.experience >= 10 for b in gs.branches for s in b.staff)},
    {"id": "hundert_mitarbeiter","name": "Konzern-HR",            "desc": "100 Mitarbeiter gleichzeitig.",                     "icon": "👔", "check": lambda gs: sum(len(b.staff) for b in gs.branches) >= 100},
    {"id": "zwei_milliarden",    "name": "Döner-Bezos",           "desc": "2 Milliarden € Gesamtumsatz.",                      "icon": "🛸", "check": lambda gs: gs.total_revenue >= 2_000_000_000},
    {"id": "promi_besuche",      "name": "VIP-Lounge",            "desc": "3x Promi-Besuch gehabt.",                           "icon": "🤵", "check": lambda gs: sum(1 for b in gs.branches for e in b.active_events if e["id"] == "prominenter_besuch") >= 3},
]

class AchievementsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self._scroll = 0
        cw = SCREEN_W() // 2
        self.btn_back = Button((cw - 80, SCREEN_H() - 55, 160, 40), "← Zurück",
                                C_PANEL2, C_TEXT, callback=self._go_back)
        self._prev_screen = "overview"

    def _go_back(self):
        self.game.set_screen(self._prev_screen)

    def handle_event(self, event):
        self.btn_back.handle_event(event)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self._go_back()
        if event.type == pygame.MOUSEWHEEL:
            self._scroll = max(0, self._scroll - event.y * 30)

    def update(self, dt):
        pass

    def draw(self, surf):
        fonts = Fonts.get()
        gs = self.game.gs
        draw_gradient_rect(surf, (0, 0, SCREEN_W(), SCREEN_H()), C_BG, (20, 15, 10))

        draw_text(surf, "Achievements", fonts.lg, C_GOLD, SCREEN_W() // 2, 95, "center")

        # Check which are unlocked (persistent)
        unlocked = []
        locked = []
        for ach in ACHIEVEMENTS:
            if ach["id"] in gs.unlocked_achievements:
                unlocked.append(ach)
            else:
                locked.append(ach)

        draw_text(surf, f"{len(unlocked)} / {len(ACHIEVEMENTS)} freigeschaltet", fonts.sm, C_TEXT2,
                  SCREEN_W() // 2, 125, "center")

        cols = 2
        card_w = (SCREEN_W() - 60) // cols
        card_h = 72
        gap = 10
        start_y = 150 - self._scroll
        all_achs = unlocked + locked

        max_scroll = max(0, ((len(all_achs) + cols - 1) // cols) * (card_h + gap) - (SCREEN_H() - 220))
        self._scroll = min(self._scroll, max_scroll)

        clip = pygame.Rect(0, 145, SCREEN_W(), SCREEN_H() - 210)
        surf.set_clip(clip)

        for i, ach in enumerate(all_achs):
            col = i % cols
            row = i // cols
            cx = 20 + col * (card_w + gap)
            cy = start_y + row * (card_h + gap)
            if cy + card_h < 145 or cy > SCREEN_H() - 65:
                continue
            is_done = ach in unlocked
            bg = (40, 38, 20) if is_done else (25, 25, 25)
            border = C_GOLD if is_done else C_PANEL2
            draw_rect_rounded(surf, bg, pygame.Rect(cx, cy, card_w, card_h), 8, 2, border)
            # Icon
            icon_col = C_GOLD if is_done else C_GRAY
            draw_text(surf, ach["icon"], fonts.lg, icon_col, cx + 36, cy + card_h // 2, "center")
            # Name
            name_col = C_GOLD if is_done else C_TEXT2
            draw_text(surf, ach["name"], fonts.sm, name_col, cx + 62, cy + 18, "midleft")
            # Desc
            draw_text(surf, ach["desc"], fonts.xs, C_GRAY if not is_done else C_TEXT2, cx + 62, cy + 40, "midleft")
            if is_done:
                draw_text(surf, "✓", fonts.md, (80, 220, 80), cx + card_w - 20, cy + card_h // 2, "center")

        surf.set_clip(None)
        self.btn_back.draw(surf)

# ─────────────────────────────────────────────
#  OVERVIEW SCREEN
# ─────────────────────────────────────────────
class OverviewScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self._anim = 0.0

    def update(self, dt):
        self._anim += dt

    def draw(self, surf):
        fonts = Fonts.get()
        gs = self.game.gs
        y0 = 85

        # Title
        draw_text(surf, "📊 Unternehmensübersicht", fonts.lg, C_GOLD, 20, y0, "topleft")

        # === LEFT COLUMN: Key Stats ===
        lx, ly = 20, y0 + 45
        panel_rect = (lx, ly, 380, 280)
        draw_rect_rounded(surf, C_PANEL, panel_rect, 8, 1, C_BORDER)
        draw_text(surf, "💰 Finanzkennzahlen", fonts.sm, C_GOLD, lx + 14, ly + 14, "topleft")

        stats = [
            ("Kapital:", format_money(gs.money), money_color(gs.money)),
            ("Gesamtumsatz:", format_money(gs.total_revenue), C_GREEN),
            ("Ausgaben gesamt:", format_money(gs.total_expenses), C_RED2),
            ("Nettogewinn:", format_money(gs.total_revenue - gs.total_expenses), money_color(gs.total_revenue - gs.total_expenses)),
            ("Filialen:", str(len(gs.branches)), C_BLUE2),
            ("Kunden gesamt:", f"{gs.total_customers_served:,}", C_ORANGE),
            ("Marktanteil:", f"{gs.market_share*100:.1f}%", C_TEAL),
            ("Länder:", str(len(gs.countries_present)), C_PURPLE),
        ]
        for i, (label, val, vc) in enumerate(stats):
            row_y = ly + 38 + i * 28
            draw_text(surf, label, fonts.sm, C_TEXT2, lx + 14, row_y, "topleft")
            draw_text(surf, val, fonts.sm, vc, lx + 360, row_y, "topright")
            if i % 2 == 1:
                pygame.draw.rect(surf, C_BG, (lx + 1, row_y - 2, 378, 26), border_radius=2)

        # === MIDDLE COLUMN: Revenue Chart ===
        mx, my = 420, y0 + 45
        draw_rect_rounded(surf, C_PANEL, (mx, my, 410, 130), 8, 1, C_BORDER)
        draw_text(surf, "📈 Tagesumsatz (30 Tage)", fonts.sm, C_GOLD, mx + 14, my + 10, "topleft")
        draw_mini_chart(surf, gs.revenue_history, (mx + 10, my + 35, 390, 85), C_GREEN)

        draw_rect_rounded(surf, C_PANEL, (mx, my + 145, 410, 130), 8, 1, C_BORDER)
        draw_text(surf, "👥 Kunden/Tag (30 Tage)", fonts.sm, C_GOLD, mx + 14, my + 155, "topleft")
        draw_mini_chart(surf, [float(v) for v in gs.customer_history],
                        (mx + 10, my + 180, 390, 85), C_BLUE)

        # === RIGHT COLUMN: Branch Leaderboard ===
        rx, ry = 850, y0 + 45
        draw_rect_rounded(surf, C_PANEL, (rx, ry, 400, 280), 8, 1, C_BORDER)
        draw_text(surf, "🏆 Top Filialen", fonts.sm, C_GOLD, rx + 14, ry + 14, "topleft")

        sorted_branches = sorted(gs.branches, key=lambda b: b.total_revenue, reverse=True)[:7]
        for i, b in enumerate(sorted_branches):
            row_y = ry + 42 + i * 34
            bar_color = [C_GOLD, C_ORANGE, C_GREEN, C_BLUE, C_TEAL, C_PURPLE, C_RED][i]
            draw_text(surf, f"{i+1}. {b.name}", fonts.sm, C_TEXT, rx + 14, row_y + 2, "topleft")
            draw_text(surf, format_money(b.total_revenue), fonts.sm, bar_color, rx + 385, row_y + 2, "topright")
            draw_bar(surf, rx + 14, row_y + 20, 360, 8,
                     b.total_revenue, max(1, sorted_branches[0].total_revenue) if sorted_branches else 1,
                     bar_color, show_pct=False)

        if not gs.branches:
            draw_text(surf, "Noch keine Filialen! Eröffne deine erste Filiale.", fonts.md, C_GRAY,
                      rx + 200, ry + 140, "center")

        # === BOTTOM: Active Events & Notifications ===
        bx, by2 = 20, y0 + 340
        draw_rect_rounded(surf, C_PANEL, (bx, by2, 820, 220), 8, 1, C_BORDER)
        draw_text(surf, "📢 Ereignisse & Meldungen", fonts.sm, C_GOLD, bx + 14, by2 + 14, "topleft")

        recent = gs.notifications[-8:] if gs.notifications else []
        for i, n in enumerate(reversed(recent)):
            row_y = by2 + 38 + i * 22
            tc = type_color(n.get("type", "info"))
            age = n.get("age", 0)
            alpha_mod = max(0.4, 1.0 - age / 30.0) if age > 5 else 1.0
            tc = tuple(int(c * alpha_mod) for c in tc)
            msg = n["msg"]
            if len(msg) > 90:
                msg = msg[:87] + "..."
            draw_text(surf, f"• {msg}", fonts.xs, tc, bx + 14, row_y, "topleft")

        # Victories
        vx, vy = 850, y0 + 340
        draw_rect_rounded(surf, C_PANEL, (vx, vy, 400, 220), 8, 1, C_BORDER)
        draw_text(surf, "🏆 Siegbedingungen", fonts.sm, C_GOLD, vx + 14, vy + 14, "topleft")

        from constants import VICTORY_CONDITIONS
        conds = [
            ("500 Filialen", len(gs.branches), 500, "branches_500"),
            ("1 Mrd€ Umsatz", gs.total_revenue, 1_000_000_000, "milliarde"),
            ("Marktführer (40%)", gs.market_share, 0.40, "marktfuehrer"),
            ("Europa (20 Länder)", len(gs.countries_present), 20, "europa"),
        ]
        for i, (desc, cur, target, vid) in enumerate(conds):
            row_y = vy + 45 + i * 44
            achieved = vid in gs.victories_achieved
            tc = C_GOLD if achieved else C_TEXT
            pct_str = f"{min(100, cur/target*100):.0f}%"
            icon = "✓" if achieved else "○"
            draw_text(surf, f"{icon} {desc}", fonts.sm, tc, vx + 14, row_y, "topleft")
            draw_text(surf, pct_str, fonts.sm, C_GREEN if achieved else C_GRAY, vx + 385, row_y, "topright")
            draw_bar(surf, vx + 14, row_y + 18, 370, 10,
                     cur, target, C_GOLD if not achieved else C_GREEN, show_pct=False)

        # Döner icon animation in corner
        draw_doener_icon(surf, SCREEN_W() - 60, y0 + 20, 30, self._anim)


# ─────────────────────────────────────────────
#  BRANCHES SCREEN
# ─────────────────────────────────────────────
class BranchesScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self.selected_idx = -1
        self.tab = TabBar((420, 85, 840, 32), ["Info", "Rezept", "Personal", "Marketing", "Lieferkette"])

        # Branch list
        self.branch_list = ScrollList((10, 85, 400, 575), 60)
        self.branch_list.on_select = self._on_branch_select

        # New branch button
        self.btn_new = Button((10, 665, 190, 36), "+ Neue Filiale", C_GOLD, C_BG,
                               callback=self._open_new_branch_dialog)
        self.btn_close_branch = Button((210, 665, 200, 36), "Filiale schließen", C_RED, C_WHITE,
                                        callback=self._close_branch)

        # New branch dialog
        self._dialog: Optional[Modal] = None
        self._new_branch_state = None

        # Recipe editor
        self._edit_recipe_idx = 0
        self._recipe_fields = {}
        self._build_recipe_buttons()

        # Info tab action buttons (positions updated each draw)
        self._btn_toggle_open = Button((430, 200, 200, 36), "Filiale öffnen/schließen",
                                        C_GREEN, C_WHITE, callback=self._toggle_open)
        self._btn_clean = Button((430, 250, 200, 36), "🧹 Reinigen (-150€)",
                                  C_TEAL, C_BG, callback=self._clean_branch)

        # Staff buttons
        self._staff_buttons = []

        # Marketing toggles
        self._mktg_buttons = {}

        self._anim = 0.0

    def _build_recipe_buttons(self):
        rx = 430
        base_y = 130
        self._btn_price_up = Button((rx + 310, base_y + 120, 30, 28), "+", C_GREEN, C_BG,
                                     callback=self._price_up)
        self._btn_price_dn = Button((rx + 270, base_y + 120, 30, 28), "-", C_RED, C_WHITE,
                                     callback=self._price_dn)
        self._btn_fleisch_up = Button((rx + 310, base_y + 155, 30, 28), "+", C_GREEN, C_BG,
                                       callback=lambda: self._menge_change(0.25))
        self._btn_fleisch_dn = Button((rx + 270, base_y + 155, 30, 28), "-", C_RED, C_WHITE,
                                       callback=lambda: self._menge_change(-0.25))
        self._btn_add_recipe = Button((rx, base_y + 320, 150, 32), "+ Rezept hinzufügen",
                                       C_TEAL, C_BG, callback=self._add_recipe)
        self._sauce_btns = {}
        for i, (sk, sn) in enumerate(SAUCE_NAMES.items()):
            def make_cb(key):
                return lambda: self._set_sauce(key)
            self._sauce_btns[sk] = Button((rx + (i % 3) * 110, base_y + 200 + (i // 3) * 36, 105, 30),
                                           sn, C_PANEL2, C_TEXT, font=Fonts.get().xs,
                                           callback=make_cb(sk))

        # Ingredient toggles
        self._ingr_btns = {}
        ingrs = [("salat", "Salat"), ("tomate", "Tomate"), ("zwiebel", "Zwiebel"),
                 ("kraut", "Kraut"), ("gurke", "Gurke")]
        for i, (k, lbl) in enumerate(ingrs):
            def make_cb(key):
                return lambda: self._toggle_ingr(key)
            self._ingr_btns[k] = Button((rx + i * 72, base_y + 275, 68, 28), lbl,
                                         C_PANEL2, C_TEXT, font=Fonts.get().xxs,
                                         callback=make_cb(k))

        # Fleisch type
        self._btn_fleisch_normal = Button((rx, base_y + 190, 150, 28), "Basis-Fleisch",
                                           C_PANEL2, C_TEXT, font=Fonts.get().xs,
                                           callback=lambda: self._set_fleisch("fleisch_basis"))
        self._btn_fleisch_premium = Button((rx + 160, base_y + 190, 150, 28), "Premium-Fleisch",
                                            C_PANEL2, C_TEXT, font=Fonts.get().xs,
                                            callback=lambda: self._set_fleisch("fleisch_premium"))

    def _on_branch_select(self, idx, item):
        self.selected_idx = idx
        self.tab.active = 0
        self._mktg_buttons = {}  # Reset so buttons are rebuilt for the newly selected branch

    def _open_new_branch_dialog(self):
        self._new_branch_state = {
            "phase": "name",
            "name": "",
            "location": "kleinststadt",
            "city": "",
            "country": "Deutschland",
        }

    def _close_branch(self):
        if self.selected_idx >= 0:
            branch = self.gs.branches[self.selected_idx]
            self._dialog = Modal(
                "Filiale schließen?",
                f"Möchtest du '{branch.name}' wirklich schließen?",
                [{"label": "Schließen", "color": C_RED, "result": "close"},
                 {"label": "Abbrechen", "color": C_PANEL2, "result": None}]
            )

    def _price_up(self):
        recipe = self._get_selected_recipe()
        if recipe:
            recipe.price = round(recipe.price + 0.5, 2)

    def _price_dn(self):
        recipe = self._get_selected_recipe()
        if recipe:
            recipe.price = max(0.5, round(recipe.price - 0.5, 2))

    def _menge_change(self, delta: float):
        recipe = self._get_selected_recipe()
        if recipe:
            recipe.fleisch_menge = max(0.5, min(3.0, round(recipe.fleisch_menge + delta, 2)))

    def _set_sauce(self, sk: str):
        recipe = self._get_selected_recipe()
        if recipe:
            recipe.sosse = sk

    def _toggle_ingr(self, key: str):
        recipe = self._get_selected_recipe()
        if recipe:
            setattr(recipe, key, not getattr(recipe, key))

    def _set_fleisch(self, ft: str):
        recipe = self._get_selected_recipe()
        if recipe:
            recipe.fleisch = ft

    def _add_recipe(self):
        if self.selected_idx >= 0 and self.selected_idx < len(self.gs.branches):
            branch = self.gs.branches[self.selected_idx]
            if len(branch.recipes) < 5:
                branch.add_recipe(DoenemRecipe(name=f"Rezept {len(branch.recipes)+1}"))
                self.gs.add_notification(f"Neues Rezept hinzugefügt!", "success")

    def _get_selected_recipe(self) -> Optional[DoenemRecipe]:
        if self.selected_idx >= 0 and self.selected_idx < len(self.gs.branches):
            branch = self.gs.branches[self.selected_idx]
            if branch.recipes:
                return branch.recipes[self._edit_recipe_idx % len(branch.recipes)]
        return None

    def _get_selected_branch(self) -> Optional[Branch]:
        if 0 <= self.selected_idx < len(self.gs.branches):
            return self.gs.branches[self.selected_idx]
        return None

    def handle_event(self, event):
        # Dialog
        if self._dialog:
            self._dialog.handle_event(event)
            if not self._dialog.open:
                if self._dialog.result == "close":
                    if self.selected_idx >= 0:
                        self.gs.close_branch(self.selected_idx)
                        self.selected_idx = -1
                self._dialog = None
            return

        # New branch dialog
        if self._new_branch_state:
            self._handle_new_branch_event(event)
            return

        self.branch_list.handle_event(event)
        self.btn_new.handle_event(event)
        self.btn_close_branch.handle_event(event)

        if self.selected_idx >= 0:
            self.tab.handle_event(event)
            if self.tab.active == 1:  # Recipe tab
                self._btn_price_up.handle_event(event)
                self._btn_price_dn.handle_event(event)
                self._btn_fleisch_up.handle_event(event)
                self._btn_fleisch_dn.handle_event(event)
                self._btn_add_recipe.handle_event(event)
                self._btn_fleisch_normal.handle_event(event)
                self._btn_fleisch_premium.handle_event(event)
                for btn in self._sauce_btns.values():
                    btn.handle_event(event)
                for btn in self._ingr_btns.values():
                    btn.handle_event(event)
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Select recipe by click on tabs
                    branch = self._get_selected_branch()
                    if branch:
                        for ri in range(len(branch.recipes)):
                            rx = 430 + ri * 90
                            ry = 122
                            rr = pygame.Rect(rx, ry, 85, 28)
                            if rr.collidepoint(event.pos):
                                self._edit_recipe_idx = ri
            elif self.tab.active == 2:  # Staff tab
                self._handle_staff_events(event)
            elif self.tab.active == 3:  # Marketing tab
                for key, btn in self._mktg_buttons.items():
                    btn.handle_event(event)
            elif self.tab.active == 0:  # Info tab
                self._handle_info_events(event)
            elif self.tab.active == 4:  # Supply tab
                self._handle_supply_events(event)

    def _handle_supply_events(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        branch = self._get_selected_branch()
        if not branch:
            return
        if hasattr(self, '_supply_rects'):
            for sel_rect, cat, sup, active in self._supply_rects:
                if sel_rect.collidepoint(event.pos):
                    if active:
                        if cat in branch.suppliers:
                            del branch.suppliers[cat]
                        self.gs.add_notification(f"Lieferant abgewählt.", "warn")
                    else:
                        branch.suppliers[cat] = sup
                        self.gs.add_notification(f"Lieferant {sup.name!r} ausgewählt!", "success")
                    self._supply_rects = []
                    break

    def _handle_new_branch_event(self, event):
        ns = self._new_branch_state
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._new_branch_state = None
                return
            if ns["phase"] == "name":
                if event.key == pygame.K_RETURN and ns["name"].strip():
                    ns["phase"] = "city"
                elif event.key == pygame.K_BACKSPACE:
                    ns["name"] = ns["name"][:-1]
                elif event.unicode.isprintable() and len(ns["name"]) < 30:
                    ns["name"] += event.unicode
            elif ns["phase"] == "city":
                if event.key == pygame.K_RETURN and ns["city"].strip():
                    ns["phase"] = "country"
                elif event.key == pygame.K_BACKSPACE:
                    ns["city"] = ns["city"][:-1]
                elif event.unicode.isprintable() and len(ns["city"]) < 30:
                    ns["city"] += event.unicode
            elif ns["phase"] == "country":
                if event.key == pygame.K_RETURN and ns["country"].strip():
                    ns["phase"] = "type"
                elif event.key == pygame.K_BACKSPACE:
                    ns["country"] = ns["country"][:-1]
                elif event.unicode.isprintable() and len(ns["country"]) < 40:
                    ns["country"] += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if ns["phase"] == "type":
                for i, (lt, cfg) in enumerate(LOCATION_TYPES.items()):
                    r = pygame.Rect(SCREEN_W() // 2 - 200, 280 + i * 70, 400, 55)
                    if r.collidepoint(event.pos):
                        ns["location"] = lt
                        cost = cfg["rent"] * 3
                        if self.gs.money >= cost:
                            self.gs.open_branch(ns["name"], lt, ns["city"], ns["country"])
                            self._new_branch_state = None
                        else:
                            self.gs.add_notification(f"Zu wenig Geld! Benötigt: {cost:.0f}€", "danger")
                        return
            # Cancel click outside
            bx, by = SCREEN_W() // 2 - 250, 200
            if not pygame.Rect(bx, by, 500, 500).collidepoint(event.pos):
                self._new_branch_state = None

    def _toggle_open(self):
        branch = self._get_selected_branch()
        if branch:
            branch.is_open = not branch.is_open

    def _clean_branch(self):
        branch = self._get_selected_branch()
        if branch:
            cost = 150.0
            if self.gs.money >= cost:
                self.gs.money -= cost
                branch.hygiene = min(100, branch.hygiene + 20)
                self.gs.add_notification(f"Filiale gereinigt! +20 Hygiene (-150€)", "success")
            else:
                self.gs.add_notification("Zu wenig Geld zum Reinigen!", "danger")

    def _handle_staff_events(self, event):
        branch = self._get_selected_branch()
        if not branch:
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        # Hire buttons (rects stored during draw)
        for stype, hire_rect in getattr(self, '_hire_rects', {}).items():
            if hire_rect.collidepoint(event.pos):
                member = StaffMember(stype)
                cost = member.salary
                if self.gs.money >= cost:
                    self.gs.money -= cost
                    branch.hire_staff(stype)
                    self.gs.add_notification(f"{member.name} eingestellt!", "success")
                else:
                    self.gs.add_notification("Zu wenig Geld für Einstellung!", "danger")
                return
        # Fire buttons (rects stored during draw)
        for i, fire_rect in enumerate(getattr(self, '_fire_rects', [])):
            if fire_rect.collidepoint(event.pos):
                if i < len(branch.staff):
                    fired = branch.staff[i]
                    branch.fire_staff(i)
                    self.gs.add_notification(f"{fired.name} wurde entlassen.", "warn")
                return

    def _handle_info_events(self, event):
        if not self._get_selected_branch():
            return
        self._btn_toggle_open.handle_event(event)
        self._btn_clean.handle_event(event)

    def update(self, dt):
        self._anim += dt
        gs = self.gs

        # Build marketing buttons if needed
        branch = self._get_selected_branch()
        if branch and not self._mktg_buttons:
            mktg_items = {
                "flyer": ("🗞 Flyer", 200, C_ORANGE),
                "social_media": ("📱 Social Media", 500, C_BLUE),
                "influencer": ("⭐ Influencer", 2000, C_PURPLE),
                "stadion": ("🏟 Stadion-Werbung", 5000, C_TEAL),
                "tv": ("📺 TV-Werbung", 15000, C_RED),
            }
            for i, (key, (lbl, cost, col)) in enumerate(mktg_items.items()):
                def make_mktg_cb(k, b=branch):
                    def cb():
                        b.marketing[k] = not b.marketing[k]
                        state = "aktiviert" if b.marketing[k] else "deaktiviert"
                        self.gs.add_notification(f"Marketing '{k}' {state}!", "info")
                    return cb
                self._mktg_buttons[key] = Button(
                    (430, 140 + i * 55, 380, 44), f"{lbl} ({cost}€/Mo)", col, C_BG,
                    callback=make_mktg_cb(key)
                )

        # Update branch list
        items = []
        for b in gs.branches:
            rep_color = C_GREEN if b.reputation >= 70 else C_WARN if b.reputation >= 40 else C_RED
            items.append({
                "label": f"{'● ' if b.is_open else '○ '}{b.name}",
                "sub": f"{b.city} | Rep: {b.reputation:.0f} | {format_money(b.daily_revenue)}/Tag (Gewinn)",
                "color": rep_color if b.is_open else C_GRAY,
                "data": b
            })
        self.branch_list.set_items(items)

    def draw(self, surf):
        fonts = Fonts.get()
        gs = self.gs
        y0 = 85

        draw_text(surf, "🏪 Filialen-Management", fonts.lg, C_GOLD, 10, y0, "topleft")

        # Branch list
        self.branch_list.draw(surf)
        self.btn_new.draw(surf)
        self.btn_close_branch.enabled = self.selected_idx >= 0
        self.btn_close_branch.draw(surf)

        # New branch dialog
        if self._new_branch_state:
            self._draw_new_branch_dialog(surf)
            return

        # Dialog
        if self._dialog:
            self._dialog.draw(surf)
            return

        # Right panel - branch detail
        branch = self._get_selected_branch()
        if not branch:
            draw_text(surf, "← Wähle eine Filiale aus", fonts.md, C_GRAY,
                      700, 400, "center")
            return

        self.tab.draw(surf)

        if self.tab.active == 0:
            self._draw_info_tab(surf, branch)
        elif self.tab.active == 1:
            self._draw_recipe_tab(surf, branch)
        elif self.tab.active == 2:
            self._draw_staff_tab(surf, branch)
        elif self.tab.active == 3:
            self._draw_marketing_tab(surf, branch)
        elif self.tab.active == 4:
            self._draw_supply_tab(surf, branch)

    def _draw_new_branch_dialog(self, surf):
        ns = self._new_branch_state
        fonts = Fonts.get()
        overlay = pygame.Surface((SCREEN_W(), SCREEN_H()), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        bx, by = SCREEN_W() // 2 - 260, 160
        bw, bh = 520, 500
        draw_rect_rounded(surf, C_PANEL, (bx, by, bw, bh), 10, 2, C_GOLD)
        draw_text(surf, "Neue Filiale eröffnen", fonts.lg, C_GOLD, SCREEN_W() // 2, by + 30, "center")
        draw_text(surf, "ESC = Abbrechen", fonts.xs, C_GRAY, SCREEN_W() // 2, by + 55, "center")

        if ns["phase"] == "name":
            draw_text(surf, "1. Filialname:", fonts.md, C_TEXT, SCREEN_W() // 2, by + 90, "center")
            inp_rect = pygame.Rect(bx + 30, by + 120, bw - 60, 44)
            draw_rect_rounded(surf, C_BG2, inp_rect, 6, 1, C_GOLD)
            cursor = "|" if int(self._anim * 2) % 2 == 0 else ""
            draw_text(surf, ns["name"] + cursor, fonts.md, C_WHITE, inp_rect.x + 10, inp_rect.centery, "midleft")
            draw_text(surf, "ENTER zum Bestätigen", fonts.xs, C_GRAY, SCREEN_W() // 2, by + 185, "center")

        elif ns["phase"] == "city":
            draw_text(surf, f"Name: {ns['name']}", fonts.sm, C_GOLD, SCREEN_W() // 2, by + 90, "center")
            draw_text(surf, "2. Stadt:", fonts.md, C_TEXT, SCREEN_W() // 2, by + 120, "center")
            inp_rect = pygame.Rect(bx + 30, by + 150, bw - 60, 44)
            draw_rect_rounded(surf, C_BG2, inp_rect, 6, 1, C_GOLD)
            cursor = "|" if int(self._anim * 2) % 2 == 0 else ""
            draw_text(surf, ns["city"] + cursor, fonts.md, C_WHITE, inp_rect.x + 10, inp_rect.centery, "midleft")
            draw_text(surf, "ENTER zum Bestätigen", fonts.xs, C_GRAY, SCREEN_W() // 2, by + 215, "center")

        elif ns["phase"] == "country":
            draw_text(surf, f"Name: {ns['name']} | Stadt: {ns['city']}", fonts.sm, C_GOLD, SCREEN_W() // 2, by + 90, "center")
            draw_text(surf, "3. Land:", fonts.md, C_TEXT, SCREEN_W() // 2, by + 120, "center")
            inp_rect = pygame.Rect(bx + 30, by + 150, bw - 60, 44)
            draw_rect_rounded(surf, C_BG2, inp_rect, 6, 1, C_GOLD)
            cursor = "|" if int(self._anim * 2) % 2 == 0 else ""
            draw_text(surf, ns["country"] + cursor, fonts.md, C_WHITE, inp_rect.x + 10, inp_rect.centery, "midleft")
            draw_text(surf, "ENTER zum Bestätigen  (Standard: Deutschland)", fonts.xs, C_GRAY, SCREEN_W() // 2, by + 215, "center")

        elif ns["phase"] == "type":
            draw_text(surf, f"Name: {ns['name']} | {ns['city']}, {ns['country']}", fonts.sm, C_GOLD,
                      SCREEN_W() // 2, by + 90, "center")
            draw_text(surf, "4. Standorttyp wählen:", fonts.md, C_TEXT, SCREEN_W() // 2, by + 118, "center")
            for i, (lt, cfg) in enumerate(LOCATION_TYPES.items()):
                r = pygame.Rect(bx + 30, by + 150 + i * 62, bw - 60, 55)
                cost = cfg["rent"] * 3
                can_afford = self.gs.money >= cost
                col = C_GOLD if can_afford else C_RED
                bg = lerp_color(C_PANEL2, col, 0.1)
                draw_rect_rounded(surf, bg, r, 6, 1, col)
                labels = {
                    "kleinststadt": "🏘 Kleinstadt",
                    "grossstadt": "🏙 Großstadt",
                    "bahnhof": "🚂 Bahnhof",
                    "einkaufszentrum": "🛍 Einkaufszentrum",
                    "flughafen": "✈ Flughafen",
                }
                draw_text(surf, labels.get(lt, lt), fonts.sm, col, r.x + 12, r.centery - 8, "midleft")
                draw_text(surf, f"Miete: {cfg['rent']}€/Mo | Einrichtung: {cost:.0f}€ | Kunden: ~{cfg['foot_traffic']}/h",
                          fonts.xxs, C_TEXT2, r.x + 12, r.centery + 10, "midleft")
                if not can_afford:
                    draw_text(surf, "Nicht genug Geld!", fonts.xxs, C_RED, r.right - 12, r.centery, "midright")

    def _draw_info_tab(self, surf, branch: Branch):
        fonts = Fonts.get()
        rx, ry = 430, 125
        w = 830

        def row(label, val, vc=C_TEXT, y=None):
            nonlocal ry
            y = y or ry
            draw_text(surf, label, fonts.sm, C_TEXT2, rx, y, "topleft")
            draw_text(surf, val, fonts.sm, vc, rx + w - 10, y, "topright")
            ry += 28

        draw_text(surf, f"🏪 {branch.name}", fonts.lg, C_GOLD, rx, ry, "topleft"); ry += 38
        draw_text(surf, f"📍 {branch.city}, {branch.country} ({branch.location_type})",
                  fonts.sm, C_TEXT2, rx, ry, "topleft"); ry += 30

        row("Status:", "GEÖFFNET ✓" if branch.is_open else "GESCHLOSSEN ✗",
            C_GREEN if branch.is_open else C_RED)
        row("Öffnungszeit:", f"{branch.open_hour:02d}:00 – {branch.close_hour:02d}:00")
        row("Miete:", f"{branch.rent:.0f}€/Monat", C_RED2)
        row("Monatl. Kosten:", format_money(branch.monthly_fixed_costs()), C_RED2)
        row("Tagesgewinn:", format_money(branch.daily_revenue), money_color(branch.daily_revenue))
        row("Kunden gesamt:", f"{branch.total_customers:,}", C_BLUE2)
        eff = branch.staff_efficiency
        eff_col = C_GREEN if eff >= 1.0 else C_WARN if eff >= 0.6 else C_RED
        row("Personal-Effizienz:", f"{eff*100:.0f}%  {'✓ Gut' if eff>=1.0 else '⚠ Mehr Personal nötig!' if eff<0.6 else '~ OK'}", eff_col)
        row("Alter:", f"{branch.age_days} Tage")

        ry += 8
        draw_text(surf, "Hygiene:", fonts.sm, C_TEXT2, rx, ry, "topleft")
        hcolor = C_GREEN if branch.hygiene >= 70 else C_WARN if branch.hygiene >= 40 else C_RED
        draw_bar(surf, rx + 120, ry, 300, 22, branch.hygiene, 100, hcolor, label="")
        draw_text(surf, f"{branch.hygiene:.0f}%", fonts.sm, hcolor, rx + 430, ry + 11, "midleft")
        ry += 32

        draw_text(surf, "Reputation:", fonts.sm, C_TEXT2, rx, ry, "topleft")
        rcolor = C_GREEN if branch.reputation >= 70 else C_WARN if branch.reputation >= 40 else C_RED
        draw_bar(surf, rx + 120, ry, 300, 22, branch.reputation, 100, rcolor, label="")
        draw_text(surf, f"{branch.reputation:.0f}%", fonts.sm, rcolor, rx + 430, ry + 11, "midleft")
        ry += 36

        # Action buttons – update rect positions to match dynamic ry, then draw
        self._btn_toggle_open.rect = pygame.Rect(rx, ry, 200, 36)
        self._btn_toggle_open.label = "Filiale schließen" if branch.is_open else "Filiale öffnen"
        self._btn_toggle_open.color = C_RED if branch.is_open else C_GREEN
        self._btn_toggle_open.draw(surf)
        ry += 46

        self._btn_clean.rect = pygame.Rect(rx, ry, 200, 36)
        self._btn_clean.draw(surf)
        ry += 46

        # Sauce popularity
        ry += 10
        draw_text(surf, "🥫 Soßen-Beliebtheit:", fonts.sm, C_GOLD, rx, ry, "topleft"); ry += 28
        total_sauces = max(1, sum(branch.sauce_popularity.values()))
        for sk, sn in SAUCE_NAMES.items():
            cnt = branch.sauce_popularity.get(sk, 0)
            draw_text(surf, sn + ":", fonts.xs, C_TEXT2, rx, ry, "topleft")
            draw_bar(surf, rx + 130, ry, 250, 14, cnt, total_sauces, C_ORANGE, show_pct=False)
            draw_text(surf, str(cnt), fonts.xxs, C_TEXT, rx + 390, ry, "topleft")
            ry += 20

        # Active events
        if branch.active_events:
            ry += 10
            draw_text(surf, "⚡ Aktive Ereignisse:", fonts.sm, C_GOLD, rx, ry, "topleft"); ry += 28
            for ev in branch.active_events:
                tc = type_color(ev.get("type", "info"))
                draw_text(surf, f"• {ev['name']} (noch {ev.get('remaining', '?')} Tage)",
                          fonts.xs, tc, rx, ry, "topleft"); ry += 20

    def _draw_recipe_tab(self, surf, branch: Branch):
        fonts = Fonts.get()
        rx, ry = 430, 122

        # Recipe selector tabs
        for i, r in enumerate(branch.recipes):
            r_rect = pygame.Rect(rx + i * 90, ry, 85, 28)
            is_sel = i == (self._edit_recipe_idx % len(branch.recipes))
            draw_rect_rounded(surf, C_GOLD if is_sel else C_PANEL2, r_rect, 4, 1, C_BORDER)
            draw_text(surf, r.name[:10], fonts.xxs, C_BG if is_sel else C_TEXT, r_rect.centerx, r_rect.centery, "center")
        ry += 40

        recipe = branch.recipes[self._edit_recipe_idx % len(branch.recipes)]

        draw_text(surf, f"✏ Rezept bearbeiten: {recipe.name}", fonts.md, C_GOLD, rx, ry, "topleft"); ry += 35

        # Price
        draw_text(surf, "Preis:", fonts.sm, C_TEXT2, rx, ry, "topleft")
        draw_text(surf, f"{recipe.price:.2f}€", fonts.md, C_GOLD, rx + 120, ry, "topleft")
        self._btn_price_dn.rect.topleft = (rx + 270, ry)
        self._btn_price_up.rect.topleft = (rx + 310, ry)
        self._btn_price_dn.draw(surf)
        self._btn_price_up.draw(surf)
        cost = recipe.ingredient_cost()
        margin = recipe.price - cost
        mc = money_color(margin)
        draw_text(surf, f"Kosten: {cost:.2f}€ | Marge: {margin:.2f}€", fonts.xs, mc, rx + 360, ry + 6, "topleft")
        ry += 35

        # Fleisch menge
        draw_text(surf, "Fleischmenge:", fonts.sm, C_TEXT2, rx, ry, "topleft")
        draw_text(surf, f"x{recipe.fleisch_menge:.2f}", fonts.md, C_ORANGE, rx + 160, ry, "topleft")
        self._btn_fleisch_dn.rect.topleft = (rx + 270, ry)
        self._btn_fleisch_up.rect.topleft = (rx + 310, ry)
        self._btn_fleisch_dn.draw(surf)
        self._btn_fleisch_up.draw(surf)
        ry += 35

        # Fleisch type
        draw_text(surf, "Fleischtyp:", fonts.sm, C_TEXT2, rx, ry, "topleft"); ry += 28
        self._btn_fleisch_normal.rect.topleft = (rx, ry)
        self._btn_fleisch_premium.rect.topleft = (rx + 160, ry)
        self._btn_fleisch_normal.color = C_GOLD if recipe.fleisch == "fleisch_basis" else C_PANEL2
        self._btn_fleisch_premium.color = C_GOLD if recipe.fleisch == "fleisch_premium" else C_PANEL2
        self._btn_fleisch_normal.draw(surf)
        self._btn_fleisch_premium.draw(surf)
        ry += 40

        # Soßen
        draw_text(surf, "Soße:", fonts.sm, C_TEXT2, rx, ry, "topleft"); ry += 28
        for i, (sk, btn) in enumerate(self._sauce_btns.items()):
            btn.rect.topleft = (rx + (i % 3) * 120, ry + (i // 3) * 38)
            btn.color = C_ORANGE if recipe.sosse == sk else C_PANEL2
            btn.draw(surf)
        ry += (len(self._sauce_btns) // 3 + 1) * 38 + 5

        # Zutaten toggles
        draw_text(surf, "Zutaten:", fonts.sm, C_TEXT2, rx, ry, "topleft"); ry += 28
        ingr_map = {"salat": "Salat", "tomate": "Tomate", "zwiebel": "Zwiebel", "kraut": "Kraut", "gurke": "Gurke"}
        for i, (k, btn) in enumerate(self._ingr_btns.items()):
            btn.rect.topleft = (rx + i * 78, ry)
            active = getattr(recipe, k, False)
            btn.color = C_GREEN if active else C_PANEL2
            btn.draw(surf)
        ry += 40

        # Quality score
        q = recipe.quality_score()
        draw_text(surf, f"Qualität: {q:.1f}/10  |  Gewinn/Döner: {recipe.profit_margin():.2f}€",
                  fonts.sm, C_GOLD, rx, ry, "topleft")
        draw_bar(surf, rx + 280, ry, 200, 18, q, 10,
                 C_GREEN if q >= 7 else C_WARN if q >= 5 else C_RED, show_pct=False)
        ry += 35

        self._btn_add_recipe.rect.topleft = (rx, ry)
        self._btn_add_recipe.draw(surf)

    def _draw_staff_tab(self, surf, branch: Branch):
        fonts = Fonts.get()
        rx, ry = 430, 130

        draw_text(surf, "👥 Personalverwaltung", fonts.md, C_GOLD, rx, ry, "topleft"); ry += 35
        draw_text(surf, "Verfügbare Positionen (Klick = Einstellen):", fonts.sm, C_TEXT2, rx, ry, "topleft"); ry += 28

        type_info = {
            "doenemrister": ("Dönermeister", C_ORANGE, 1800),
            "kassengenie": ("Kassengenie", C_GREEN, 1600),
            "sauce_guru": ("Sauce-Guru", C_RED, 1700),
            "azubi": ("Azubi", C_BLUE, 600),
            "filialleiter": ("Filialleiter", C_GOLD, 2800),
            "reiniger": ("Reinigungskraft 🧹", C_TEAL, 700),
        }
        self._hire_rects = {}
        staff_descs = {
            "reiniger": "Hält Hygiene ≥ 80%",
        }
        for i, (stype, (lbl, col, sal)) in enumerate(type_info.items()):
            row_rect = pygame.Rect(rx, ry + i * 50, 570, 44)
            draw_rect_rounded(surf, C_PANEL2, row_rect, 6, 1, C_BORDER)
            draw_text(surf, lbl, fonts.sm, col, rx + 10, ry + i * 50 + 12, "topleft")
            sal_text = f"Gehalt: {sal}€/Mo"
            if stype in staff_descs:
                sal_text += f"  |  {staff_descs[stype]}"
            draw_text(surf, sal_text, fonts.xs, C_TEXT2, rx + 220, ry + i * 50 + 14, "topleft")
            # Hire button
            hire_rect = pygame.Rect(rx + 580, ry + i * 50 + 7, 80, 30)
            self._hire_rects[stype] = hire_rect
            pygame.draw.rect(surf, C_GREEN if self.gs.money >= sal else C_GRAY2, hire_rect, border_radius=5)
            draw_text(surf, "+ Hire", fonts.xs, C_BG, hire_rect.centerx, hire_rect.centery, "center")

        ry += len(type_info) * 50 + 15
        draw_text(surf, "Aktuelle Belegschaft:", fonts.sm, C_GOLD, rx, ry, "topleft"); ry += 28

        self._fire_rects = []
        if not branch.staff:
            draw_text(surf, "Keine Mitarbeiter!", fonts.sm, C_GRAY, rx + 100, ry, "topleft")
        else:
            for i, s in enumerate(branch.staff):
                row_y = ry + i * 38
                bg = C_PANEL if i % 2 == 0 else C_BG2
                pygame.draw.rect(surf, bg, (rx, row_y, 570, 34), border_radius=4)
                tc = C_TEXT
                draw_text(surf, s.name, fonts.xs, C_GOLD, rx + 8, row_y + 10, "topleft")
                draw_text(surf, s.type_label(), fonts.xxs, C_TEXT2, rx + 180, row_y + 10, "topleft")
                draw_text(surf, f"Eff:{s.efficiency:.1f}|Spd:{s.speed}|Frd:{s.friendliness}",
                          fonts.xxs, C_TEXT3, rx + 280, row_y + 10, "topleft")
                draw_bar(surf, rx + 440, row_y + 10, 80, 12, s.morale, 1.0,
                         C_GREEN if s.morale > 0.6 else C_WARN, show_pct=False)
                # Fire button
                fire_rect = pygame.Rect(rx + 580, row_y + 4, 70, 26)
                self._fire_rects.append(fire_rect)
                pygame.draw.rect(surf, C_DARK_RED, fire_rect, border_radius=4)
                draw_text(surf, "Entlassen", fonts.xxs, C_WHITE, fire_rect.centerx, fire_rect.centery, "center")

    def _draw_marketing_tab(self, surf, branch: Branch):
        fonts = Fonts.get()
        rx, ry = 430, 130

        draw_text(surf, "📢 Marketing-Management", fonts.md, C_GOLD, rx, ry, "topleft"); ry += 35
        draw_text(surf, "Aktive Kampagnen erhöhen Kundenzulauf und Umsatz:",
                  fonts.sm, C_TEXT2, rx, ry, "topleft"); ry += 30

        mktg_info = {
            "flyer": ("🗞 Flyer", 200, "+10% Kunden", C_ORANGE),
            "social_media": ("📱 Social Media", 500, "+20% Kunden", C_BLUE),
            "influencer": ("⭐ Influencer", 2000, "+35% Kunden", C_PURPLE),
            "stadion": ("🏟 Stadion-Werbung", 5000, "+50% Kunden", C_TEAL),
            "tv": ("📺 TV-Werbung", 15000, "+80% Kunden", C_RED),
        }

        for i, (key, (lbl, cost, effect, col)) in enumerate(mktg_info.items()):
            active = branch.marketing.get(key, False)
            row_rect = pygame.Rect(rx, ry + i * 55, 700, 48)
            bg = lerp_color(C_PANEL2, col, 0.15) if active else C_PANEL2
            draw_rect_rounded(surf, bg, row_rect, 6, 2, col if active else C_BORDER)
            draw_text(surf, lbl, fonts.sm, col, rx + 12, ry + i * 55 + 14, "topleft")
            draw_text(surf, f"{cost}€/Monat | {effect}", fonts.xs, C_TEXT2,
                      rx + 220, ry + i * 55 + 16, "topleft")
            status = "AKTIV ✓" if active else "INAKTIV"
            sc = C_GREEN if active else C_GRAY
            draw_text(surf, status, fonts.sm, sc, rx + 600, ry + i * 55 + 14, "topleft")
            if key in self._mktg_buttons:
                btn = self._mktg_buttons[key]
                btn.rect = pygame.Rect(rx + 500, ry + i * 55 + 8, 90, 32)
                btn.label = "Deaktivieren" if active else "Aktivieren"
                btn.color = C_RED if active else C_GREEN
                btn.draw(surf)

        ry += len(mktg_info) * 55 + 20
        total_mktg_cost = sum(
            {"flyer": 200, "social_media": 500, "influencer": 2000, "stadion": 5000, "tv": 15000}.get(k, 0)
            for k, v in branch.marketing.items() if v
        )
        draw_text(surf, f"Gesamt Marketing-Kosten: {total_mktg_cost}€/Monat",
                  fonts.sm, C_ORANGE, rx, ry, "topleft")
        draw_text(surf, f"Marketing-Multiplikator: x{branch.marketing_multiplier:.2f}",
                  fonts.sm, C_GOLD, rx, ry + 25, "topleft")

    def _draw_supply_tab(self, surf, branch: Branch):
        fonts = Fonts.get()
        rx, ry = 430, 130
        self._supply_rects = []

        draw_text(surf, "🚚 Lieferketten-Management", fonts.md, C_GOLD, rx, ry, "topleft"); ry += 35

        suppliers_available = [
            Supplier("fleisch", "Ahmet's Halal Fleisch", 7, 8, 1.0),
            Supplier("fleisch", "BioFleisch Premium GmbH", 9, 7, 1.5),
            Supplier("fleisch", "Billigfleisch Express", 3, 6, 0.6),
            Supplier("brot", "Bäckerei Müller", 8, 9, 1.0),
            Supplier("brot", "Industriebäckerei Schnell", 5, 7, 0.7),
            Supplier("gemuese", "Öztürk Gemüse", 8, 8, 1.0),
            Supplier("gemuese", "Bio-Garten Wagner", 9, 7, 1.4),
            Supplier("getraenke", "Cola & Co Vertrieb", 6, 9, 1.0),
        ]

        categories = {"fleisch": "🥩 Fleisch", "brot": "🍞 Brot",
                      "gemuese": "🥗 Gemüse", "getraenke": "🥤 Getränke"}

        for cat, cat_lbl in categories.items():
            draw_text(surf, cat_lbl, fonts.sm, C_GOLD, rx, ry, "topleft"); ry += 24
            cat_suppliers = [s for s in suppliers_available if s.stype == cat]
            for sup in cat_suppliers:
                active = branch.suppliers.get(cat) and branch.suppliers[cat].name == sup.name
                row_rect = pygame.Rect(rx, ry, 680, 36)
                bg = lerp_color(C_PANEL2, C_GREEN, 0.15) if active else C_PANEL2
                draw_rect_rounded(surf, bg, row_rect, 4, 1, C_GREEN if active else C_BORDER)

                qc = C_GREEN if sup.quality >= 7 else C_WARN if sup.quality >= 5 else C_RED
                rc = C_GREEN if sup.reliability >= 7 else C_WARN if sup.reliability >= 5 else C_RED
                pc = C_GREEN if sup.price_mod <= 1.0 else C_RED

                draw_text(surf, sup.name, fonts.xs, C_TEXT, rx + 8, ry + 10, "topleft")
                draw_text(surf, f"Qual:{sup.quality}", fonts.xxs, qc, rx + 240, ry + 10, "topleft")
                draw_text(surf, f"Zuv:{sup.reliability}", fonts.xxs, rc, rx + 300, ry + 10, "topleft")
                draw_text(surf, f"Preis: x{sup.price_mod:.1f}", fonts.xxs, pc, rx + 360, ry + 10, "topleft")

                sel_rect = pygame.Rect(rx + 590, ry + 5, 80, 26)
                col = C_RED if active else C_GREEN
                pygame.draw.rect(surf, col, sel_rect, border_radius=4)
                draw_text(surf, "Ausgewählt" if active else "Wählen",
                          fonts.xxs, C_BG, sel_rect.centerx, sel_rect.centery, "center")

                # Store rect+data for handle_event
                if not hasattr(self, '_supply_rects'):
                    self._supply_rects = []
                self._supply_rects.append((sel_rect, cat, sup, active))
                ry += 40
            ry += 8


# ─────────────────────────────────────────────
#  RESEARCH SCREEN
# ─────────────────────────────────────────────
class ResearchScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        self._anim = 0.0
        self._hovered_node = None

        # Node positions (manual layout)
        self._positions = {
            "schnittmaschine":   (150, 200),
            "premium_zutaten":   (150, 380),
            "ki_kasse":          (380, 200),
            "schnelle_lieferung":(380, 380),
            "eigene_logistik":   (610, 380),
            "franchise":         (610, 200),
            "brotfabrik":        (840, 380),
            "fleischproduktion": (840, 540),
            "solar_energie":     (150, 540),
            "loyalty_app":       (380, 540),
            "geheimrezept":      (610, 540),
            "mega_grill":        (840, 200),
        }
        self._node_size = 80

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for nid, (nx, ny) in self._positions.items():
                nr = pygame.Rect(nx - self._node_size // 2, ny - self._node_size // 2,
                                 self._node_size, self._node_size)
                if nr.collidepoint(mx, my):
                    self.gs.start_research(nid)
                    break
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self._hovered_node = None
            for nid, (nx, ny) in self._positions.items():
                nr = pygame.Rect(nx - self._node_size // 2, ny - self._node_size // 2,
                                 self._node_size, self._node_size)
                if nr.collidepoint(mx, my):
                    self._hovered_node = nid

    def update(self, dt):
        self._anim += dt

    def draw(self, surf):
        fonts = Fonts.get()
        gs = self.gs
        y0 = 85

        draw_text(surf, "🔬 Forschung & Entwicklung", fonts.lg, C_GOLD, 20, y0, "topleft")

        if gs.active_research:
            node = gs.research_tree[gs.active_research]
            prog = node.progress
            draw_text(surf, f"Aktive Forschung: {node.name}  [{int(prog*100)}%]",
                      fonts.sm, C_TEAL, SCREEN_W() - 20, y0 + 5, "topright")
            draw_bar(surf, SCREEN_W() - 400, y0 + 25, 380, 12, prog, 1.0, C_TEAL, show_pct=False)

        # Draw connections
        for nid, node in gs.research_tree.items():
            if nid not in self._positions:
                continue
            nx, ny = self._positions[nid]
            for req in node.requires:
                if req in self._positions:
                    rx, ry = self._positions[req]
                    req_node = gs.research_tree[req]
                    col = C_GREEN if req_node.unlocked else C_GRAY2
                    pygame.draw.line(surf, col, (rx + 30, ry), (nx - 30, ny), 2)

        # Draw nodes
        for nid, node in gs.research_tree.items():
            if nid not in self._positions:
                continue
            nx, ny = self._positions[nid]
            ns = self._node_size

            # Colors
            if node.unlocked:
                bg = lerp_color(C_GREEN, C_BG, 0.5)
                border = C_GREEN
            elif node.researching:
                t = abs(math.sin(self._anim * 2))
                bg = lerp_color(C_TEAL, C_BG, 0.4 + t * 0.2)
                border = C_TEAL
            elif any(not gs.research_tree[r].unlocked for r in node.requires):
                bg = C_BG2
                border = C_GRAY2
            else:
                bg = C_PANEL
                border = C_GOLD if nid == self._hovered_node else C_BORDER

            rect = pygame.Rect(nx - ns // 2, ny - ns // 2, ns, ns)
            draw_rect_rounded(surf, bg, rect, 8, 2, border)

            # Icon / status
            if node.unlocked:
                icon = "✓"
                ic = C_GREEN
            elif node.researching:
                icon = f"{int(node.progress*100)}%"
                ic = C_TEAL
            else:
                icon = "🔬"
                ic = C_GRAY

            draw_text(surf, icon, fonts.sm, ic, nx, ny - 16, "center")
            # Truncate name
            name_short = node.name if len(node.name) <= 14 else node.name[:12] + ".."
            lines = name_short.split(" ")
            for li, line in enumerate(lines[:2]):
                draw_text(surf, line, fonts.xxs, C_TEXT, nx, ny + 4 + li * 14, "center")

            if nid == self._hovered_node:
                draw_text(surf, f"{format_money(node.cost)} | {node.duration_days}T",
                          fonts.xxs, C_GOLD, nx, ny + 46, "center")

        # Tooltip for hovered
        if self._hovered_node:
            node = gs.research_tree[self._hovered_node]
            mx, my = pygame.mouse.get_pos()
            tw = 320
            th = 100
            tx = min(mx + 15, SCREEN_W() - tw - 5)
            ty = min(my + 15, SCREEN_H() - th - 5)
            draw_rect_rounded(surf, C_PANEL, (tx, ty, tw, th), 8, 1, C_GOLD)
            draw_text(surf, node.name, fonts.sm, C_GOLD, tx + 10, ty + 10, "topleft")
            draw_text(surf, node.desc, fonts.xs, C_TEXT, tx + 10, ty + 35,
                      "topleft", max_width=300)
            status = "✓ Abgeschlossen" if node.unlocked else \
                     f"In Bearbeitung {int(node.progress*100)}%" if node.researching else \
                     f"Kosten: {format_money(node.cost)} | {node.duration_days} Tage"
            draw_text(surf, status, fonts.xs, C_TEAL if node.unlocked else C_GOLD,
                      tx + 10, ty + 75, "topleft")

        # Legend
        ly = SCREEN_H() - 60
        for col, lbl in [(C_GREEN, "Abgeschlossen"), (C_TEAL, "In Bearbeitung"),
                         (C_GOLD, "Verfügbar"), (C_GRAY2, "Gesperrt")]:
            pygame.draw.circle(surf, col, (20, ly + 10), 6)
            draw_text(surf, lbl, fonts.xxs, C_TEXT2, 32, ly + 5, "topleft")
            ly += 18


# ─────────────────────────────────────────────
#  STATISTICS SCREEN
# ─────────────────────────────────────────────
class StatisticsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)

    def draw(self, surf):
        fonts = Fonts.get()
        gs = self.gs
        y0 = 85

        draw_text(surf, "📊 Statistiken & Analysen", fonts.lg, C_GOLD, 20, y0, "topleft")

        # Top row charts
        chart_w = 390
        chart_h = 140
        charts = [
            (gs.revenue_history, "Tagesgewinn", C_GREEN, 20, y0 + 45),
            ([float(v) for v in gs.customer_history], "Kunden/Tag", C_BLUE, 430, y0 + 45),
            (gs.expense_history, "Tagesausgaben", C_RED, 840, y0 + 45),
        ]
        for data, lbl, col, cx, cy in charts:
            draw_rect_rounded(surf, C_PANEL, (cx, cy, chart_w, chart_h + 30), 8, 1, C_BORDER)
            draw_text(surf, lbl, fonts.sm, col, cx + 10, cy + 10, "topleft")
            draw_mini_chart(surf, data, (cx + 8, cy + 35, chart_w - 16, chart_h - 10), col, label="")

        # Branch performance table
        ty = y0 + 230
        draw_rect_rounded(surf, C_PANEL, (20, ty, 1240, 260), 8, 1, C_BORDER)
        draw_text(surf, "🏪 Filial-Performance", fonts.md, C_GOLD, 30, ty + 12, "topleft")

        headers = ["Filiale", "Stadt", "Kunden", "Umsatz", "Hygiene", "Reputation", "Status"]
        col_x = [30, 200, 360, 470, 600, 720, 860]
        for i, (h, x) in enumerate(zip(headers, col_x)):
            draw_text(surf, h, fonts.sm, C_GOLD, x, ty + 38, "topleft")
        pygame.draw.line(surf, C_BORDER, (25, ty + 56), (1255, ty + 56))

        for i, b in enumerate(sorted(gs.branches, key=lambda b: b.total_revenue, reverse=True)[:6]):
            row_y = ty + 62 + i * 32
            bg = C_PANEL if i % 2 == 0 else C_BG2
            pygame.draw.rect(surf, bg, (25, row_y - 2, 1230, 30), border_radius=3)
            vals = [
                (b.name[:16], C_TEXT),
                (b.city[:14], C_TEXT2),
                (f"{b.total_customers:,}", C_BLUE2),
                (format_money(b.total_revenue), C_GREEN),
                (f"{b.hygiene:.0f}%", C_GREEN if b.hygiene >= 70 else C_WARN if b.hygiene >= 40 else C_RED),
                (f"{b.reputation:.0f}%", C_GREEN if b.reputation >= 70 else C_WARN if b.reputation >= 40 else C_RED),
                ("OFFEN" if b.is_open else "ZU", C_GREEN if b.is_open else C_RED),
            ]
            for (v, vc), x in zip(vals, col_x):
                draw_text(surf, v, fonts.xs, vc, x, row_y + 6, "topleft")

        # Sauce popularity global
        sy = y0 + 510
        draw_rect_rounded(surf, C_PANEL, (20, sy, 400, 170), 8, 1, C_BORDER)
        draw_text(surf, "🥫 Beliebteste Soßen (gesamt)", fonts.sm, C_GOLD, 30, sy + 12, "topleft")

        # Aggregate sauce data
        total_sauces: dict = {}
        for b in gs.branches:
            for sk, cnt in b.sauce_popularity.items():
                total_sauces[sk] = total_sauces.get(sk, 0) + cnt

        max_cnt = max(total_sauces.values()) if total_sauces else 1
        for i, (sk, sn) in enumerate(SAUCE_NAMES.items()):
            cnt = total_sauces.get(sk, 0)
            row_y = sy + 38 + i * 24
            draw_text(surf, sn + ":", fonts.xs, C_TEXT2, 30, row_y, "topleft")
            draw_bar(surf, 140, row_y, 200, 16, cnt, max_cnt, C_ORANGE, show_pct=False)
            draw_text(surf, str(cnt), fonts.xxs, C_TEXT, 350, row_y + 1, "topleft")

        # Company summary
        cx2, cy2 = 440, sy
        draw_rect_rounded(surf, C_PANEL, (cx2, cy2, 400, 170), 8, 1, C_BORDER)
        draw_text(surf, "🏢 Unternehmenskennzahlen", fonts.sm, C_GOLD, cx2 + 10, cy2 + 12, "topleft")
        kpis = [
            ("Filialen:", str(len(gs.branches))),
            ("Gesamtkunden:", f"{gs.total_customers_served:,}"),
            ("Gesamtumsatz:", format_money(gs.total_revenue)),
            ("Länder:", str(len(gs.countries_present))),
            ("Spieltage:", str(gs.day)),
        ]
        for i, (k, v) in enumerate(kpis):
            draw_text(surf, k, fonts.xs, C_TEXT2, cx2 + 10, cy2 + 40 + i * 24, "topleft")
            draw_text(surf, v, fonts.sm, C_GOLD, cx2 + 390, cy2 + 38 + i * 24, "topright")

        # Competitor overview
        comp_x, comp_y = 860, sy
        draw_rect_rounded(surf, C_PANEL, (comp_x, comp_y, 380, 170), 8, 1, C_BORDER)
        draw_text(surf, "⚔ Konkurrenz", fonts.sm, C_GOLD, comp_x + 10, comp_y + 12, "topleft")
        if gs.competitors:
            for i, comp in enumerate(gs.competitors[:5]):
                row_y = comp_y + 38 + i * 24
                draw_text(surf, comp.name[:20], fonts.xxs, comp.color, comp_x + 10, row_y, "topleft")
                draw_text(surf, f"Marktanteil: {comp.market_share*100:.1f}%",
                          fonts.xxs, C_TEXT2, comp_x + 230, row_y, "topleft")
        else:
            draw_text(surf, "Noch keine Konkurrenz!", fonts.sm, C_GRAY, comp_x + 190, comp_y + 90, "center")


# ─────────────────────────────────────────────
#  FINANCE SCREEN
# ─────────────────────────────────────────────
class FinanceScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        loan_x, loan_y = 860, 85 + 150   # matches draw layout
        self._btn_loan10 = Button(
            (loan_x + 10, loan_y + 100, 160, 36), "10K\u20ac Kredit nehmen",
            C_TEAL, C_BG,
            callback=self._take_loan_10k
        )
        self._btn_loan50 = Button(
            (loan_x + 10, loan_y + 145, 160, 36), "50K\u20ac Kredit nehmen",
            C_BLUE, C_BG,
            callback=self._take_loan_50k
        )

    def _take_loan_10k(self):
        self.gs.money += 10000
        self.gs.loan_debt += 10000
        self.gs.loan_monthly_payment += 500
        self.gs.add_notification("10.000\u20ac Kredit aufgenommen! +500\u20ac Zinsen/Monat", "warn")

    def _take_loan_50k(self):
        self.gs.money += 50000
        self.gs.loan_debt += 50000
        self.gs.loan_monthly_payment += 2500
        self.gs.add_notification("50.000\u20ac Kredit aufgenommen! +2500\u20ac Zinsen/Monat", "warn")

    def handle_event(self, event):
        self._btn_loan10.handle_event(event)
        self._btn_loan50.handle_event(event)

    def draw(self, surf):
        fonts = Fonts.get()
        gs = self.gs
        y0 = 85

        draw_text(surf, "💰 Finanzübersicht", fonts.lg, C_GOLD, 20, y0, "topleft")

        # Summary boxes
        boxes = [
            ("Kapital", format_money(gs.money), money_color(gs.money)),
            ("Gesamtumsatz", format_money(gs.total_revenue), C_GREEN),
            ("Gesamtausgaben", format_money(gs.total_expenses), C_RED2),
            ("Nettogewinn", format_money(gs.total_revenue - gs.total_expenses),
             money_color(gs.total_revenue - gs.total_expenses)),
        ]
        for i, (lbl, val, vc) in enumerate(boxes):
            bx = 20 + i * 310
            draw_rect_rounded(surf, C_PANEL, (bx, y0 + 45, 295, 80), 8, 1, C_BORDER)
            draw_text(surf, lbl, fonts.sm, C_TEXT2, bx + 12, y0 + 55, "topleft")
            draw_text(surf, val, fonts.lg, vc, bx + 148, y0 + 75, "center")

        # Revenue/Expense chart combined
        cy = y0 + 150
        draw_rect_rounded(surf, C_PANEL, (20, cy, 820, 180), 8, 1, C_BORDER)
        draw_text(surf, "📈 Gewinn vs Ausgaben (30 Tage)", fonts.sm, C_GOLD, 30, cy + 12, "topleft")
        # Draw dual charts
        rev_max = max(max(gs.revenue_history), 1)
        exp_max = max(max(gs.expense_history), 1)
        overall_max = max(rev_max, exp_max)
        chart_rect = (30, cy + 38, 800, 130)
        pygame.draw.rect(surf, C_BG2, chart_rect, border_radius=4)

        def draw_line(data, color, max_v):
            pts = []
            for i, v in enumerate(data):
                if v <= 0:
                    continue
                px = chart_rect[0] + int(i / 29 * (chart_rect[2] - 8)) + 4
                py = chart_rect[1] + chart_rect[3] - 4 - int(v / max_v * (chart_rect[3] - 12))
                pts.append((px, py))
            if len(pts) >= 2:
                pygame.draw.lines(surf, color, False, pts, 2)

        draw_line(gs.revenue_history, C_GREEN, overall_max)
        draw_line(gs.expense_history, C_RED, overall_max)

        draw_text(surf, "— Gewinn", fonts.xxs, C_GREEN, chart_rect[0] + chart_rect[2] - 10, cy + 40, "topright")
        draw_text(surf, "— Ausgaben", fonts.xxs, C_RED, chart_rect[0] + chart_rect[2] - 10, cy + 55, "topright")

        # Per-branch cost breakdown
        ty = y0 + 350
        draw_rect_rounded(surf, C_PANEL, (20, ty, 820, 290), 8, 1, C_BORDER)
        draw_text(surf, "🏪 Filialkosten", fonts.md, C_GOLD, 30, ty + 12, "topleft")
        headers = ["Filiale", "Miete", "Personal", "Marketing", "Fixkosten", "Tagesgewinn", "Monatsgewinn"]
        hx = [30, 180, 310, 440, 560, 660, 780]
        for h, x in zip(headers, hx):
            draw_text(surf, h, fonts.xs, C_GOLD, x, ty + 36, "topleft")
        pygame.draw.line(surf, C_BORDER, (25, ty + 52), (835, ty + 52))

        total_rent = total_staff = total_mktg = 0.0
        for i, b in enumerate(sorted(gs.branches, key=lambda b: b.monthly_fixed_costs(), reverse=True)[:7]):
            row_y = ty + 58 + i * 32
            bg = C_PANEL if i % 2 == 0 else C_BG2
            pygame.draw.rect(surf, bg, (25, row_y - 2, 810, 28), border_radius=3)
            rent = b.rent
            staff_cost = sum(s.monthly_cost() for s in b.staff)
            mktg_cost = sum(
                {"flyer": 200, "social_media": 500, "influencer": 2000, "stadion": 5000, "tv": 15000}.get(k, 0)
                for k, v in b.marketing.items() if v
            )
            total = rent + staff_cost + mktg_cost
            daily_rev = b.daily_revenue
            daily_profit = daily_rev - total / 30
            total_rent += rent; total_staff += staff_cost; total_mktg += mktg_cost
            vals = [
                (b.name[:14], C_TEXT),
                (f"{rent:.0f}€", C_RED2),
                (f"{staff_cost:.0f}€", C_RED2),
                (f"{mktg_cost:.0f}€", C_ORANGE),
                (f"{total:.0f}€", C_RED),
                (format_money(daily_rev * 30), C_GREEN),
                (format_money(daily_rev * 30 - total), money_color(daily_rev * 30 - total)),
            ]
            for (v, vc), x in zip(vals, hx):
                draw_text(surf, v, fonts.xxs, vc, x, row_y + 6, "topleft")

        # Totals row
        total_y = ty + 58 + min(len(gs.branches), 7) * 32 + 5
        if len(gs.branches) > 0:
            pygame.draw.line(surf, C_BORDER, (25, total_y), (835, total_y))
            total_y += 4
            draw_text(surf, "GESAMT", fonts.xs, C_GOLD, 30, total_y, "topleft")
            draw_text(surf, f"{total_rent:.0f}€", fonts.xs, C_RED2, 180, total_y, "topleft")
            draw_text(surf, f"{total_staff:.0f}€", fonts.xs, C_RED2, 310, total_y, "topleft")
            draw_text(surf, f"{total_mktg:.0f}€", fonts.xs, C_ORANGE, 440, total_y, "topleft")
            grand_total = total_rent + total_staff + total_mktg
            draw_text(surf, f"{grand_total:.0f}€/Mo", fonts.xs, C_RED, 560, total_y, "topleft")

        # Loan system
        loan_x, loan_y = 860, y0 + 150
        draw_rect_rounded(surf, C_PANEL, (loan_x, loan_y, 380, 200), 8, 1, C_BORDER)
        draw_text(surf, "🏦 Kreditoption", fonts.sm, C_GOLD, loan_x + 10, loan_y + 12, "topleft")
        draw_text(surf, "Sofortkredit: 10.000€", fonts.sm, C_TEXT, loan_x + 10, loan_y + 45, "topleft")
        draw_text(surf, "Zinsen: 5% / Monat", fonts.xs, C_TEXT2, loan_x + 10, loan_y + 70, "topleft")
        debt_col = C_RED if self.gs.loan_debt > 0 else C_TEXT2
        draw_text(surf, f"Schulden: {self.gs.loan_debt:.0f}€  |  Rate: {self.gs.loan_monthly_payment:.0f}€/Mo", fonts.xs, debt_col, loan_x + 10, loan_y + 90, "topleft")


        self._btn_loan10.draw(surf)
        self._btn_loan50.draw(surf)


# ─────────────────────────────────────────────
#  OPTIONS SCREEN
# ─────────────────────────────────────────────
class OptionsScreen(Screen):
    def __init__(self, game):
        super().__init__(game)
        cx = SCREEN_W() // 2
        self.btn_save0 = Button((cx - 160, 200, 300, 50), "Spiel speichern (Slot 1)", C_GOLD, C_BG,
                                 callback=lambda: self.game.gs.save(0))
        self.btn_save1 = Button((cx - 160, 265, 300, 50), "Spiel speichern (Slot 2)", C_ORANGE, C_BG,
                                 callback=lambda: self.game.gs.save(1))
        self.btn_save2 = Button((cx - 160, 330, 300, 50), "Spiel speichern (Slot 3)", C_TEAL, C_BG,
                                 callback=lambda: self.game.gs.save(2))
        self.btn_menu = Button((cx - 160, 420, 300, 50), "Zurück zum Hauptmenü", C_RED, C_WHITE,
                                callback=lambda: self.game.set_screen("main_menu"))
        self.btn_quit = Button((cx - 160, 490, 300, 50), "Spiel beenden", C_DARK_RED, C_WHITE,
                                callback=lambda: setattr(self.game, "running", False))

    def handle_event(self, event):
        for btn in [self.btn_save0, self.btn_save1, self.btn_save2, self.btn_menu, self.btn_quit]:
            btn.handle_event(event)
        # Speed buttons
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            cx = SCREEN_W() // 2
            for i, (lbl, spd) in enumerate([("1x", 1.0), ("2x", 3.0), ("4x", 8.0), ("8x", 16.0)]):
                r = pygame.Rect(cx - 160 + i * 80, 175, 74, 30)
                if r.collidepoint(event.pos):
                    self.gs.game_speed = spd

    def draw(self, surf):
        fonts = Fonts.get()
        y0 = 85
        draw_text(surf, "⚙ Optionen", fonts.lg, C_GOLD, SCREEN_W() // 2, y0 + 20, "center")

        # Speed setting
        cx = SCREEN_W() // 2
        draw_text(surf, "Spielgeschwindigkeit:", fonts.sm, C_TEXT2, cx - 160, 155, "topleft")
        for i, (lbl, spd) in enumerate([("1x", 1.0), ("2x", 3.0), ("4x", 8.0), ("8x", 16.0)]):
            r = pygame.Rect(cx - 160 + i * 80, 175, 74, 30)
            col = C_GOLD if self.gs.game_speed == spd else C_PANEL2
            pygame.draw.rect(surf, col, r, border_radius=5)
            draw_text(surf, lbl, fonts.sm, C_BG if col == C_GOLD else C_TEXT,
                      r.centerx, r.centery, "center")


        for btn in [self.btn_save0, self.btn_save1, self.btn_save2, self.btn_menu, self.btn_quit]:
            btn.draw(surf)

        # Tips
        draw_rect_rounded(surf, C_PANEL, (SCREEN_W() - 450, 200, 420, 360), 8, 1, C_BORDER)
        draw_text(surf, "💡 Spieltipps", fonts.md, C_GOLD, SCREEN_W() - 230, 218, "center")
        tips = [
            "Eröffne zuerst in Kleinstädten,",
            "bevor du in Großstädte gehst.",
            "",
            "Stelle mindestens einen Dönermeister",
            "und einen Azubi ein.",
            "",
            "Forsche früh in Schnittmaschine",
            "für schnellere Produktion.",
            "",
            "Achte auf Hygiene! Ein schmutziger",
            "Laden verliert Kunden schnell.",
            "",
            "Social Media lohnt sich ab Tag 1!",
        ]
        for i, tip in enumerate(tips):
            draw_text(surf, tip, fonts.xs, C_TEXT2, SCREEN_W() - 440, 248 + i * 20, "topleft")