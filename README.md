# DÖNERIMPERIUM™

## Starten
```
pip install pygame-ce
python3 main.py
```

## Projektstruktur
```
doeneumperium/
├── main.py           – Spielschleife & Einstiegspunkt
├── constants.py      – Alle Konstanten, Farben, Balancing
├── entities.py       – Spielobjekte: Branch, Customer, Staff, Recipe, Supplier, Competitor
├── gamestate.py      – Spielzustand, Simulation, Save/Load
├── ui_components.py  – Wiederverwendbare UI-Elemente
├── screens.py        – Alle Spielbildschirme
├── saves/            – Gespeicherte Spielstände (JSON)
└── README.md
```

## Steuerung
- **Maus** – Alles klickbar
- **⏸/1x/2x/3x** – Spielgeschwindigkeit (oben rechts)
- **Navigation** – Tabs oben in der Leiste

## Spielziel
- 500 Filialen eröffnen
- 1 Milliarde € Umsatz erreichen
- Marktführer werden (>40% Marktanteil)
- Europaweit expandieren (20+ Länder)
