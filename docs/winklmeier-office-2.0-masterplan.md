# Winklmeier Office 2.0: Masterplan fuer den radikalen Umbau

## Entscheidung

Winklmeier Office 2.0 ist kein weiterer Design-Refresh. Die Anwendung wird als durchgehendes Arbeitswerkzeug neu ausgerichtet. Jede Oberflaeche, jeder Button, jede Tabelle und jeder Dialog wird daran gemessen, ob er die echte Arbeitskette schneller, klarer und fehleraermer macht.

Die zentrale Frage lautet nicht mehr: "Welche Funktion gibt es?"  
Die zentrale Frage lautet: "Was muss im Betrieb als Naechstes erledigt werden?"

## Arbeitskette als Produktkern

Die Anwendung wird konsequent auf diese Kette ausgerichtet:

1. Kunde finden oder Tageskunde auswaehlen.
2. Kundenkontext sehen: Adresse, Hinweise, Zahlart, offene Rechnungen, letzte Bestellung.
3. Bestellung aus letzten Mengen oder leer starten.
4. Mengen erfassen, Pfand-Rueckgaben pruefen, Lieferpauschale setzen.
5. Bestellung speichern und Beleg erzeugen.
6. Lieferschein/Rechnung als Excel und PDF erzeugen oder erneut oeffnen.
7. Zahlung/offene Posten verfolgen.
8. Pruefpunkte und Stammdaten nur dann bearbeiten, wenn sie die Arbeit blockieren.

Alles, was diese Kette nicht direkt unterstuetzt, wird aus dem Hauptfluss entfernt oder in Stammdaten/Verwaltung verschoben.

## Produktprinzipien

### 1. Eine Sache im Fokus

Jeder Bereich hat genau eine Hauptaufgabe:

- **Heute**: Was ist jetzt zu tun?
- **Kunden**: Welcher Kunde ist gemeint und was ist der naechste Schritt?
- **Bestellungen**: Welche Bestellung wird gerade bearbeitet?
- **Rechnungen**: Welche Belege/Zahlungen brauchen Aufmerksamkeit?
- **Stammdaten**: Was muss verwaltet oder geklaert werden?

### 2. Liste links, Kontext rechts

Die Standardstruktur ist:

- links oder mittig eine ruhige Arbeitsliste,
- rechts ein Kontextbereich mit Details,
- unten oder rechts genau eine primaere Weiter-Aktion.

Der Nutzer soll selten raten muessen, wo der naechste Klick ist.

### 3. Dialoge sind nicht der Hauptarbeitsplatz

Dialoge werden nur fuer kleine, abgeschlossene Entscheidungen benutzt:

- bestaetigen,
- kurze Auswahl treffen,
- Fehler klaeren,
- einzelne Stammdaten bearbeiten.

Bestellung erfassen, Rechnung pruefen und Kundendaten im Kontext verstehen gehoeren ins Hauptfenster, nicht in verschachtelte Dialogketten.

### 4. Tabellen werden Arbeitslisten

Tabellen duerfen nicht mehr wie Datenbankansichten wirken. Jede Tabelle bekommt:

- eine klare Aufgabe,
- wenige entscheidungsrelevante Spalten,
- Status in Klartext,
- Suche/Filter direkt oberhalb,
- eine lesbare Auswahl,
- einen Detail-/Inspector-Bereich,
- keine horizontalen Scrollbalken im Normalfall.

Spalten, die nicht bei einer Entscheidung helfen, wandern in den Detailbereich.

### 5. Buttons werden Handlungsversprechen

Buttons werden nach diesen Regeln geprueft:

- Pro Ansicht gibt es eine primaere Aktion.
- Buttontexte sind Verben: `Bestellung starten`, `Beleg erzeugen`, `Als bezahlt markieren`.
- Keine doppelten Buttons fuer denselben Zweck.
- Keine unklaren Begriffe wie `Ausfuehren`, `Verarbeiten`, `Oeffnen`, wenn nicht klar ist, was passiert.
- Gefaehrliche Aktionen sind selten, neutral platziert und bestaetigungspflichtig.
- Wichtige Aktionen sind auch per Tastatur erreichbar.

### 6. Sprache wird alltagstauglich

Die sichtbare UI spricht wie ein Buerowerkzeug, nicht wie ein technisches System:

- `Rechnungen` statt nur `Offene Posten`.
- `Kasse pruefen` oder `Zahlung pruefen` im Tageskontext.
- `Pruefpunkte` nur dort, wo wirklich Konflikte geklaert werden.
- `Bestellung starten` statt `Auftrag anlegen`.
- `Letzte Mengen uebernehmen` statt `Kundensortiment vorbefuellen`.

### 7. 60+ tauglich ist ein Muss

Die App muss fuer Anwender funktionieren, die sicher mit einfachen Excel-Listen umgehen, aber keine Softwarelogik lernen wollen:

- grosse Klickziele,
- klare Auswahlzustaende,
- keine versteckten Hover-Funktionen,
- keine Pflicht-Rechtsklicks,
- kurze Texte,
- verstaendliche Fehlermeldungen,
- wenig gleichzeitige Entscheidungen,
- sichtbarer naechster Schritt.

## Screen-Zielbilder 2.0

### Heute

**Zweck:** Tagesarbeit starten, nicht beeindrucken.

Heute wird eine Aufgaben- und Arbeitswarteschlange:

- faellige Lieferungen,
- offene Rechnungen,
- offene Pruefpunkte,
- zuletzt bearbeitete Kunden/Bestellungen,
- ein grosser Primaerweg: `Kunde suchen oder Bestellung starten`.

Was entfernt wird:

- generische Kacheln,
- dekorative Kennzahlen ohne Aktion,
- Workflow-Grafiken,
- Marketing-Sprache.

Akzeptanz:

- Ein neuer Nutzer versteht in 10 Sekunden, wo er anfangen muss.
- Jede Zeile hat eine klare Aktion.
- Es gibt keinen Bereich, der nur gut aussieht.

### Kunden

**Zweck:** Kunde finden, Kundenlage verstehen, Bestellung starten.

Kunden wird zum eigentlichen Arbeitsplatz fuer wiederkehrende Lieferkunden:

- Suchfeld oben mit Name, Ort, Mail, Rechnungsnummer.
- Kundenliste mit Name, Ort, Status, letzter Bestellung, offenen Rechnungen.
- Inspector rechts mit Adresse, Telefon/Mail, Zahlart, Lieferhinweisen, letzter Bestellung, offenen Belegen.
- Primaeraktion: `Bestellung starten`.
- Sekundaeraktionen: `Letzte Belege`, `Kundenordner`, `Kundendaten bearbeiten`.

Was entfernt oder zurueckgestuft wird:

- "Kundenordner" als Hauptbegriff,
- Datei-/Ordnerlogik im Mittelpunkt,
- zu viele gleichwertige Startbuttons.

Akzeptanz:

- Kunde suchen und Bestellung starten geht ohne Seitenwechsel.
- Der Nutzer sieht vor dem Start, ob offene Rechnungen oder Lieferhinweise existieren.
- Ein leerer oder unvollstaendiger Kunde blockiert nicht wortlos, sondern zeigt den naechsten Reparaturschritt.

### Bestellungen

**Zweck:** Mengen schnell und fehlerarm erfassen.

Bestellungen bekommt einen echten Editor statt eines Dialog-Schwerpunkts:

- Liste der aktuellen Entwuerfe und heutigen Bestellungen.
- Auswahl oeffnet rechts oder darunter die Bestellung.
- Erfassungsbereich mit Kundensortiment/letzten Mengen.
- Mengenfelder sind gross, stabil und tabulatorfreundlich.
- Pfand-Rueckgaben sind sichtbar, aber nicht im Weg.
- Summe und Warnungen bleiben immer sichtbar.
- Primaeraktion: `Speichern und Beleg erzeugen`.

Was entfernt oder umgebaut wird:

- zentrale Bestellungserfassung in modalen Dialogen,
- gemischte Tabellen mit zu vielen technischen Spalten,
- unklare Trennung zwischen Entwurf, Auftrag, Rechnung und Lieferschein.

Akzeptanz:

- Eine Stammkundenbestellung kann mit Tastatur und wenigen Klicks aus letzten Mengen erfasst werden.
- Preis/Pfand-Logik bleibt aus dem UI heraus im Kern/Service.
- Unsichere Artikel oder Preisabweichungen erscheinen als klares Hindernis mit Loesungsweg.

### Rechnungen

**Zweck:** Belege und Zahlungen kontrollieren.

Rechnungen wird nicht mehr als Exportstelle gedacht, sondern als Beleg- und Zahlungsarbeitsplatz:

- Filter: `Offen`, `Faellig`, `Bezahlt`, `Alle`.
- Liste mit Rechnung, Kunde, Datum, Faelligkeit, Zahlart, Status, Betrag.
- Inspector mit Dateien, Zahlart-Hinweis, Zahlungshistorie, Belegaktionen.
- Primaeraktion je nach Status: `PDF oeffnen`, `Als bezahlt markieren`, `Beleg erzeugen`.

Was entfernt oder entkoppelt wird:

- Belegerzeugung als isolierte Funktionsseite,
- offene Posten als rein technische Liste,
- Exportaktionen ohne Statuskontext.

Akzeptanz:

- Der Nutzer sieht sofort, welche Rechnung Aufmerksamkeit braucht.
- PDF/Excel sind nahe an der Rechnung, nicht in einem separaten Suchprozess.
- Zahlart steuert sichtbar die naechste Handlung.

### Stammdaten

**Zweck:** Verwaltung, nicht Tagesarbeit.

Stammdaten bleibt wichtig, wird aber bewusst niedriger priorisiert:

- Tabs/Segmente: `Kunden`, `Artikel`, `Pruefpunkte`, `Import`, `Einstellungen`.
- Listen sind kompakt und suchbar.
- Detailbearbeitung in Inspector oder ruhigem Bearbeiten-Dialog.
- Pruefpunkte zeigen Auswirkungen: "blockiert Bestellung", "Preisabweichung", "Kontaktkonflikt".

Was entfernt wird:

- Stammdaten als gleichwertiger Tagesstart,
- gequetschte Bearbeiten/Liste-Kombinationen,
- technische Importdetails ohne Handlung.

Akzeptanz:

- Tagesarbeit kann erledigt werden, ohne Stammdaten zu verstehen.
- Wenn Stammdaten benoetigt werden, fuehrt die App gezielt zum betroffenen Punkt.

## Komponenten-Audit

### Navigation

Bleibt:

- links eine ruhige Hauptnavigation,
- maximal fuenf Hauptbereiche,
- Einstellungen unten oder unter Stammdaten.

Wird geaendert:

- keine nummerierte Navigation,
- keine schweren Markenbloecke,
- keine Navigationspunkte fuer einzelne technische Funktionen.

### Toolbar

Bleibt:

- globale Suche,
- `Neu`,
- `Aktualisieren`,
- Hilfe.

Wird geaendert:

- `Neu` muss kontextsensitiv werden: auf Kunden `Bestellung starten`, auf Rechnungen `Beleg erzeugen` oder `Zahlung erfassen`.
- Hilfe wird klein und ruhig.
- Toolbar darf keine zweite Hauptnavigation werden.

### Inspector

Wird zur zentralen 2.0-Komponente:

- zeigt Kontext zur Auswahl,
- zeigt Status,
- zeigt Warnungen,
- zeigt naechste Aktion,
- entlastet Tabellen von Nebendaten.

### Tabellen

Jede bestehende Tabelle wird geprueft:

- Welche Entscheidung trifft der Nutzer hier?
- Welche Spalten braucht er dafuer wirklich?
- Was gehoert in den Inspector?
- Welche Standardfilter braucht die Liste?
- Wie sieht ein leerer Zustand aus?
- Was passiert bei Doppelklick oder Enter?

### Formulare

Formulare werden kuerzer und gefuehrter:

- Pflichtfelder zuerst,
- optionale Felder einklappbar oder im Detailbereich,
- klare Fehler direkt am Feld,
- Speichern mit sichtbarer Rueckmeldung,
- naechster sinnvoller Schritt nach dem Speichern.

## Technische Leitplanken

Der Umbau bleibt innerhalb der Architekturregeln:

- UI bleibt Schale, keine Fachlogik in Widgets.
- Bestellung, Beleg, Pfand, Preis, Zahlart und Faelligkeit bleiben in Kern/Services/Vorgaengen.
- UI-Komponenten duerfen Workflows darstellen, aber nicht berechnen.
- Exportpfade, Vorlagen und Einstellungen bleiben Konfiguration/Daten.
- Tests sichern Kernregeln und zentrale UI-Flows.

## Umsetzung in Meilensteinen

### Meilenstein 0: Inventur und Design-Schulden einfrieren

Ziel:

- alle bestehenden Hauptoberflaechen anhand dieses Masterplans bewerten,
- alte verworfene Konzepte als historisch markieren,
- keine weitere Arbeit an der Betriebs-Cockpit-Richtung.

Akzeptanz:

- pro Hauptbereich existiert eine Umbauentscheidung,
- UI-Begriffe sind festgelegt,
- offene Designfragen sind dokumentiert.

### Meilenstein 1: Shell 2.0 stabilisieren

Ziel:

- aktuelle helle Shell bereinigen,
- Navigation, Toolbar und Grundlayout endgueltig auf 2.0 bringen,
- Inspector-Basiskomponente einfuehren.

Akzeptanz:

- keine Hauptseite hat horizontalen Scroll,
- einheitliche Abstaende, Typografie und Buttonhoehen,
- `Neu` und Suche verhalten sich pro Bereich nachvollziehbar.

### Meilenstein 2: Kundenarbeitsplatz

Ziel:

- Kundenliste + Inspector bauen,
- Bestellung aus Kundenkontext starten,
- Kundenordner-Dateien als Kontext, nicht als Hauptkonzept.

Akzeptanz:

- Kunde suchen -> Details sehen -> Bestellung starten in einem Fluss,
- offene Rechnungen und Lieferhinweise sind sichtbar,
- 60+-Smoke-Test besteht ohne Erklaertext.

### Meilenstein 3: Bestellarbeitsplatz

Ziel:

- Bestellliste und Bestelleditor ins Hauptfenster holen,
- letzte Mengen, aktuelle Mengen, Pfand und Summe sauber fuehren,
- Dialoge aus dem Hauptfluss entfernen.

Akzeptanz:

- Stammkundenbestellung aus letzten Mengen ist in wenigen Schritten erledigt,
- Fehler zeigen konkrete Reparatur,
- Beleg kann direkt aus gespeicherter Bestellung erzeugt werden.

### Meilenstein 4: Rechnungen und Kasse

Ziel:

- Rechnungen, Dateien und offene Zahlungen zusammenfuehren,
- Statusfilter und Inspector-Aktionen bauen,
- Zahlung markieren und Belege oeffnen vereinfachen.

Akzeptanz:

- offene/faellige/bezahlte Rechnungen sind eindeutig unterscheidbar,
- PDF/Excel sind ohne Suche auffindbar,
- Zahlarttexte und Faelligkeiten bleiben regressionssicher.

### Meilenstein 5: Stammdaten und Pruefpunkte

Ziel:

- Stammdaten als Adminbereich ordnen,
- Pruefpunkte nach Auswirkung priorisieren,
- Import als gefuehrten Vorgang statt technischer Maske gestalten.

Akzeptanz:

- Tagesnutzer koennen Stammdaten ignorieren,
- blockierende Pruefpunkte zeigen Loesungsaktion,
- Import meldet Ausreisser ohne Absturz und ohne Ratespiel.

### Meilenstein 6: UAT und Regression

Ziel:

- kompletter Anwenderlauf mit echtem Kundenordner,
- Regression fuer Berechnung, Export, Snapshots und UI-Hauptwege,
- visuelle Kontrolle der Hauptscreens.

Akzeptanz:

- Golden-Werte Metzgerei Karl bleiben korrekt,
- Rechnung/Lieferschein Excel und PDF werden erzeugt,
- offene Posten zeigen richtige Snapshot-Betraege,
- 60+-Bedienprobe: Bestellung ohne Entwicklerhilfe moeglich.

## Harte Abnahmekriterien fuer 2.0

1. Die App fuehlt sich nicht mehr wie ein Prototyp an.
2. Der Hauptweg ist immer sichtbar: Kunde -> Bestellung -> Beleg -> Zahlung.
3. Kein Bereich zeigt mehrere gleich wichtige Hauptaktionen.
4. Tabellen sind Arbeitslisten, keine Datenbankfenster.
5. Dialoge blockieren den Hauptfluss nicht mehr.
6. Die Oberflaeche ist hell, ruhig, modern und markennah, aber nicht dekorativ ueberladen.
7. Anwender ueber 60 koennen die Kernaufgabe ohne versteckte Bedienmuster erledigen.
8. Fachlogik bleibt ausserhalb der UI.
9. Tests und Golden-Files bleiben die Korrektheitsanker.

## Sofortige naechste Schritte

1. Bestehende Screens gegen diesen Masterplan auditieren.
2. Inspector-Grundkomponente entwerfen und in Shell 2.0 einbauen.
3. Kundenbereich als ersten echten 2.0-Arbeitsplatz umbauen.
4. Danach Bestellungen aus dem Dialog in einen Hauptfenster-Workflow ueberfuehren.
5. Rechnungen/Kasse als zusammenhaengenden Kontrollbereich neu bauen.
