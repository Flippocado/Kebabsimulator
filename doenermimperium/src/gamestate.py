# DÖNERIMPERIUM™ - Game State
# ============================
from __future__ import annotations
import random
import math
import json
import os
import time
from typing import Optional
from constants import *
from entities import Branch, Customer, StaffMember, DoenemRecipe, Supplier, ResearchNode, Competitor


def _build_research_tree() -> dict[str, ResearchNode]:
    nodes = {
        "schnittmaschine": ResearchNode(
            "schnittmaschine", "Automatischer Döner-Schneider",
            "Erhöht die Produktionsgeschwindigkeit um 30%.",
            cost=5000, duration_days=7,
            effect={"speed_mod": 1.3}
        ),
        "premium_zutaten": ResearchNode(
            "premium_zutaten", "Premium-Zutaten-Programm",
            "Schaltet Premium-Fleisch und Bio-Gemüse frei. Qualität +2.",
            cost=8000, duration_days=14,
            effect={"quality_mod": 2.0}
        ),
        "ki_kasse": ResearchNode(
            "ki_kasse", "KI-Kassensystem",
            "Reduziert Wartezeiten. Kunden-Durchsatz +25%.",
            cost=12000, duration_days=10, requires=["schnittmaschine"],
            effect={"throughput_mod": 1.25}
        ),
        "schnelle_lieferung": ResearchNode(
            "schnelle_lieferung", "Expresslieferdienst",
            "Lieferengpässe werden schneller behoben.",
            cost=7000, duration_days=7,
            effect={"supply_resilience": 0.5}
        ),
        "eigene_logistik": ResearchNode(
            "eigene_logistik", "Eigenes Logistikzentrum",
            "Senkt Lieferkosten um 20%. Stabile Versorgung.",
            cost=50000, duration_days=30, requires=["schnelle_lieferung"],
            effect={"cost_mod": 0.8}
        ),
        "franchise": ResearchNode(
            "franchise", "Franchise-System",
            "Ermöglicht Franchise-Filialen. Passives Einkommen!",
            cost=80000, duration_days=45, requires=["ki_kasse"],
            effect={"franchise_enabled": True}
        ),
        "brotfabrik": ResearchNode(
            "brotfabrik", "Eigene Brotfabrik",
            "Produziert Brot in Eigenregie. Brotkosten -60%.",
            cost=200000, duration_days=60, requires=["eigene_logistik"],
            effect={"bread_cost_mod": 0.4}
        ),
        "fleischproduktion": ResearchNode(
            "fleischproduktion", "Eigene Fleischproduktion",
            "Eigene Produktion. Fleischkosten -50%. Qualität +1.",
            cost=500000, duration_days=90, requires=["brotfabrik"],
            effect={"meat_cost_mod": 0.5, "quality_mod": 1.0}
        ),
        "solar_energie": ResearchNode(
            "solar_energie", "Solarenergie-System",
            "Senkt Stromkosten. Stromausfälle weniger häufig.",
            cost=25000, duration_days=14,
            effect={"energy_resilience": True, "cost_mod": 0.95}
        ),
        "loyalty_app": ResearchNode(
            "loyalty_app", "Döner-Loyalty-App",
            "Kundenbindungs-App. Stammkunden +40%.",
            cost=15000, duration_days=21, requires=["ki_kasse"],
            effect={"loyalty_mod": 1.4}
        ),
        "geheimrezept": ResearchNode(
            "geheimrezept", "Geheimes Familienrezept",
            "Legendäre Soße. Qualität massiv verbessert. Ruf +20.",
            cost=30000, duration_days=30, requires=["premium_zutaten"],
            effect={"quality_mod": 3.0, "reputation_bonus": 20}
        ),
        "mega_grill": ResearchNode(
            "mega_grill", "Mega-Drehspieß 3000",
            "Industriegrill. Kapazität +100%. Kunden pro Stunde verdoppelt.",
            cost=40000, duration_days=21, requires=["schnittmaschine"],
            effect={"capacity_mod": 2.0}
        ),
    }
    return nodes


class GameState:
    def __init__(self):
        self.money = STARTING_MONEY
        self.day = 1
        self.hour = 8
        self.minute = 0
        self.tick = 0
        self.difficulty = "normal"  # easy / normal / hard
        self.game_speed = 1.0
        self.paused = False

        # Company
        self.company_name = "DÖNERIMPERIUM™"
        self.total_revenue = 0.0
        self.total_expenses = 0.0
        self.total_customers_served = 0
        self.market_share = 0.05
        self.loan_debt = 0.0
        self.loan_monthly_payment = 0.0

        # Branches
        self.branches: list[Branch] = []

        # Research
        self.research_tree: dict[str, ResearchNode] = _build_research_tree()
        self.active_research: Optional[str] = None
        self.research_progress_days = 0

        # Competitors
        self.competitors: list[Competitor] = []

        # Notifications queue
        self.notifications: list[dict] = []

        # Revenue history (last 30 days)
        self.revenue_history: list[float] = [0.0] * 30
        self.customer_history: list[int] = [0] * 30
        self.expense_history: list[float] = [0.0] * 30

        # Achievement / victory tracking
        self.victories_achieved: set[str] = set()
        self.unlocked_achievements: set[str] = set()

        # Statistics
        self.total_branches_ever = 0
        self.countries_present: set[str] = set()

        # Accumulated ticks for simulation
        self._tick_acc = 0.0

        # Humor timer
        self._humor_timer = 0.0
        self._humor_interval = random.uniform(45, 120)

    # ─── TIME ─────────────────────────────────
    def advance_time(self, dt_seconds: float):
        if self.paused:
            return

        self._tick_acc += dt_seconds * self.game_speed
        ticks_to_process = int(self._tick_acc / TICK_RATE)
        self._tick_acc -= ticks_to_process * TICK_RATE

        for _ in range(min(ticks_to_process, 10)):
            self._process_tick()

        # Humor messages
        self._humor_timer += dt_seconds * self.game_speed
        if self._humor_timer >= self._humor_interval:
            self._humor_timer = 0.0
            self._humor_interval = random.uniform(45, 120)
            if random.random() < 0.7:
                msg = random.choice(HUMOR_MESSAGES)
                self.add_notification(msg[1], msg[0])

    def _process_tick(self):
        self.tick += 1
        self.minute = (self.minute + 10) % 60
        if self.minute == 0:
            self._process_hour()

    def _process_hour(self):
        self.hour = (self.hour + 1) % 24
        if self.hour == 0:
            self._process_day()
        else:
            # Simulate customers for open branches
            for branch in self.branches:
                if branch.is_open and branch.open_hour <= self.hour < branch.close_hour:
                    self._simulate_branch_hour(branch)


    def _diff(self) -> dict:
        """Returns difficulty multipliers."""
        return {
            "easy":   {"hygiene_decay": 1.0, "morale_decay": 1.0, "event_prob": 1.0,  "comp_aggression": 1.0,  "satisfaction_threshold": 0.4},
            "normal": {"hygiene_decay": 1.4, "morale_decay": 1.3, "event_prob": 1.4,  "comp_aggression": 1.5,  "satisfaction_threshold": 0.48},
            "hard":   {"hygiene_decay": 2.0, "morale_decay": 1.8, "event_prob": 1.8,  "comp_aggression": 2.0,  "satisfaction_threshold": 0.55},
        }.get(self.difficulty, {"hygiene_decay": 1.0, "morale_decay": 1.0, "event_prob": 1.0, "comp_aggression": 1.0, "satisfaction_threshold": 0.4})

    def _simulate_branch_hour(self, branch: Branch):
        n_customers = branch.get_hourly_customers(self.hour)
        for recipe in branch.recipes:
            for _ in range(max(0, n_customers // len(branch.recipes))):
                self._serve_customer(branch, recipe)

    def _serve_customer(self, branch: Branch, recipe: DoenemRecipe):
        ctype = self._pick_customer_type(self.hour)
        customer = Customer(ctype, branch)

        # Check if customer stays based on hygiene + reputation
        abandon_chance = max(0, (100 - branch.hygiene) / 200.0 + (50 - branch.reputation) / 200.0)
        if random.random() < abandon_chance:
            return

        # Check budget
        if customer.budget < recipe.price * 0.7:
            return

        # Calculate satisfaction
        sauce_match = customer.fav_sauce == recipe.sosse
        quality = recipe.quality_score()

        # Apply research bonuses
        quality += self._get_quality_bonus()

        # quality_score() liefert 5.0-10.0, calc_satisfaction erwartet 0.0-1.0
        # Normierung: (quality - 5) / 5 -> 0.0 bei Basis, 1.0 bei Maximum
        quality_normalized = (quality - 5.0) / 5.0
        satisfaction = customer.calc_satisfaction(recipe.price, quality_normalized, sauce_match, 45.0)

        # Revenue
        actual_price = min(recipe.price, customer.budget)
        ingredient_cost = recipe.ingredient_cost() * self._get_cost_mod()

        revenue = actual_price
        profit = revenue - ingredient_cost

        branch.daily_revenue += profit
        branch.total_revenue += revenue
        branch.daily_customers += 1
        branch.total_customers += 1
        branch.sauce_popularity[recipe.sosse] = branch.sauce_popularity.get(recipe.sosse, 0) + 1

        self.money += profit
        self.total_revenue += revenue
        self.total_expenses += ingredient_cost   # track ingredient cost as expense
        self.total_customers_served += 1

        # Reputation update: satisfaction 0.0-1.0, Schwelle bei 0.5
        rep_change = (satisfaction - self._diff()["satisfaction_threshold"]) * 0.3
        branch.reputation = max(0, min(100, branch.reputation + rep_change))

    def _pick_customer_type(self, hour: int) -> str:
        weights = []
        for ctype, cfg in CUSTOMER_RATES.items():
            if hour in cfg["peak"]:
                weights.append(cfg["rate"] * 2)
            else:
                weights.append(max(1, cfg["rate"] // 3))
        total = sum(weights)
        r = random.random() * total
        for i, (ctype, _) in enumerate(CUSTOMER_RATES.items()):
            r -= weights[i]
            if r <= 0:
                return ctype
        return "student"

    def _get_quality_bonus(self) -> float:
        bonus = 0.0
        for nid, node in self.research_tree.items():
            if node.unlocked and "quality_mod" in node.effect:
                bonus += node.effect["quality_mod"]
        return bonus

    def _get_cost_mod(self) -> float:
        mod = 1.0
        for nid, node in self.research_tree.items():
            if node.unlocked and "cost_mod" in node.effect:
                mod *= node.effect["cost_mod"]
        return mod

    def _process_day(self):
        self.day += 1

        # Deduct monthly costs on day 1 of each month
        if self.day % 30 == 1:
            self._process_monthly()

        # Daily expenses (proportional)
        total_daily_expenses = 0.0
        for branch in self.branches:
            daily_cost = branch.monthly_fixed_costs() / 30.0
            branch.daily_expenses = daily_cost
            total_daily_expenses += daily_cost

        self.money -= total_daily_expenses
        self.total_expenses += total_daily_expenses

        # Research progress
        if self.active_research:
            node = self.research_tree.get(self.active_research)
            if node and node.researching:
                self.research_progress_days += 1
                node.progress = self.research_progress_days / node.duration_days
                if self.research_progress_days >= node.duration_days:
                    node.unlocked = True
                    node.researching = False
                    self.active_research = None
                    self.research_progress_days = 0
                    self.add_notification(f"Forschung abgeschlossen: {node.name}!", "success")
                    self._apply_research_effect(node)

        # Competitor ticks
        for comp in self.competitors:
            comp.tick_day(self._diff()["comp_aggression"])

        # Random events
        self._check_random_events()

        # Victory check
        self._check_victory()
        self._check_achievements()

        # Update histories BEFORE resetting daily counters
        day_idx = (self.day - 1) % 30
        daily_rev = sum(b.daily_revenue for b in self.branches)
        daily_cust = sum(b.daily_customers for b in self.branches)
        self.revenue_history[day_idx] = daily_rev
        self.customer_history[day_idx] = daily_cust
        self.expense_history[day_idx] = total_daily_expenses

        # Update market share based on player customers vs competitors
        # Assume each competitor is roughly a mid-size location (~800 foot traffic * 12h * share)
        BASE_COMP_DAILY = 800 * 12
        comp_customers = sum(
            max(1, int(c.market_share * BASE_COMP_DAILY)) for c in self.competitors
        ) if self.competitors else daily_cust * 5
        total_customers = max(1, daily_cust + comp_customers)
        target_share = daily_cust / total_customers
        # Smooth so it doesn't jump wildly day to day
        self.market_share = self.market_share * 0.95 + target_share * 0.05
        self.market_share = max(0.001, min(0.99, self.market_share))

        # Now reset daily counters via tick_day
        _d = self._diff()
        for branch in self.branches:
            branch.tick_day(_d["hygiene_decay"], _d["morale_decay"])

        # Add competitors for new cities
        if self.day % 60 == 0 and self.branches:
            self._maybe_add_competitor()

        # Bankruptcy check
        if self.money < -50000:
            self.add_notification("BANKROTT! Du bist pleite! Spiel verloren!", "danger")

    def _process_monthly(self):
        # Deduct loan payments
        if self.loan_monthly_payment > 0:
            self.money -= self.loan_monthly_payment
            self.total_expenses += self.loan_monthly_payment
            self.add_notification(
                f"Kreditrate: -{self.loan_monthly_payment:.0f}€ (Schulden: {self.loan_debt:.0f}€)",
                "warn"
            )
        # Monthly summary notification
        monthly_rev = sum(self.revenue_history)
        self.add_notification(
            f"Monatsabschluss: {monthly_rev:.0f}€ Umsatz, {len(self.branches)} Filialen",
            "info"
        )

    def _apply_research_effect(self, node: ResearchNode):
        if "reputation_bonus" in node.effect:
            for b in self.branches:
                b.reputation = min(100, b.reputation + node.effect["reputation_bonus"])
        if "capacity_mod" in node.effect:
            for b in self.branches:
                b.capacity = int(b.capacity * node.effect["capacity_mod"])

    def _check_random_events(self):
        for ev_template in RANDOM_EVENTS:
            if random.random() < ev_template["probability"] * self._diff()["event_prob"]:
                target_branch = random.choice(self.branches) if self.branches else None
                if target_branch:
                    ev = dict(ev_template)
                    ev["remaining"] = ev.get("duration", 1)

                    # Hygiene check event
                    if ev["effect"].get("hygiene_check"):
                        if target_branch.hygiene < 50:
                            penalty = random.uniform(500, 2000)
                            self.money -= penalty
                            self.add_notification(
                                f"Gesundheitsamt: Bußgeld {penalty:.0f}€ für {target_branch.name}!",
                                "danger"
                            )
                        else:
                            self.add_notification(
                                f"Lebensmittelkontrolle bestanden! Hygiene-Bonus für {target_branch.name}!",
                                "success"
                            )
                        continue

                    target_branch.active_events.append(ev)
                    self.add_notification(
                        f"{target_branch.name}: {ev['name']} — {ev['desc']}", ev["type"]
                    )

    def _check_victory(self):
        total_branches = len(self.branches)
        countries = len(self.countries_present)

        if total_branches >= 500 and "branches_500" not in self.victories_achieved:
            self.victories_achieved.add("branches_500")
            self.add_notification("🏆 SIEG! 500 Filialen erreicht! DÖNERIMPERIUM™ ist vollständig!", "success")

        if self.total_revenue >= 1_000_000_000 and "milliarde" not in self.victories_achieved:
            self.victories_achieved.add("milliarde")
            self.add_notification("🏆 SIEG! Eine MILLIARDE Euro Umsatz! Legendär!", "success")

        if countries >= 20 and "europa" not in self.victories_achieved:
            self.victories_achieved.add("europa")
            self.add_notification("🏆 SIEG! Europaweit! DÖNERIMPERIUM™ erobert Europa!", "success")


    def _check_achievements(self):
        from screens import ACHIEVEMENTS
        for ach in ACHIEVEMENTS:
            permanent = ach.get("permanent", True)
            try:
                currently_met = ach["check"](self)
            except Exception:
                continue
            if permanent:
                # Lock in forever once met
                if currently_met and ach["id"] not in self.unlocked_achievements:
                    self.unlocked_achievements.add(ach["id"])
                    self.add_notification(f"Achievement freigeschaltet: {ach['name']}!", "success")
            else:
                # Live: update each day, notify only on first unlock
                if currently_met:
                    if ach["id"] not in self.unlocked_achievements:
                        self.add_notification(f"Achievement freigeschaltet: {ach['name']}!", "success")
                    self.unlocked_achievements.add(ach["id"])
                else:
                    self.unlocked_achievements.discard(ach["id"])

    def _maybe_add_competitor(self):
        cfg = random.choice(COMPETITOR_TYPES)
        cities = [b.city for b in self.branches]
        if cities:
            city = random.choice(cities)
            comp = Competitor(cfg, city)
            self.competitors.append(comp)
            self.add_notification(f"Neue Konkurrenz: {comp.name} eröffnet in {city}!", "warn")

    # ─── BRANCH MANAGEMENT ────────────────────
    def open_branch(self, name: str, location_type: str, city: str, country: str = "Deutschland") -> Optional[Branch]:
        cfg = LOCATION_TYPES.get(location_type, LOCATION_TYPES["kleinststadt"])
        setup_cost = cfg["rent"] * 3
        if self.money < setup_cost:
            self.add_notification(f"Zu wenig Geld für neue Filiale! Benötigt: {setup_cost:.0f}€", "danger")
            return None

        self.money -= setup_cost
        branch = Branch(name, location_type, city, country)
        # Add one starter azubi (cheap), player hires more manually
        branch.staff.append(StaffMember("azubi", 1))
        self.branches.append(branch)
        self.total_branches_ever += 1
        self.countries_present.add(country)
        self.add_notification(f"Neue Filiale '{name}' in {city} eröffnet! Kosten: {setup_cost:.0f}€", "success")
        return branch

    def close_branch(self, idx: int):
        if 0 <= idx < len(self.branches):
            b = self.branches.pop(idx)
            self.add_notification(f"Filiale '{b.name}' geschlossen.", "warn")

    # ─── RESEARCH ─────────────────────────────
    def start_research(self, node_id: str) -> bool:
        node = self.research_tree.get(node_id)
        if not node or node.unlocked or node.researching:
            return False
        # Check requirements
        for req in node.requires:
            if not self.research_tree[req].unlocked:
                self.add_notification(f"Voraussetzung fehlt: {self.research_tree[req].name}", "warn")
                return False
        if self.money < node.cost:
            self.add_notification(f"Zu wenig Geld für Forschung: {node.cost:.0f}€", "danger")
            return False
        if self.active_research:
            self.add_notification("Es läuft bereits eine Forschung!", "warn")
            return False

        self.money -= node.cost
        node.researching = True
        self.active_research = node_id
        self.research_progress_days = 0
        self.add_notification(f"Forschung gestartet: {node.name}!", "info")
        return True

    # ─── NOTIFICATIONS ─────────────────────────
    def add_notification(self, msg: str, ntype: str = "info"):
        # Deduplicate: skip if same message was added within last 3 ticks
        if self.notifications:
            last = self.notifications[-1]
            if last["msg"] == msg and last["age"] < 3.0:
                return
        self.notifications.append({
            "msg": msg, "type": ntype,
            "time": self.day * 24 + self.hour,
            "age": 0.0
        })
        # Keep last 50
        if len(self.notifications) > 50:
            self.notifications.pop(0)

    def tick_notifications(self, dt: float):
        for n in self.notifications:
            n["age"] += dt

    # ─── SAVE / LOAD ───────────────────────────
    def to_dict(self) -> dict:
        return {
            "version": "1.0",
            "money": self.money,
            "day": self.day,
            "hour": self.hour,
            "minute": self.minute,
            "tick": self.tick,
            "company_name": self.company_name,
            "total_revenue": self.total_revenue,
            "total_expenses": self.total_expenses,
            "total_customers_served": self.total_customers_served,
            "difficulty": self.difficulty,
            "market_share": self.market_share,
            "loan_debt": self.loan_debt,
            "loan_monthly_payment": self.loan_monthly_payment,
            "branches": [b.to_dict() for b in self.branches],
            "research_tree": {k: v.to_dict() for k, v in self.research_tree.items()},
            "active_research": self.active_research,
            "research_progress_days": self.research_progress_days,
            "competitors": [c.to_dict() for c in self.competitors],
            "notifications": self.notifications[-20:],
            "revenue_history": self.revenue_history,
            "customer_history": self.customer_history,
            "expense_history": self.expense_history,
            "victories_achieved": list(self.victories_achieved),
            "unlocked_achievements": list(self.unlocked_achievements),
            "total_branches_ever": self.total_branches_ever,
            "countries_present": list(self.countries_present),
            "game_speed": self.game_speed,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "GameState":
        gs = cls()
        gs.money = d["money"]
        gs.day = d["day"]
        gs.hour = d["hour"]
        gs.minute = d.get("minute", 0)
        gs.tick = d.get("tick", 0)
        gs.company_name = d.get("company_name", "DÖNERIMPERIUM™")
        gs.total_revenue = d["total_revenue"]
        gs.total_expenses = d["total_expenses"]
        gs.total_customers_served = d["total_customers_served"]
        gs.difficulty = d.get("difficulty", "normal")
        gs.market_share = d["market_share"]
        gs.loan_debt = d.get("loan_debt", 0.0)
        gs.loan_monthly_payment = d.get("loan_monthly_payment", 0.0)
        gs.branches = [Branch.from_dict(b) for b in d["branches"]]
        rt = _build_research_tree()
        for k, v in d.get("research_tree", {}).items():
            if k in rt:
                rt[k].unlocked = v.get("unlocked", False)
                rt[k].researching = v.get("researching", False)
                rt[k].progress = v.get("progress", 0.0)
        gs.research_tree = rt
        gs.active_research = d.get("active_research")
        gs.research_progress_days = d.get("research_progress_days", 0)
        gs.competitors = [Competitor.from_dict(c) for c in d.get("competitors", [])]
        gs.notifications = d.get("notifications", [])
        gs.revenue_history = d.get("revenue_history", [0.0] * 30)
        gs.customer_history = d.get("customer_history", [0] * 30)
        gs.expense_history = d.get("expense_history", [0.0] * 30)
        gs.victories_achieved = set(d.get("victories_achieved", []))
        gs.unlocked_achievements = set(d.get("unlocked_achievements", []))
        gs.total_branches_ever = d.get("total_branches_ever", len(gs.branches))
        gs.countries_present = set(d.get("countries_present", ["Deutschland"]))
        gs.game_speed = d.get("game_speed", 1.0)
        return gs

    def save(self, slot: int = 0):
        os.makedirs(SAVES_DIR, exist_ok=True)
        path = os.path.join(SAVES_DIR, f"save_{slot}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        self.add_notification(f"Spiel gespeichert (Slot {slot+1})!", "success")

    @classmethod
    def load(cls, slot: int = 0) -> Optional["GameState"]:
        path = os.path.join(SAVES_DIR, f"save_{slot}.json")
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    @staticmethod
    def save_exists(slot: int = 0) -> bool:
        path = os.path.join(SAVES_DIR, f"save_{slot}.json")
        return os.path.exists(path)