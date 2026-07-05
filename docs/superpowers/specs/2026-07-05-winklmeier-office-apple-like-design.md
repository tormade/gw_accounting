# Spec: Winklmeier Office Apple-like Redesign

## Status

Freigegeben fuer Review, noch nicht zur Implementierung freigegeben.

## Ziel

Die bestehende UI-Richtung wird nicht weiterentwickelt. Das neue Zielbild ist in `docs/designkonzept-winklmeier-office-apple-like-2026.md` beschrieben: eine helle, ruhige Apple-like Office-App mit Lexware-Aufgabenlogik und SAP-Fiori-Objektarbeit.

## Umsetzungsidee

- Eine dezente App-Shell ersetzt Banner, Kachelwand und schwere Kontraste.
- Sidebar, Toolbar, Content und Inspector bilden die Grundstruktur.
- Die Hauptnavigation wird auf `Heute`, `Kunden`, `Bestellungen`, `Rechnungen`, `Stammdaten` reduziert.
- Tagesarbeit steht vor Verwaltung.
- Listen fuehren zu Details; Details und naechste Schritte stehen im Inspector.
- Winklmeier-Rot bleibt Akzent, nicht Flaechenfarbe.

## Akzeptanz

- Keine Hauptseite nutzt horizontales Scrollen.
- Keine Startseite besteht aus Dashboard-Kacheln.
- Eine ausgewaehlte Entitaet hat immer Kontext und naechsten Schritt.
- Ein neuer Nutzer versteht den Tagesablauf ohne Schulungstext.
- Die App wirkt hell, ruhig, hochwertig und nicht wie ein Admin-Prototyp.

## Referenzen

- Apple UI Design Dos and Don'ts: https://developer.apple.com/design/tips/
- SAP Fiori Design System: https://www.sap.com/design-system/fiori-design-web
- Lexware Aufgabenlogik: https://www.lexware.de/

## Naechster Schritt

Vor Umsetzung zuerst das Konzeptdokument reviewen. Danach sollte ein Implementierungsplan erstellt werden, der Phase 1 `Shell neu bauen` als separaten Meilenstein behandelt.
