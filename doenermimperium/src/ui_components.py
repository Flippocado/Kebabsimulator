# DÖNERIMPERIUM™ - UI Components
# =================================
from __future__ import annotations
import pygame
import math
import time
from typing import Optional, Callable
from constants import *


# ─────────────────────────────────────────────
#  FONT MANAGER
# ─────────────────────────────────────────────
class Fonts:
    _instance = None

    def __init__(self):
        pygame.font.init()
        # Use system fonts with fallbacks
        def try_font(names: list, size: int, bold: bool = False) -> pygame.font.Font:
            for name in names:
                try:
                    return pygame.font.SysFont(name, size, bold=bold)
                except:
                    pass
            return pygame.font.Font(None, size)

        self.xl    = try_font(["Palatino", "Georgia", "Garamond", "freesans"], 52, True)
        self.lg    = try_font(["Palatino", "Georgia", "Garamond", "freesans"], 36, True)
        self.md    = try_font(["Palatino", "Georgia", "Garamond", "freesans"], 26)
        self.sm    = try_font(["Palatino", "Georgia", "freesans", "dejavu sans"], 20)
        self.xs    = try_font(["Palatino", "Georgia", "freesans", "dejavu sans"], 16)
        self.xxs   = try_font(["Palatino", "Georgia", "freesans", "dejavu sans"], 13)
        self.title = try_font(["Palatino", "Garamond", "Georgia", "freesans"], 64, True)
        self.mono  = try_font(["Courier New", "DejaVu Sans Mono", "Courier", "monospace"], 16)

    @classmethod
    def get(cls) -> "Fonts":
        if cls._instance is None:
            cls._instance = Fonts()
        return cls._instance


# ─────────────────────────────────────────────
#  DRAWING HELPERS
# ─────────────────────────────────────────────
def draw_rect_rounded(surf: pygame.Surface, color, rect, radius: int = 8, border: int = 0, border_color=None):
    pygame.draw.rect(surf, color, rect, border_radius=radius)
    if border > 0 and border_color:
        pygame.draw.rect(surf, border_color, rect, border, border_radius=radius)


def draw_text(surf: pygame.Surface, text: str, font: pygame.font.Font,
              color, x: int, y: int, anchor: str = "topleft", max_width: int = 0) -> pygame.Rect:
    if not text:
        return pygame.Rect(x, y, 0, 0)
    if max_width > 0:
        words = text.split()
        lines = []
        cur = ""
        for w in words:
            test = cur + (" " if cur else "") + w
            if font.size(test)[0] > max_width and cur:
                lines.append(cur)
                cur = w
            else:
                cur = test
        if cur:
            lines.append(cur)
        rects = []
        ly = y
        for line in lines:
            r = draw_text(surf, line, font, color, x, ly, anchor)
            ly += r.height + 2
            rects.append(r)
        return rects[0] if rects else pygame.Rect(x, y, 0, 0)

    surf2 = font.render(text, True, color)
    r = surf2.get_rect()
    setattr(r, anchor, (x, y))
    surf.blit(surf2, r)
    return r


def draw_bar(surf: pygame.Surface, x: int, y: int, w: int, h: int,
             value: float, max_val: float, fg_color, bg_color=C_PANEL2,
             border_color=C_BORDER, label: str = "", show_pct: bool = True):
    pct = max(0.0, min(1.0, value / max_val)) if max_val > 0 else 0.0
    bg_rect = pygame.Rect(x, y, w, h)
    fg_rect = pygame.Rect(x, y, int(w * pct), h)
    pygame.draw.rect(surf, bg_color, bg_rect, border_radius=4)
    if fg_rect.width > 0:
        pygame.draw.rect(surf, fg_color, fg_rect, border_radius=4)
    pygame.draw.rect(surf, border_color, bg_rect, 1, border_radius=4)
    if label or show_pct:
        fonts = Fonts.get()
        txt = f"{label} {int(pct*100)}%" if label else f"{int(pct*100)}%"
        draw_text(surf, txt, fonts.xxs, C_WHITE, x + w // 2, y + h // 2, "center")


def draw_gradient_rect(surf: pygame.Surface, rect, color1, color2, vertical: bool = True):
    """Draw a vertical or horizontal gradient."""
    x, y, w, h = rect
    if vertical:
        for i in range(h):
            t = i / max(1, h - 1)
            c = tuple(int(color1[j] + (color2[j] - color1[j]) * t) for j in range(3))
            pygame.draw.line(surf, c, (x, y + i), (x + w - 1, y + i))
    else:
        for i in range(w):
            t = i / max(1, w - 1)
            c = tuple(int(color1[j] + (color2[j] - color1[j]) * t) for j in range(3))
            pygame.draw.line(surf, c, (x + i, y), (x + i, y + h - 1))


def lerp_color(a, b, t: float):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def money_color(amount: float) -> tuple:
    if amount >= 0:
        return C_GREEN2
    return C_RED2


def format_money(amount: float) -> str:
    if abs(amount) >= 1_000_000_000:
        return f"{amount/1_000_000_000:.2f}Mrd€"
    if abs(amount) >= 1_000_000:
        return f"{amount/1_000_000:.2f}Mio€"
    if abs(amount) >= 1_000:
        return f"{amount/1_000:.1f}K€"
    return f"{amount:.2f}€"


def type_color(ntype: str) -> tuple:
    return {
        "success": C_GREEN, "warn": C_WARN, "danger": C_DANGER,
        "info": C_INFO, "positive": C_GREEN, "negative": C_RED
    }.get(ntype, C_INFO)


# ─────────────────────────────────────────────
#  BUTTON
# ─────────────────────────────────────────────
class Button:
    def __init__(self, rect, label: str, color=C_GOLD, text_color=C_BG,
                 font=None, radius: int = 6, callback: Callable = None,
                 icon: str = ""):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.color = color
        self.hover_color = lerp_color(color, C_WHITE, 0.2)
        self.text_color = text_color
        self.font = font
        self.radius = radius
        self.callback = callback
        self.icon = icon
        self.hovered = False
        self.pressed = False
        self.enabled = True
        self._press_time = 0.0
        self.tooltip = ""

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                self._press_time = time.time()
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.pressed and self.rect.collidepoint(event.pos):
                self.pressed = False
                if self.callback:
                    self.callback()
                return True
            self.pressed = False
        return False

    def draw(self, surf: pygame.Surface):
        fonts = Fonts.get()
        font = self.font or fonts.sm

        if not self.enabled:
            color = C_GRAY2
            tc = C_GRAY
        elif self.pressed:
            color = lerp_color(self.color, C_BG, 0.3)
            tc = self.text_color
        elif self.hovered:
            color = self.hover_color
            tc = self.text_color
        else:
            color = self.color
            tc = self.text_color

        draw_rect_rounded(surf, color, self.rect, self.radius)
        # Subtle highlight on top
        highlight = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.w - 4, self.rect.h // 2 - 2)
        highlight_surf = pygame.Surface((highlight.w, highlight.h), pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 20))
        surf.blit(highlight_surf, highlight)

        txt = (self.icon + " " if self.icon else "") + self.label
        draw_text(surf, txt, font, tc, self.rect.centerx, self.rect.centery, "center")


# ─────────────────────────────────────────────
#  PANEL / CARD
# ─────────────────────────────────────────────
class Panel:
    def __init__(self, rect, title: str = "", color=C_PANEL, border=C_BORDER,
                 title_color=C_GOLD, radius: int = 8):
        self.rect = pygame.Rect(rect)
        self.title = title
        self.color = color
        self.border = border
        self.title_color = title_color
        self.radius = radius

    def draw(self, surf: pygame.Surface):
        fonts = Fonts.get()
        draw_rect_rounded(surf, self.color, self.rect, self.radius, 1, self.border)
        if self.title:
            # Title bar
            title_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.w, 32)
            draw_rect_rounded(surf, lerp_color(self.color, C_GOLD, 0.15), title_rect, self.radius)
            pygame.draw.line(surf, self.border,
                (self.rect.x, self.rect.y + 32), (self.rect.right, self.rect.y + 32))
            draw_text(surf, self.title, fonts.sm, self.title_color,
                      self.rect.x + 10, self.rect.y + 16, "midleft")


# ─────────────────────────────────────────────
#  SCROLLABLE LIST
# ─────────────────────────────────────────────
class ScrollList:
    def __init__(self, rect, item_height: int = 36):
        self.rect = pygame.Rect(rect)
        self.item_height = item_height
        self.scroll = 0
        self.items = []  # list of dicts: {label, sub, color, data, selected}
        self.selected_idx = -1
        self.on_select: Optional[Callable] = None

    def set_items(self, items: list):
        self.items = items
        self.scroll = max(0, min(self.scroll, max(0, len(items) * self.item_height - self.rect.h)))

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.rect.collidepoint(pygame.mouse.get_pos()):
            return False
        if event.type == pygame.MOUSEWHEEL:
            self.scroll = max(0, min(
                self.scroll - event.y * self.item_height,
                max(0, len(self.items) * self.item_height - self.rect.h)
            ))
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.rect.collidepoint(mx, my):
                rel_y = my - self.rect.y + self.scroll
                idx = int(rel_y // self.item_height)
                if 0 <= idx < len(self.items):
                    self.selected_idx = idx
                    if self.on_select:
                        self.on_select(idx, self.items[idx])
                    return True
        return False

    def draw(self, surf: pygame.Surface):
        fonts = Fonts.get()
        # Clip
        clip = surf.get_clip()
        surf.set_clip(self.rect)

        # Background
        pygame.draw.rect(surf, C_BG2, self.rect)

        visible_start = self.scroll // self.item_height
        visible_end = min(len(self.items), visible_start + self.rect.h // self.item_height + 2)

        for i in range(visible_start, visible_end):
            item = self.items[i]
            iy = self.rect.y + i * self.item_height - self.scroll
            item_rect = pygame.Rect(self.rect.x, iy, self.rect.w, self.item_height)

            bg = C_PANEL if i % 2 == 0 else C_BG2
            if i == self.selected_idx:
                bg = lerp_color(C_GOLD, C_BG, 0.7)
            pygame.draw.rect(surf, bg, item_rect)
            pygame.draw.line(surf, C_BORDER, (item_rect.x, item_rect.bottom - 1), (item_rect.right, item_rect.bottom - 1))

            color = item.get("color", C_WHITE)
            label = item.get("label", "")
            sub = item.get("sub", "")
            draw_text(surf, label, fonts.sm, color, self.rect.x + 10, iy + (8 if sub else 10), "topleft")
            if sub:
                draw_text(surf, sub, fonts.xxs, C_TEXT3, self.rect.x + 10, iy + 24, "topleft")

        # Scrollbar
        if len(self.items) * self.item_height > self.rect.h:
            total_h = len(self.items) * self.item_height
            bar_h = max(20, int(self.rect.h * self.rect.h / total_h))
            bar_y = int(self.scroll / total_h * self.rect.h)
            bar_rect = pygame.Rect(self.rect.right - 6, self.rect.y + bar_y, 4, bar_h)
            pygame.draw.rect(surf, C_BORDER, bar_rect, border_radius=2)

        pygame.draw.rect(surf, C_BORDER, self.rect, 1)
        surf.set_clip(clip)


# ─────────────────────────────────────────────
#  NOTIFICATION TOAST
# ─────────────────────────────────────────────
class NotificationSystem:
    def __init__(self):
        self.toasts: list[dict] = []

    def add(self, msg: str, ntype: str = "info"):
        self.toasts.append({
            "msg": msg, "type": ntype,
            "age": 0.0, "duration": 4.0 + len(msg) * 0.04
        })
        if len(self.toasts) > 5:
            self.toasts.pop(0)

    def tick(self, dt: float):
        for t in self.toasts[:]:
            t["age"] += dt
            if t["age"] >= t["duration"]:
                self.toasts.remove(t)

    def draw(self, surf: pygame.Surface):
        fonts = Fonts.get()
        sw = surf.get_width()
        y = surf.get_height() - 20
        for toast in reversed(self.toasts):
            alpha = 1.0
            age = toast["age"]
            dur = toast["duration"]
            if age < 0.3:
                alpha = age / 0.3
            elif age > dur - 0.5:
                alpha = (dur - age) / 0.5
            alpha = max(0.0, min(1.0, alpha))

            color = type_color(toast["type"])
            msg = toast["msg"]
            # Truncate
            if len(msg) > 80:
                msg = msg[:77] + "..."

            tw, th = fonts.sm.size(msg)
            w = tw + 24
            x = sw - w - 20
            y -= th + 16

            box = pygame.Surface((w, th + 12), pygame.SRCALPHA)
            bc = (*lerp_color(C_PANEL, color, 0.15), int(230 * alpha))
            pygame.draw.rect(box, bc, (0, 0, w, th + 12), border_radius=6)
            bc2 = (*color, int(200 * alpha))
            pygame.draw.rect(box, bc2, (0, 0, w, th + 12), 1, border_radius=6)
            # Left accent
            pygame.draw.rect(box, (*color, int(255 * alpha)), (0, 0, 4, th + 12), border_radius=3)

            tc = (*C_WHITE, int(255 * alpha))
            txt_surf = fonts.sm.render(msg, True, C_WHITE)
            box.blit(txt_surf, (14, 6))
            surf.blit(box, (x, y))


# ─────────────────────────────────────────────
#  MINI CHART
# ─────────────────────────────────────────────
def draw_mini_chart(surf: pygame.Surface, data: list, rect,
                    color=C_GOLD, bg=C_PANEL2, label: str = ""):
    fonts = Fonts.get()
    x, y, w, h = rect
    pygame.draw.rect(surf, bg, rect, border_radius=4)
    pygame.draw.rect(surf, C_BORDER, rect, 1, border_radius=4)

    if not data or max(data) <= 0:
        draw_text(surf, "Keine Daten", fonts.xxs, C_GRAY, x + w // 2, y + h // 2, "center")
        return

    mn = min(data)
    mx = max(data)
    rng = mx - mn if mx != mn else 1

    pts = []
    for i, v in enumerate(data):
        px = x + int(i / (len(data) - 1) * (w - 8)) + 4
        py = y + h - 4 - int((v - mn) / rng * (h - 12))
        pts.append((px, py))

    if len(pts) >= 2:
        # Fill area
        fill_pts = [(pts[0][0], y + h - 4)] + pts + [(pts[-1][0], y + h - 4)]
        fill_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        fill_col = (*color, 40)
        pygame.draw.polygon(fill_surf, fill_col,
            [(p[0] - x, p[1] - y) for p in fill_pts])
        surf.blit(fill_surf, (x, y))
        pygame.draw.lines(surf, color, False, pts, 2)

    for pt in pts[::max(1, len(pts) // 5)]:
        pygame.draw.circle(surf, color, pt, 3)

    if label:
        draw_text(surf, label, fonts.xxs, C_GRAY, x + 4, y + 4, "topleft")
    # Last value
    if data:
        draw_text(surf, format_money(data[-1]), fonts.xxs, color, x + w - 4, y + 4, "topright")


# ─────────────────────────────────────────────
#  DÖNER ICON DRAWER (ASCII art style)
# ─────────────────────────────────────────────
def draw_doener_icon(surf: pygame.Surface, cx: int, cy: int, size: int = 40, anim: float = 0.0):
    """Draw a simple kebab/döner icon."""
    wobble = math.sin(anim * 3) * 2
    # Spit (vertical line)
    pygame.draw.line(surf, C_GRAY, (cx, cy - size), (cx, cy + size), 3)
    # Meat layers
    layer_colors = [
        (180, 80, 50), (200, 100, 60), (170, 70, 40),
        (190, 90, 55), (160, 65, 35)
    ]
    for i, lc in enumerate(layer_colors):
        offset = math.sin(anim * 2 + i) * wobble
        ly = cy - size + size//3 + i * (size * 2 // len(layer_colors))
        lw = size + int(math.sin(i * 0.8) * size // 3)
        lh = size // 4
        pygame.draw.ellipse(surf, lc,
            (cx - lw // 2 + offset, ly - lh // 2, lw, lh))
    # Top cap
    pygame.draw.circle(surf, C_GOLD, (cx, cy - size), size // 6)

# ─────────────────────────────────────────────
#  TAB BAR
# ─────────────────────────────────────────────
class TabBar:
    def __init__(self, rect, tabs: list[str], active: int = 0):
        self.rect = pygame.Rect(rect)
        self.tabs = tabs
        self.active = active
        self.tab_w = self.rect.w // len(tabs)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if self.rect.collidepoint(mx, my):
                idx = (mx - self.rect.x) // self.tab_w
                if 0 <= idx < len(self.tabs):
                    self.active = idx
                    return True
        return False

    def draw(self, surf: pygame.Surface):
        fonts = Fonts.get()
        pygame.draw.rect(surf, C_PANEL2, self.rect)
        for i, tab in enumerate(self.tabs):
            tx = self.rect.x + i * self.tab_w
            tr = pygame.Rect(tx, self.rect.y, self.tab_w, self.rect.h)
            if i == self.active:
                pygame.draw.rect(surf, C_PANEL, tr)
                pygame.draw.line(surf, C_GOLD, (tr.x, tr.bottom - 2), (tr.right, tr.bottom - 2), 2)
                tc = C_GOLD
            else:
                tc = C_GRAY
            draw_text(surf, tab, fonts.sm, tc, tr.centerx, tr.centery, "center")
            if i > 0:
                pygame.draw.line(surf, C_BORDER, (tx, self.rect.y + 4), (tx, self.rect.bottom - 4))
        pygame.draw.rect(surf, C_BORDER, self.rect, 1)


# ─────────────────────────────────────────────
#  DIALOG / MODAL
# ─────────────────────────────────────────────
class Modal:
    def __init__(self, title: str, message: str, buttons: list[dict] = None):
        self.title = title
        self.message = message
        self.buttons = buttons or [{"label": "OK", "color": C_GOLD, "result": True}]
        self.result = None
        self.open = True
        self._btns: list[Button] = []
        self._build_buttons()

    def _build_buttons(self):
        sw, sh = SCREEN_W, SCREEN_H
        bw = 120
        gap = 16
        total = len(self.buttons) * bw + (len(self.buttons) - 1) * gap
        bx = sw // 2 - total // 2
        by = sh // 2 + 60
        self._btns = []
        for i, bd in enumerate(self.buttons):
            def make_cb(r):
                def cb():
                    self.result = r
                    self.open = False
                return cb
            btn = Button(
                (bx + i * (bw + gap), by, bw, 36),
                bd["label"], bd.get("color", C_GOLD),
                callback=make_cb(bd.get("result", True))
            )
            self._btns.append(btn)

    def handle_event(self, event: pygame.event.Event):
        for btn in self._btns:
            btn.handle_event(event)

    def draw(self, surf: pygame.Surface):
        fonts = Fonts.get()
        # Overlay
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surf.blit(overlay, (0, 0))

        # Box
        bw, bh = 500, 200
        bx = SCREEN_W // 2 - bw // 2
        by = SCREEN_H // 2 - bh // 2
        box_rect = pygame.Rect(bx, by, bw, bh)
        draw_rect_rounded(surf, C_PANEL, box_rect, 10, 2, C_GOLD)

        draw_text(surf, self.title, fonts.lg, C_GOLD, SCREEN_W // 2, by + 30, "center")
        draw_text(surf, self.message, fonts.sm, C_WHITE, SCREEN_W // 2, by + 80,
                  "center", max_width=460)

        for btn in self._btns:
            btn.draw(surf)
