# Designkonzept: Winklmeier Office 2026

## Kurzfassung

Die bisherige UI-Richtung wird verworfen. Sie wirkte trotz Verbesserungen weiterhin wie ein Prototyp mit nachtraeglich aufgetragenem Theme: zu viele Boxen, zu harte Kontraste, zu viel Rot/Schwarz, zu wenig ruhige Arbeitsfuehrung.

Das neue Zielbild heisst **Winklmeier Office**: eine ruhige, helle Desktop-App im Stil einer guten macOS-/Apple-Produktivsoftware, kombiniert mit den Prozessmustern aus Lexware und SAP Fiori.

Die App soll nicht nach Dashboard aussehen. Sie soll sich anfuehlen wie ein aufgeraeumtes Buero-Werkzeug: links Orientierung, oben Suche und Hauptaktion, in der Mitte die Arbeitsliste, rechts Kontext und naechster Schritt.

## Designziele

1. **Einfacher als Excel, nicht bunter als Excel.**
   Nutzer sollen schnell erkennen, wo sie klicken muessen. Die Oberflaeche darf modern aussehen, aber sie darf nie lauter sein als die Aufgabe.

2. **Apple-like Ruhe.**
   Viel Weissraum, helle Flaechen, dezente Trennlinien, klare Typografie, wenige Akzentfarben, keine schweren schwarzen Bloecke.

3. **Lexware-like Aufgabenlogik.**
   Nicht nach Datenbanktabellen navigieren, sondern nach Alltagsaufgaben: Kunde suchen, Bestellung schreiben, Rechnung erzeugen, Zahlung pruefen.

4. **SAP-Fiori-like Objektarbeit.**
   Listen fuehren zu Details. Eine ausgewaehlte Sache hat Kontext, Status, Aktionen und naechsten Schritt. Keine Seite soll alles gleichzeitig gleich wichtig zeigen.

5. **60+ tauglich.**
   Grosse Ziele, klare Sprache, kein verstecktes Hover-Wissen, kein horizontaler Scroll, keine gequetschten Detailbereiche.

## Recherchegrundlage

- Apple UI Design Dos and Don'ts: primaerer Inhalt ohne horizontales Scrollen, Controls nahe am Inhalt, klare Ausrichtung, mindestens 44pt grosse Ziele, lesbarer Text und ausreichend Kontrast.
- SAP Fiori: modulare, konsistente Enterprise-Komponenten; starke Muster fuer List Report, Object Page und Flexible Column Layout.
- Lexware: Aufgabenversprechen statt Funktionswand; Rechnungen, Belege, Banking und Ueberblick werden als alltagsnahe Arbeit formuliert.

## Nicht mehr machen

- Keine schwarzen Navigationsbloecke.
- Keine roten Vollflaechen als Standard.
- Keine Kachelwand auf der Startseite.
- Keine gequetschten Split-Screens mit Formular rechts und Tabelle links, wenn der Platz nicht reicht.
- Keine nummerierte Navigation als optisches Gimmick.
- Keine Begriffe wie "Cockpit", "Pruefstand" oder "Belegwerkstatt" als sichtbare UI-Sprache, wenn sie nach Konzeptfolie statt Alltag klingen.
- Keine zu technische Hauptnavigation wie "Offene Posten" als alleiniger Begriff, wenn "Kasse" oder "Zahlungen" verstaendlicher ist.

## Neues Informationsmodell

Die App wird in fuenf Hauptbereiche gegliedert:

1. **Heute**
   Tagesueberblick, faellige Arbeit, offene Aufgaben.

2. **Kunden**
   Kunde suchen, Kundenakte oeffnen, letzte Mengen sehen, Bestellung starten.

3. **Bestellungen**
   Bestellung erfassen, Positionen pruefen, Lieferschein/Rechnung vorbereiten.

4. **Rechnungen**
   Rechnung/Lieferschein erstellen, Excel/PDF oeffnen, offene Zahlungen sehen.

5. **Stammdaten**
   Kunden, Artikel, Import und Pruefpunkte. Das ist Verwaltung, nicht Tagesarbeit.

Optional unten in der Sidebar: **Einstellungen** als kleiner Eintrag, nicht als gleich wichtiger Hauptbereich.

## Shell-Layout

Die App bekommt eine klassische Apple-like Arbeitsstruktur:

```text
+--------------------------------------------------------------------------------+
| Toolbar:  Suche...                         + Neu   Aktualisieren   Hilfe       |
+----------------------+-----------------------------+---------------------------+
| Sidebar              | Content                     | Inspector                 |
|                      |                             |                           |
| Heute                | Seitentitel                 | Kontext                   |
| Kunden               | Segment / Filter            | Status                    |
| Bestellungen         | Liste oder Formular         | Naechste Schritte         |
| Rechnungen           |                             | Hinweise                  |
| Stammdaten           |                             |                           |
|                      |                             |                           |
| Einstellungen        |                             |                           |
+----------------------+-----------------------------+---------------------------+
```

### Sidebar

- Breite ca. 220 px.
- Heller Hintergrund, keine harte schwarze Auswahl.
- Aktiver Eintrag: dezente helle Flaeche mit roter linker Linie oder kleinem rotem Punkt.
- Icons optional, aber sparsam: Haus, Person, Liste, Beleg, Tabelle.
- Keine Nummern.

### Toolbar

- Oben eine schmale Werkzeugleiste.
- Links globale Suche: "Kunde, Rechnung oder Artikel suchen".
- Rechts wenige Aktionen: "Neu", "Aktualisieren", Hilfe.
- Winklmeier-Logo klein links oben oder im Fenstertitelbereich, nicht als dominante Bannerflaeche.

### Content

- Pro Hauptbereich eine klare Hauptliste oder ein klarer Arbeitsprozess.
- Keine Kachelwand.
- Tabellen sind ruhig, hell und gut lesbar.
- Status wird als Badge gezeigt: Offen, Faellig, Bezahlt, Pruefen.

### Inspector

- Rechte Kontextspalte, wenn ein Kunde, eine Bestellung oder Rechnung ausgewaehlt ist.
- Zeigt nur das, was jetzt hilft:
  - Kundendaten
  - Lieferhinweise
  - offene Rechnungen
  - letzte Bestellung
  - naechster sinnvoller Button
- Wenn nichts ausgewaehlt ist, zeigt er eine freundliche Leerseite mit Beispiel: "Kunde auswaehlen, um Details zu sehen."

## Hauptbereiche als Wireframes

### 1. Heute

```text
Heute
------------------------------------------------------------
Aufgaben fuer heute

[ ] 3 Kunden beliefern                 Button: Route oeffnen
[ ] 2 offene Rechnungen pruefen        Button: Kasse oeffnen
[ ] 4 Pruefpunkte klaeren              Button: Pruefen

------------------------------------------------------------
Naechste Lieferungen
Kunde             Zeit       Hinweis                 Aktion
Metzgerei Karl    bis 13     SEPA                    Oeffnen
Cafe Nord         nachm.     Leergut pruefen          Oeffnen
```

Prinzip: Startseite ist eine Aufgabenliste, keine Grafikseite. Sie beantwortet: "Was muss heute getan werden?"

### 2. Kunden

```text
Kunden
------------------------------------------------------------
Suche: [ Cafe, Metzgerei, Kundennummer ... ]

Kundenliste
Name              Ort/Adresse             Status       Letzte Bestellung
Metzgerei Karl    ...                     aktiv        24.06.2026
Cafe Nord         ...                     aktiv        21.06.2026

                                                   Inspector
                                                   ---------------------
                                                   Metzgerei Karl
                                                   Adresse
                                                   Lieferhinweise
                                                   Offene Rechnung: nein

                                                   [Bestellung starten]
                                                   [Ordner oeffnen]
```

Prinzip: Erst Liste, dann Detail. Der Nutzer sucht den Kunden und sieht rechts sofort, was wichtig ist.

### 3. Bestellungen

```text
Bestellungen
------------------------------------------------------------
Segment: [Aktuell] [Archiv]

Bestellliste
Nr.        Kunde             Lieferdatum     Status       Betrag
B-1021     Metzgerei Karl    Heute           Entwurf      186,38

                                                   Inspector
                                                   ---------------------
                                                   Bestellung B-1021
                                                   12 Positionen
                                                   Pfand Rueckgabe: ja
                                                   Summe: 186,38 EUR

                                                   [Weiter bearbeiten]
                                                   [Lieferschein erstellen]
```

Bestellung erfassen:

```text
Neue Bestellung
------------------------------------------------------------
Kunde: Metzgerei Karl                       Lieferdatum: Heute

Letzte Mengen                              Neue Bestellung
Artikel                 Letzte Menge        Menge       Preis
Frucade Colamix         3                   [ 3 ]       10,48
Wasser still            2                   [ 2 ]        8,90

Pfand Rueckgabe
[+ Pfand hinzufuegen]

                                           Summe: 186,38 EUR
                                           [Speichern]
                                           [Speichern und Lieferschein]
```

Prinzip: Links Vorlage, rechts aktuelle Bestellung. Nicht alles als technische Tabelle, sondern als klarer Erfassungsprozess.

### 4. Rechnungen

```text
Rechnungen
------------------------------------------------------------
Filter: [Offen] [Faellig] [Bezahlt] [Alle]

Rechnungsliste
Nr.        Kunde             Datum       Faellig     Status    Betrag
RE-1021    Metzgerei Karl    24.06.26    01.07.26    Offen     186,38

                                                   Inspector
                                                   ---------------------
                                                   Rechnung RE-1021
                                                   Zahlart: SEPA
                                                   Faellig: 01.07.2026
                                                   Dateien vorhanden

                                                   [PDF oeffnen]
                                                   [Excel oeffnen]
                                                   [Als bezahlt markieren]
```

Prinzip: Rechnungen sind kein Exportdialog, sondern ein Zahlungs- und Dokumentenbereich.

### 5. Stammdaten

```text
Stammdaten
------------------------------------------------------------
Segment: [Kunden] [Artikel] [Import] [Pruefpunkte]

Kunden / Artikel als Listenansicht

Bei Auswahl:
Detailformular erscheint rechts im Inspector oder in einem Bearbeiten-Dialog.
```

Prinzip: Stammdaten sind Verwaltung. Sie duerfen weniger prominent sein als Tagesarbeit.

## Visuelle Richtung

### Palette

- Hintergrund: `#F5F5F7` macOS-hellgrau.
- Flaeche: `#FFFFFF`.
- Primaertext: `#1D1D1F`.
- Sekundaertext: `#6E6E73`.
- Linie: `#D2D2D7`.
- Winklmeier-Rot: `#C4312F`, nur fuer Akzent, Badge, Warnung oder aktiven Fokus.
- Erfolgsgruen: `#2E7D32`, nur fuer bezahlt/ok.
- Hinweisblau: `#0A84FF`, optional fuer primaere Apple-like Aktionen.

### Typografie

- Systemschrift: Segoe UI auf Windows, San Francisco-artige Anmutung durch klare Groessen.
- Titel 24-28 px, nicht 30+.
- Tabellen/Forms 14-15 px.
- Keine extrem fetten Headlines.
- Weniger Versalien.

### Komponenten

- Sidebar item: flach, hell, 36-44 px hoch.
- Toolbar button: klein, ruhig, optional mit Icon.
- Primary button: nur eine pro Arbeitsbereich.
- Secondary button: neutral.
- Badges: klein, farbig, abgerundet.
- Tables: helle Header, dezente Linien, gut lesbare Auswahl.
- Inspector: rechte helle Seitenleiste mit klaren Gruppen.

## Bedienregeln

1. Pro Seite genau eine primaere Aktion.
2. Alles, was die Auswahl betrifft, steht nah an der Auswahl oder im Inspector.
3. Keine Aktion darf nur ueber Rechtsklick erreichbar sein.
4. Rechtsklick ist Bonus fuer geuebte Nutzer, nicht Hauptweg.
5. Jede Liste hat Suche und Filter oben.
6. Jeder leere Zustand sagt, was als Naechstes zu tun ist.
7. Keine Seite braucht horizontales Scrollen.
8. Dialoge nur fuer kleine Entscheidungen; groessere Arbeit bleibt im Hauptfenster.
9. Speichern erzeugt klare Rueckmeldung und bietet den naechsten Schritt an.
10. Fehlertexte sagen, was fehlt und wie man es behebt.

## Umsetzungsstrategie

### Phase 1: Shell neu bauen

- Header-Banner entfernen.
- Dezente Toolbar einfuehren.
- Sidebar optisch auf Apple-like hell umstellen.
- Navigation auf `Heute`, `Kunden`, `Bestellungen`, `Rechnungen`, `Stammdaten` umbauen.
- Inspector-Grundkomponente einfuehren.

### Phase 2: Heute und Kunden

- Startseite als Aufgabenliste bauen.
- Kundenbereich als Liste + Inspector bauen.
- Kundenordner-Aktionen in den Inspector verschieben.
- Suchkomponente kompakt halten.

### Phase 3: Bestellungen

- Bestellliste und Bestelldetail trennen.
- Neue Bestellung als gefuehrten Editor bauen: Kunde, letzte Mengen, aktuelle Mengen, Summe, naechster Schritt.

### Phase 4: Rechnungen/Kasse

- Rechnungsliste mit Statusfiltern.
- Rechnung/Dateien/Zahlung im Inspector.
- Excel/PDF-Erzeugung als Aktion an einer Bestellung oder Rechnung, nicht als separater schwerer Bereich.

### Phase 5: Stammdaten und Pruefung

- Kunden/Artikel/Import/Pruefpunkte als Segmente.
- Bearbeitung im Inspector oder in ruhigem Detaildialog.

## Akzeptanzkriterien

- Die App wirkt hell, ruhig und modern, nicht wie ein Admin-Template.
- Winklmeier ist sichtbar, aber nicht als schwerer Banner.
- Ein neuer Nutzer kann auf der Startseite erkennen, was heute zu tun ist.
- Ein Kunde kann gesucht und weiterbearbeitet werden, ohne die Seite zu wechseln.
- Eine Bestellung kann aus letzten Mengen gestartet werden, ohne Formularchaos.
- Rechnungen und offene Zahlungen sind in einem klaren Bereich.
- Keine Hauptseite zeigt horizontalen Scroll.
- Mindestens 44 px Zielhoehe fuer wichtige Controls.
- Tests bleiben gruen.

## Entscheidung

Empfohlen wird diese Richtung: **Apple-like Office Shell mit SAP-Fiori Objektarbeit und Lexware Aufgabenlogik.**

Die vorherige Betriebs-Cockpit-Richtung bleibt als verworfener Zwischenstand dokumentiert, soll aber nicht weitergebaut werden.
