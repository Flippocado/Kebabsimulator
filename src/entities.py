# DÖNERIMPERIUM™ - Game Entities
# ================================
from __future__ import annotations
import random
import math
from dataclasses import dataclass, field
from typing import Optional
from constants import *


# ─────────────────────────────────────────────
#  CUSTOMER
# ─────────────────────────────────────────────
class Customer:
    TYPES = list(CUSTOMER_RATES.keys())
    SAUCE_PREFS = list(SAUCE_NAMES.keys())

    def __init__(self, ctype: str = None, branch=None):
        self.ctype = ctype or random.choice(self.TYPES)
        self.branch = branch

        # Attributes
        cfg = {
            "schueler":    {"budget": (2.5, 4.5),  "patience": (30, 60),  "loyalty_gain": 0.3},
            "student":     {"budget": (3.0, 6.0),  "patience": (40, 80),  "loyalty_gain": 0.4},
            "bueroangest": {"budget": (5.0, 9.0),  "patience": (20, 40),  "loyalty_gain": 0.6},
            "handwerker":  {"budget": (4.0, 8.0),  "patience": (35, 70),  "loyalty_gain": 0.5},
            "familie":     {"budget": (8.0, 20.0), "patience": (50, 90),  "loyalty_gain": 0.7},
            "tourist":     {"budget": (6.0, 15.0), "patience": (60, 120), "loyalty_gain": 0.2},
            "stammkunde":  {"budget": (4.0, 8.0),  "patience": (60, 120), "loyalty_gain": 0.9},
        }[self.ctype]

        self.budget = random.uniform(*cfg["budget"])
        self.patience = random.uniform(*cfg["patience"])
        self.max_patience = self.patience
        self.loyalty_gain = cfg["loyalty_gain"]
        self.fav_sauce = random.choice(self.SAUCE_PREFS)
        self.brand_loyalty = random.uniform(0.0, 1.0) if self.ctype == "stammkunde" else random.uniform(0.0, 0.4)
        self.hunger = random.uniform(0.5, 1.0)

        # State
        self.satisfied = False
        self.left = False
        self.paid = 0.0
        self.wait_time = 0.0
        self.order = None
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.anim_progress = 0.0
        self.color = {
            "schueler":    (100, 180, 255),
            "student":     (150, 230, 150),
            "bueroangest": (200, 170, 100),
            "handwerker":  (180, 120, 80),
            "familie":     (230, 150, 200),
            "tourist":     (255, 200, 80),
            "stammkunde":  (255, 230, 100),
        }[self.ctype]

    def tick(self, dt: float):
        self.patience -= dt
        self.wait_time += dt
        if self.patience <= 0 and not self.satisfied:
            self.left = True

    def calc_satisfaction(self, price: float, quality: float, sauce_match: bool, wait: float) -> float:
        base = quality * 0.6
        if self.budget >= price:
            base += 0.2
        else:
            # Proportionale Strafe: je weiter über Budget, desto mehr Abzug
            # Aber hohe Qualität federt das ab
            over_budget = (price - self.budget) / max(price, 1.0)
            base -= over_budget * 0.4 * (1.0 - quality * 0.5)
        if sauce_match:
            base += 0.2
        wait_penalty = max(0, (wait - 60) / 120)
        base -= wait_penalty
        return max(0.0, min(1.0, base))

    def type_label(self) -> str:
        return {
            "schueler": "Schüler", "student": "Student",
            "bueroangest": "Büroangestellter", "handwerker": "Handwerker",
            "familie": "Familie", "tourist": "Tourist", "stammkunde": "Stammkunde"
        }.get(self.ctype, self.ctype)


# ─────────────────────────────────────────────
#  STAFF MEMBER
# ─────────────────────────────────────────────
class StaffMember:
    TYPES = ["doenemrister", "kassengenie", "sauce_guru", "azubi", "filialleiter", "reiniger"]
    NAMES_M = ["Mehmet", "Cem", "Murat", "Hasan", "Ibrahim", "Yusuf", "Ali", "Kemal", "Tariq", "Ömer"]
    NAMES_F = ["Fatima", "Ayse", "Zeynep", "Leyla", "Nadia", "Sara", "Derya", "Melek"]
    SURNAMES = ["Yilmaz", "Kaya", "Demir", "Sahin", "Celik", "Ozturk", "Aksoy", "Polat"]

    def __init__(self, stype: str = None, level: int = 1):
        self.stype = stype or random.choice(self.TYPES)
        self.level = level
        self.name = f"{random.choice(self.NAMES_M + self.NAMES_F)} {random.choice(self.SURNAMES)}"

        base_skill = level * 1.5
        cfg = {
            "doenemrister": {"speed": 7, "friendliness": 5, "exp": 8, "reliability": 7, "salary": 1800},
            "kassengenie":  {"speed": 6, "friendliness": 8, "exp": 5, "reliability": 8, "salary": 1600},
            "sauce_guru":   {"speed": 5, "friendliness": 7, "exp": 6, "reliability": 6, "salary": 1700},
            "azubi":        {"speed": 3, "friendliness": 6, "exp": 2, "reliability": 5, "salary": 600},
            "filialleiter": {"speed": 5, "friendliness": 7, "exp": 7, "reliability": 9, "salary": 2800},
            "reiniger":     {"speed": 4, "friendliness": 5, "exp": 3, "reliability": 8, "salary": 700},
        }[self.stype]

        self.speed = min(10, cfg["speed"] + random.randint(-1, 2) + int(base_skill * 0.3))
        self.friendliness = min(10, cfg["friendliness"] + random.randint(-1, 2))
        self.experience = min(10, cfg["exp"] + random.randint(-1, 2) + int(base_skill * 0.2))
        self.reliability = min(10, cfg["reliability"] + random.randint(-2, 1))
        self.salary = cfg["salary"] * (1 + (level - 1) * 0.15)
        self.morale = random.uniform(0.6, 1.0)
        self.is_working = True
        self.efficiency = self._calc_efficiency()

    def _calc_efficiency(self) -> float:
        # /25 so a good worker gives ~0.7, team of 2 gets >1.0
        return (self.speed + self.experience + self.reliability) / 25.0 * self.morale

    def type_label(self) -> str:
        return {
            "doenemrister": "Dönermeister", "kassengenie": "Kassengenie",
            "sauce_guru": "Sauce-Guru", "azubi": "Azubi", "filialleiter": "Filialleiter",
            "reiniger": "Reinigungskraft"
        }.get(self.stype, self.stype)

    def monthly_cost(self) -> float:
        return self.salary

    def tick_morale(self, morale_mod: float = 1.0):
        # Morale drifts slightly
        change = random.uniform(-0.01 * morale_mod, 0.005)
        self.morale = max(0.2, min(1.0, self.morale + change))
        self.efficiency = self._calc_efficiency()

    def to_dict(self) -> dict:
        return {
            "stype": self.stype, "level": self.level, "name": self.name,
            "speed": self.speed, "friendliness": self.friendliness,
            "experience": self.experience, "reliability": self.reliability,
            "salary": self.salary, "morale": self.morale
        }

    @classmethod
    def from_dict(cls, d: dict) -> "StaffMember":
        s = cls(d["stype"], d["level"])
        s.name = d["name"]
        s.speed = d["speed"]
        s.friendliness = d["friendliness"]
        s.experience = d["experience"]
        s.reliability = d["reliability"]
        s.salary = d["salary"]
        s.morale = d["morale"]
        s.efficiency = s._calc_efficiency()
        return s


# ─────────────────────────────────────────────
#  DÖNER RECIPE
# ─────────────────────────────────────────────
@dataclass
class DoenemRecipe:
    name: str = "Classic Döner"
    fleisch: str = "fleisch_basis"
    brot: str = "brot_normal"
    salat: bool = True
    tomate: bool = True
    zwiebel: bool = True
    kraut: bool = True
    gurke: bool = True
    sosse: str = "sosse_knoblauch"
    schaerfe: int = 2          # 0-5
    fleisch_menge: float = 1.0  # multiplier
    price: float = 5.50

    def ingredient_cost(self) -> float:
        cost = INGREDIENT_COSTS.get(self.fleisch, 1.2) * self.fleisch_menge
        cost += INGREDIENT_COSTS.get(self.brot, 0.25)
        if self.salat:  cost += INGREDIENT_COSTS["salat"]
        if self.tomate: cost += INGREDIENT_COSTS["tomate"]
        if self.zwiebel: cost += INGREDIENT_COSTS["zwiebel"]
        if self.kraut:  cost += INGREDIENT_COSTS["kraut"]
        if self.gurke:  cost += INGREDIENT_COSTS["gurke"]
        cost += INGREDIENT_COSTS.get(self.sosse, 0.08)
        return cost

    def quality_score(self) -> float:
        q = 5.0
        if self.fleisch == "fleisch_premium": q += 2.0
        if self.brot == "brot_vollkorn": q += 0.5
        if self.salat: q += 0.3
        if self.tomate: q += 0.3
        if self.gurke: q += 0.2
        q += self.fleisch_menge * 0.5
        return min(10.0, q)

    def profit_margin(self) -> float:
        return self.price - self.ingredient_cost()

    def to_dict(self) -> dict:
        return {
            "name": self.name, "fleisch": self.fleisch, "brot": self.brot,
            "salat": self.salat, "tomate": self.tomate, "zwiebel": self.zwiebel,
            "kraut": self.kraut, "gurke": self.gurke, "sosse": self.sosse,
            "schaerfe": self.schaerfe, "fleisch_menge": self.fleisch_menge, "price": self.price
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DoenemRecipe":
        r = cls()
        for k, v in d.items():
            setattr(r, k, v)
        return r


# ─────────────────────────────────────────────
#  SUPPLIER
# ─────────────────────────────────────────────
@dataclass
class Supplier:
    stype: str       # "fleisch", "brot", "gemuese", "getraenke"
    name: str
    quality: int     # 1-10
    reliability: int # 1-10
    price_mod: float # 1.0 = normal
    contract_days: int = 30
    active: bool = True

    def monthly_cost(self, base_volume: float) -> float:
        return base_volume * self.price_mod

    def to_dict(self) -> dict:
        return {
            "stype": self.stype, "name": self.name, "quality": self.quality,
            "reliability": self.reliability, "price_mod": self.price_mod,
            "contract_days": self.contract_days, "active": self.active
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Supplier":
        return cls(**d)


# ─────────────────────────────────────────────
#  BRANCH (Filiale)
# ─────────────────────────────────────────────
class Branch:
    def __init__(self, name: str, location_type: str, city: str, country: str = "Deutschland"):
        self.name = name
        self.location_type = location_type
        self.city = city
        self.country = country
        cfg = LOCATION_TYPES.get(location_type, LOCATION_TYPES["kleinststadt"])
        self.rent = cfg["rent"]
        self.base_foot_traffic = cfg["foot_traffic"]

        # State
        self.money = 0.0
        self.hygiene = 80.0        # 0-100
        self.reputation = 50.0     # 0-100
        self.open_hour = 10
        self.close_hour = 22
        self.is_open = True
        self.is_franchise = False

        # Recipes (menu)
        self.recipes: list[DoenemRecipe] = [DoenemRecipe()]

        # Staff
        self.staff: list[StaffMember] = []

        # Suppliers
        self.suppliers: dict[str, Supplier] = {}

        # Upgrades purchased
        self.upgrades: set[str] = set()

        # Marketing active
        self.marketing: dict[str, bool] = {
            "flyer": False, "social_media": False, "influencer": False,
            "stadion": False, "tv": False
        }

        # Daily stats
        self.daily_customers = 0
        self.daily_revenue = 0.0
        self.daily_expenses = 0.0
        self.total_customers = 0
        self.total_revenue = 0.0

        # Sauce popularity
        self.sauce_popularity: dict[str, int] = {k: 0 for k in SAUCE_NAMES}

        # Active events
        self.active_events: list[dict] = []

        # Seating capacity
        self.capacity = 15
        self.current_customers: list[Customer] = []

        # Opening age in days
        self.age_days = 0

    @property
    def staff_efficiency(self) -> float:
        if not self.staff:
            return 0.3
        return min(2.5, sum(s.efficiency for s in self.staff))

    @property
    def marketing_multiplier(self) -> float:
        mult = 1.0
        if self.marketing.get("flyer"): mult += 0.1
        if self.marketing.get("social_media"): mult += 0.2
        if self.marketing.get("influencer"): mult += 0.35
        if self.marketing.get("stadion"): mult += 0.5
        if self.marketing.get("tv"): mult += 0.8
        return mult

    @property
    def event_multiplier(self) -> float:
        mult = 1.0
        for ev in self.active_events:
            if "daily_customers" in ev.get("effect", {}):
                mult *= ev["effect"]["daily_customers"]
            if "capacity_mod" in ev.get("effect", {}):
                mult *= ev["effect"]["capacity_mod"]
        return mult

    def get_hourly_customers(self, hour: int) -> int:
        base = self.base_foot_traffic / 12.0
        # Peak hours boost
        if hour in [12, 13]: base *= 2.5
        elif hour in [11, 18, 19]: base *= 1.5
        elif hour in [10, 14, 17, 20]: base *= 1.0
        elif hour < 10 or hour > 21: base *= 0.1
        else: base *= 0.6

        base *= self.marketing_multiplier
        base *= self.event_multiplier
        base *= (0.5 + self.reputation / 100.0)
        base *= self.staff_efficiency

        if "hygiene" in self.upgrades: base *= 1.1
        return max(0, int(base + random.uniform(-base * 0.2, base * 0.2)))

    def hire_staff(self, stype: str, level: int = 1) -> StaffMember:
        s = StaffMember(stype, level)
        self.staff.append(s)
        return s

    def fire_staff(self, idx: int):
        if 0 <= idx < len(self.staff):
            self.staff.pop(idx)

    def add_recipe(self, recipe: DoenemRecipe):
        self.recipes.append(recipe)

    def monthly_fixed_costs(self) -> float:
        costs = self.rent
        for s in self.staff:
            costs += s.monthly_cost()
        mktg_costs = {
            "flyer": 200, "social_media": 500, "influencer": 2000,
            "stadion": 5000, "tv": 15000
        }
        for k, v in self.marketing.items():
            if v:
                costs += mktg_costs.get(k, 0)
        return costs

    def tick_day(self, hygiene_mod: float = 1.0, morale_mod: float = 1.0):
        self.age_days += 1
        # Hygiene degrades
        self.hygiene = max(0, self.hygiene - random.uniform(0.5, 2.0) * hygiene_mod)
        # Reiniger hält Hygiene auf mindestens 80%
        has_reiniger = any(s.stype == "reiniger" for s in self.staff)
        if has_reiniger and self.hygiene < 80.0:
            self.hygiene = 80.0
        # Reputation only changes through customer satisfaction and events, not time
        # Staff morale tick
        for s in self.staff:
            s.tick_morale(morale_mod)
        # Tick event durations
        for ev in self.active_events[:]:
            ev["remaining"] = ev.get("remaining", ev.get("duration", 1)) - 1
            if ev["remaining"] <= 0:
                self.active_events.remove(ev)
        # Reset daily counters
        self.daily_customers = 0
        self.daily_revenue = 0.0
        self.daily_expenses = 0.0

    def to_dict(self) -> dict:
        return {
            "name": self.name, "location_type": self.location_type,
            "city": self.city, "country": self.country,
            "rent": self.rent, "hygiene": self.hygiene,
            "reputation": self.reputation, "open_hour": self.open_hour,
            "close_hour": self.close_hour, "is_open": self.is_open,
            "is_franchise": self.is_franchise,
            "recipes": [r.to_dict() for r in self.recipes],
            "staff": [s.to_dict() for s in self.staff],
            "suppliers": {k: v.to_dict() for k, v in self.suppliers.items()},
            "upgrades": list(self.upgrades),
            "marketing": self.marketing,
            "total_customers": self.total_customers,
            "total_revenue": self.total_revenue,
            "sauce_popularity": self.sauce_popularity,
            "active_events": self.active_events,
            "capacity": self.capacity,
            "age_days": self.age_days,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Branch":
        b = cls(d["name"], d["location_type"], d["city"], d.get("country", "Deutschland"))
        b.rent = d["rent"]
        b.hygiene = d["hygiene"]
        b.reputation = d["reputation"]
        b.open_hour = d["open_hour"]
        b.close_hour = d["close_hour"]
        b.is_open = d["is_open"]
        b.is_franchise = d.get("is_franchise", False)
        b.recipes = [DoenemRecipe.from_dict(r) for r in d["recipes"]]
        b.staff = [StaffMember.from_dict(s) for s in d["staff"]]
        b.suppliers = {k: Supplier.from_dict(v) for k, v in d.get("suppliers", {}).items()}
        b.upgrades = set(d.get("upgrades", []))
        b.marketing = d.get("marketing", {k: False for k in ["flyer","social_media","influencer","stadion","tv"]})
        b.total_customers = d.get("total_customers", 0)
        b.total_revenue = d.get("total_revenue", 0.0)
        b.sauce_popularity = d.get("sauce_popularity", {k: 0 for k in SAUCE_NAMES})
        b.active_events = d.get("active_events", [])
        b.capacity = d.get("capacity", 15)
        b.age_days = d.get("age_days", 0)
        return b


# ─────────────────────────────────────────────
#  RESEARCH NODE
# ─────────────────────────────────────────────
@dataclass
class ResearchNode:
    node_id: str
    name: str
    desc: str
    cost: float
    duration_days: int
    requires: list[str] = field(default_factory=list)
    unlocked: bool = False
    researching: bool = False
    progress: float = 0.0
    effect: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id, "name": self.name, "desc": self.desc,
            "cost": self.cost, "duration_days": self.duration_days,
            "requires": self.requires, "unlocked": self.unlocked,
            "researching": self.researching, "progress": self.progress,
            "effect": self.effect
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ResearchNode":
        return cls(**d)


# ─────────────────────────────────────────────
#  COMPETITOR
# ─────────────────────────────────────────────
class Competitor:
    def __init__(self, cfg: dict, city: str):
        self.name = cfg["name"]
        self.quality = cfg["quality"]
        self.price_mod = cfg["price_mod"]
        self.color = cfg["color"]
        self.city = city
        self.market_share = random.uniform(0.05, 0.20)
        self.reputation = random.uniform(40, 80)
        self.age_days = 0

    def tick_day(self, aggression: float = 1.0):
        self.age_days += 1
        # Slight random drift in market share
        self.market_share = max(0.01, min(0.8, self.market_share + random.uniform(-0.002, 0.002 * aggression)))

    def to_dict(self) -> dict:
        return {
            "name": self.name, "quality": self.quality, "price_mod": self.price_mod,
            "city": self.city, "market_share": self.market_share,
            "reputation": self.reputation, "age_days": self.age_days
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Competitor":
        cfg = {"name": d["name"], "quality": d["quality"],
               "price_mod": d["price_mod"], "color": C_RED}
        c = cls(cfg, d["city"])
        c.market_share = d["market_share"]
        c.reputation = d["reputation"]
        c.age_days = d["age_days"]
        return c