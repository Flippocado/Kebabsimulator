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

📖 Spieler-Guide: DÖNERIMPERIUM™
Einstieg
Du startest mit einer einzigen Filiale in Dönerhausen — einer Kleinstadt mit wenig Kundschaft, aber niedrigen Kosten. Ziel ist es, ein weltweites Döner-Imperium aufzubauen, die Konkurrenz zu verdrängen und möglichst viele Siegbedingungen zu erfüllen.
Beim ersten Start wählst du einen Firmennamen und eine Schwierigkeit:
SchwierigkeitWas sich ändertEinfachAlte Standardwerte — Kunden nachsichtig, Hygiene hält lang, Events seltenNormalEtwas anspruchsvoller — Hygiene verfällt schneller, Konkurrenz aktiverSchwerKunden sehr anspruchsvoll, Hygiene verfällt doppelt so schnell, Konkurrenz aggressiv

Die Oberfläche
Oben rechts im HUD findest du:

Spielgeschwindigkeit (1x / 3x / 8x) und Pause
Achievements-Button — öffnet deine Achievement-Übersicht
Aktuelles Geld, Tag und Uhrzeit

Die Navigation läuft über die Tabs oben: Übersicht, Filialen, Forschung, Statistiken, Finanzen, Optionen

Standorte & Mieten
Beim Eröffnen einer neuen Filiale wählst du Standorttyp, Stadt und Land frei. Die Standorttypen unterscheiden sich in Kundenfrequenz und Miete:
TypMiete/TagKunden-FrequenzFreischaltung abKleinstadt800 €NiedrigSofortGroßstadt2.500 €Mittel3 FilialenBahnhof3.500 €Hoch5 FilialenEinkaufszentrum4.500 €Sehr hoch8 FilialenFlughafen8.000 €Maximal15 Filialen
Tipp: Flughäfen bringen die meisten Kunden, sind aber teuer. Starte mit Kleinstädten und Großstädten, dann upgrade auf Flughäfen.

Personal
Jede Filiale braucht Mitarbeiter. Es gibt drei Typen:

Dönermeister — Hauptproduktion, hoher Einfluss auf Kundendurchsatz
Azubi — Günstig, aber langsamer und weniger erfahren
Reiniger — Hält die Hygiene oben; ohne Reiniger fällt Hygiene schnell

Mitarbeiter haben Moral — sinkt die Moral, sinkt die Effizienz. Hohe Moral = bessere Leistung. Moral kann durch schlechtes Management sinken.
Tipp: Jede Filiale sollte mindestens einen Reiniger haben, sonst fällt die Hygiene auf 0 — und das Gesundheitsamt freut sich.

Rezepte & Preise
Du kannst pro Filiale mehrere Rezepte anlegen. Jedes Rezept hat:

Fleischsorte (Standard / Premium)
Brot (Normal / Vollkorn)
Zutaten (Salat, Tomate, Zwiebel, Kraut, Gurke)
Soße (Knoblauch, Scharf, Kräuterquark, Joghurt, Tomate)
Preis

Der Preis beeinflusst direkt wie viele Kunden kaufen. Zu teuer = weniger Kunden, zu günstig = weniger Gewinn. Das Sweet-Spot liegt meist zwischen 7–10 €.

Lieferanten
Jede Filiale hat Lieferanten für Fleisch, Brot, Gemüse und Getränke. Bessere Lieferanten haben höhere Qualität und Zuverlässigkeit — was direkt die Kundenzufriedenheit beeinflusst. Lieferanten-Verträge laufen nach einer bestimmten Anzahl Tage aus und müssen erneuert werden.

Hygiene & Reputation

Hygiene sinkt täglich automatisch — Reiniger verlangsamen das
Fällt Hygiene unter 50, drohen negative Events (Lebensmittelkontrolle!)
Reputation steigt wenn Kunden zufrieden sind, sinkt bei schlechtem Service
Reputation 100 = maximale Kundenbindung


Forschung
Im Forschungsbaum schaltest du dauerhaft Verbesserungen frei:

Automatischer Döner-Schneider → Produktionsgeschwindigkeit +30%
KI-Kassensystem → Kundendurchsatz +25%
Mega-Drehspieß 3000 → Kapazität verdoppelt
Franchise-System → Ermöglicht Franchise-Filialen (passives Einkommen)
Eigene Brotfabrik → Brotkosten -60%
Eigene Fleischproduktion → Fleischkosten -50%, Qualität +1
Döner-Loyalty-App → Stammkunden +40%
Geheimes Familienrezept → Massiver Qualitäts- und Reputationsboost

Tipp: Priorität: Schnittmaschine → KI-Kasse → Loyalty-App → Franchise

Marketing
Pro Filiale buchbar, kostet täglich:
OptionKosten/TagEffektFlyer200 €+10% KundenSocial Media500 €ReichweiteInfluencer2.000 €Großer BoostStadionwerbung5.000 €MassivTV-Werbung15.000 €Maximum

Zufalls-Events
Regelmäßig passieren Events in deinen Filialen:
EventEffektTikTok viral+50% Kunden, Reputation +15 (7 Tage)LebensmittelkontrolleHygiene-Strafe bei schlechter HygieneFußball-AnsturmMassenhaft Kunden nach dem SpielStromausfallTemporäre SchließungTomaten-KnappheitLieferproblemeGute BewertungReputation +10Promi-BesuchReputation +20, Kunden +40% (7 Tage)
Bei Schwer sind negative Events fast doppelt so häufig.

Marktanteil
Dein Marktanteil wird täglich basierend auf deinen Kunden im Vergleich zur Konkurrenz berechnet. Mit mehr Filialen und Marketing steigt er. Über 40% Marktanteil ist eine der Siegbedingungen.
Die Konkurrenz wächst automatisch mit — alle 60 Tage können neue Konkurrenten in deinen Städten auftauchen.

Siegbedingungen
Das Spiel endet nicht — aber du kannst folgende Ziele erreichen:
ZielBedingung500 FilialenDöner-Weltkonzern1 Milliarde € UmsatzLegendärer Status>40% MarktanteilMarktführer20+ LänderEuropäische Expansion

Achievements
Es gibt 64 Achievements — von ernst bis komplett absurd. Einmal freigeschaltet bleiben sie permanent (außer "Banker hasst ihn", das sich täglich aktualisiert). Du siehst deinen Fortschritt im Achievements-Screen oben rechts.
Viel Erfolg beim Döner-Imperium! 🥙