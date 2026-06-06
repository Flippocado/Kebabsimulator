# DÖNERIMPERIUM™ - Main Game Loop
# ==================================
from __future__ import annotations
import pygame
import sys
import os
from typing import Optional

# Sicherstellen, dass src/ im Suchpfad ist (für direkten Start aus src/)
_SRC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src")
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)

from constants import *
from iconloader import set_window_icon
from gamestate import GameState
from ui_components import Fonts, NotificationSystem
from screens import (
    MainMenuScreen, LoadMenuScreen, DifficultyScreen, AchievementsScreen,
    OverviewScreen, BranchesScreen,
    ResearchScreen, StatisticsScreen, FinanceScreen, OptionsScreen, HUD
)


class Game:
    def __init__(self):
        pygame.init()
        set_window_icon()  # Döner.ico setzen
        pygame.display.set_caption(TITLE)
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.gs = GameState()
        self.notif = NotificationSystem()
        self.hud: Optional[HUD] = None
        self.last_event: Optional[pygame.event.Event] = None

        self._screens: dict = {}
        self.current_screen_name = "main_menu"
        self._current_screen = None
        self._in_game = False

        self._build_main_menu()

    def _build_main_menu(self):
        self.pending_company_name = ""
        self._screens = {"main_menu": MainMenuScreen(self), "load_menu": LoadMenuScreen(self), "difficulty": DifficultyScreen(self)}
        self._current_screen = self._screens["main_menu"]
        self.current_screen_name = "main_menu"
        self._in_game = False

    def _build_game_screens(self):
        self._screens = {
            "overview":   OverviewScreen(self),
            "branches":   BranchesScreen(self),
            "staff":      BranchesScreen(self),  # reuse with tab preselect
            "research":   ResearchScreen(self),
            "stats":      StatisticsScreen(self),
            "finance":    FinanceScreen(self),
            "options":    OptionsScreen(self),
        }
        self.hud = HUD(self)
        self._in_game = True

    def set_screen(self, name: str):
        if name == "achievements":
            prev = self.current_screen_name
            self._screens["achievements"] = AchievementsScreen(self)
            self._screens["achievements"]._prev_screen = prev if prev != "achievements" else "overview"
            self._current_screen = self._screens["achievements"]
            self.current_screen_name = "achievements"
            return
        if name == "difficulty":
            self._screens["difficulty"] = DifficultyScreen(self)
            self._current_screen = self._screens["difficulty"]
            self.current_screen_name = "difficulty"
            return
        if name == "main_menu":
            self._build_main_menu()
            return
        if name == "load_menu":
            if "load_menu" not in self._screens:
                self._screens["load_menu"] = LoadMenuScreen(self)
            self._current_screen = self._screens["load_menu"]
            self.current_screen_name = "load_menu"
            return
        if name in self._screens:
            self._current_screen = self._screens[name]
            self.current_screen_name = name
            # Pre-select staff tab when navigating to 'staff'
            if name == "staff":
                self._current_screen.tab.active = 2
                # Erste Filiale automatisch auswaehlen falls noch keine gewaehlt
                if self._current_screen.selected_idx < 0 and self.gs.branches:
                    self._current_screen.selected_idx = 0

    def start_new_game(self, company_name: str, difficulty: dict = None):
        self.gs = GameState()
        self.gs.company_name = company_name
        if difficulty:
            self.gs.difficulty = difficulty["key"]
        # Open first branch automatically
        self.gs.open_branch(f"{company_name} #1", "kleinststadt", "Dönerhausen")
        diff_label = difficulty["label"] if difficulty else "Normal"
        self.gs.add_notification(f"Willkommen bei {company_name}! Schwierigkeit: {diff_label}", "success")
        self.gs.add_notification("Tipp: Stelle Mitarbeiter ein und passe dein Rezept an!", "info")
        self._build_game_screens()
        self.set_screen("overview")

    def load_game(self, slot: int):
        gs = GameState.load(slot)
        if gs:
            self.gs = gs
            self.gs.add_notification(f"Spiel geladen! Tag {gs.day}, {format_from_constants(gs.money)}", "success")
            self._build_game_screens()
            self.set_screen("overview")
        else:
            self.notif.add("Kein Speicherstand in diesem Slot!", "danger")

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            dt = min(dt, 0.1)  # cap dt

            self.last_event = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                if event.type == pygame.VIDEORESIZE:
                    continue  # pygame 2.x handles this automatically
                self.last_event = event
                if self.hud and self._in_game:
                    self.hud.handle_event(event)
                if self._current_screen:
                    self._current_screen.handle_event(event)

            # Update
            if self._in_game:
                self.gs.advance_time(dt)
                self.gs.tick_notifications(dt)
                self.notif.tick(dt)
                # Sync gs notifications to notif system
                for n in self.gs.notifications:
                    if n.get("age", 0) < dt * 2:
                        self.notif.add(n["msg"], n.get("type", "info"))

            if self.hud:
                self.hud.update(dt)
            if self._current_screen:
                self._current_screen.update(dt)

            # Draw directly to screen (which is now the real window size via SCREEN_W()/SCREEN_H())
            self.screen.fill(C_BG)
            if self._current_screen:
                self._current_screen.draw(self.screen)
            if self.hud and self._in_game:
                self.hud.draw(self.screen)
            self.notif.draw(self.screen)

            # FPS counter (debug)
            fps = self.clock.get_fps()
            fonts = Fonts.get()
            fps_surf = fonts.xxs.render(f"FPS: {fps:.0f}", True, C_GRAY2)
            self.screen.blit(fps_surf, (5, SCREEN_H() - 18))

            pygame.display.flip()

        pygame.quit()
        sys.exit()


def format_from_constants(money: float) -> str:
    if abs(money) >= 1_000_000:
        return f"{money/1_000_000:.2f}Mio€"
    if abs(money) >= 1_000:
        return f"{money/1_000:.1f}K€"
    return f"{money:.2f}€"


if __name__ == "__main__":
    os.makedirs(SAVES_DIR, exist_ok=True)
    game = Game()
    game.run()