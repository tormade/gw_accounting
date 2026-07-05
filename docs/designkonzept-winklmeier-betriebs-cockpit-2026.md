# Designkonzept: Winklmeier Betriebs-Cockpit 2026

## Ziel

Die App soll wie eine eigenstaendige Arbeitssoftware fuer Getraenke Winklmeier wirken, nicht wie ein generisches KI-Dashboard. Sie bleibt dicht, schnell und desktop-tauglich, bekommt aber eine klare Marken- und Arbeitslogik: Lieferservice, Tour, Kasse, Beleg, Pruefstand und Stammdaten.

Nach dem ersten Designwurf wurde klar: reine Theme-Politur reicht nicht. Der radikale Zielzustand ist eine vereinfachte Arbeitsstationen-App mit wenigen Hauptwegen und weniger gleichfoermigen Boxen.

## Recherche- und Markenbasis

- Die Winklmeier-Homepage setzt stark auf Weiss, Schwarz und Rot, das Logo, den Claim "Wir bringen's einfach", den Lieferservice und die regionale Bestandswirkung.
- WCAG 2.2 empfiehlt als aktuelle Referenz sichtbaren Fokus, ausreichende Bedienziele, verstaendliche Labels, konsistente Navigation und robuste Statusmeldungen.
- 2026-UX-Trend fuer Arbeitssoftware: weniger austauschbare Card-Dashboards, mehr kontextbezogene Oberflaechen, klare Human-in-the-loop-Kontrollen, hohe Lesbarkeit und spezifische Markenidentitaet.
- Fuer Nutzer 60+ zaehlen nicht Effekte, sondern Orientierung, grosse Klickziele, wenig versteckte Bedienung, klare Sprache und erkennbare Konsequenzen.
- Referenzmuster aus sevdesk, Lexware und orgaMAX: Modulnavigation, statusstarke Tabellen, Aufgabenlisten, klare Hauptaktion, Beleg-/Rechnungsstatus statt dekorativer Kacheln.

## Gestaltungsprinzip

**Betriebs-Cockpit statt SaaS-Karte.**

Jede Hauptflaeche bekommt eine erkennbare Arbeitsrolle:

- Start: gefuehrtes Ablaufbrett fuer Kunden finden, Bestellung/Beleg, Kasse und Pruefung.
- Kundenarbeit: Kundenakte, Ablage und naechster Schritt.
- Kasse & Listen: offene Posten, Tour und Wiedervorlage.
- Stammdaten: Kundenkarte, Kundenstamm, Preiskarte, Artikelstamm.
- Pruefen: Pruefstand fuer Konflikte.
- Setup: Importstand.
- Belege: Belegwerkstatt mit klaren Schritten.

## Visuelle Regeln

- Keine grossen generischen Rounded Cards. Maximal 8px Radius, klare Kanten, arbeitsnahe Flaechen.
- Rot ist Winklmeier-Marke und Hauptaktion, Schwarz ist Markenanker und Navigation, Gruen ist Status/Fokus/Kasse.
- Seitenkoepfe wirken wie Arbeitszettel: Kicker, Titel, Beschreibung und rote linke Fuehrungslinie.
- Navigation ist nummeriert und stabil, damit Nutzer jederzeit wissen, wo sie sind.
- Die Navigation nutzt Aufgabenwoerter statt technische Begriffe: Start, Kundenarbeit, Kasse & Listen, Stammdaten, Pruefen, Setup.
- Tabellen sind nicht "leise grau", sondern Arbeitslisten mit schwarzem Kopf und roter Linie.
- Buttons haben mindestens 44px Hoehe. Fokusrahmen sind sichtbar.
- Hilfetexte sind konkret und handlungsnah, nicht marketinghaft.
- Horizontaler Seiten-Scroll wird vermieden; Formulare duerfen umbrechen.
- Stammdaten werden vertikal gefuehrt: Bearbeiten oben, Liste darunter. Kein gequetschter Split-Screen.

## UX-Regeln fuer 60+

- Pro Bereich gibt es eine sichtbare Hauptaktion und klare Nebenaktionen.
- Keine rein hover-abhaengige Bedienung.
- Statusmeldungen bleiben unten sichtbar.
- Tabellen behalten klare Zeilen, Tooltips und Auswahlzustaende.
- Dialoge und Belegschritte bleiben kompakt, aber scrollfaehig.
- Suchfelder sagen, was eingegeben werden soll.

## Umsetzung im Code

- `PageHeader`, `ActionCard` und `WorkspaceCard` tragen Kicker und visuelle Tones.
- Tones: `route`, `cash`, `audit`, `document`.
- Die Panels nutzen diese Tones semantisch, ohne Fachlogik in die UI zu ziehen.
- Das Theme ist ein gemeinsames QSS-Designsystem statt Einzelstyling pro Widget.
- Der Startscreen nutzt ein `workflowBoard` mit vier klaren Arbeitsschritten statt generischer Schnellaktionskarten.
- `SearchableSelect` zeigt initial keine leere Trefferbox mehr.

## Akzeptanz

- Die App muss auf den ersten Blick nach Winklmeier wirken: Logo, Claim, Service, Rot/Schwarz/Weiss.
- Keine Oberflaeche darf wie austauschbares KI-Template aussehen.
- Alle Hauptbereiche muessen dieselbe visuelle Sprache sprechen.
- Tests muessen gruene Regression melden.
