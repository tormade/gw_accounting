# Winklmeier Office 2.0: Screen-Audit und Umbaukarte

Dieses Audit bewertet den aktuellen UI-Stand gegen den 2.0-Masterplan. Ziel ist nicht, den bestehenden Stand zu verteidigen, sondern klar zu entscheiden, welche Teile bleiben, welche nur technisch wiederverwendet werden und welche aus dem Hauptfluss verschwinden.

## Gesamtbefund

Die aktuelle App hat fachlich schon viel Substanz, wirkt in der Bedienung aber noch wie mehrere nebeneinanderliegende Werkzeuge:

- Startseite, Kundenordner, Bestellung, Belegerzeugung und offene Posten sind noch zu stark als getrennte Stationen sichtbar.
- Viele Aktionen sitzen in Panels oder Dialogen, statt aus dem ausgewaehlten Objekt heraus angeboten zu werden.
- Tabellen zeigen teilweise Rohdaten, wo der Nutzer eigentlich eine Entscheidung treffen soll.
- Der Begriff `Kundenordner` beschreibt die Herkunft der Daten, aber nicht mehr den idealen Hauptarbeitsplatz.
- Der Umbau auf die helle Office-Shell ist begonnen, aber die Inhaltsflaechen sind noch nicht 2.0.

Die 2.0-Linie lautet daher:

**Die App wird von Dateiverwaltung und Funktionsseiten auf Objektarbeit umgebaut: Kunde auswaehlen, Kontext sehen, naechste Aktion ausfuehren.**

## Hauptfenster und Shell

Dateien:

- `src/getraenkeladen_tool/ui/main_window.py`
- `src/getraenkeladen_tool/ui/layouts.py`
- `src/getraenkeladen_tool/ui/theme.py`

Aktueller Stand:

- Hauptnavigation ist bereits auf `Heute`, `Kunden`, `Bestellungen`, `Rechnungen`, `Stammdaten` reduziert.
- Toolbar ist hell und ruhig.
- Die Seiten werden weiterhin als ganze alte Panels in einen Stack gelegt.
- Es gibt noch keine echte Inspector-Basiskomponente.
- `Neu` in der Toolbar startet aktuell immer eine neue Bestellung und ist noch nicht kontextsensitiv.

2.0-Entscheidung:

- Shell bleibt, wird aber um einen wiederverwendbaren Inspector und kontextsensitive Toolbar-Aktionen erweitert.
- `Neu` wird je nach Bereich umbenannt oder mit Kontext belegt:
  - Heute: `Bestellung starten`
  - Kunden: `Bestellung starten`
  - Bestellungen: `Neue Bestellung`
  - Rechnungen: `Beleg erzeugen` oder keine Primaeraktion ohne Auswahl
  - Stammdaten: `Eintrag anlegen`
- Die Shell darf keine Fachlogik enthalten. Sie leitet nur an die zuständigen Panels/Services weiter.

Naechster Umbau:

1. `InspectorPanel` in `layouts.py` einfuehren.
2. Shell-Kontext fuer Primaeraktion vorbereiten.
3. Bestehende Panels schrittweise auf Liste + Inspector umbauen.

## Heute

Datei:

- `src/getraenkeladen_tool/ui/dashboard_panel.py`

Aktueller Stand:

- Startseite wurde bereits vereinfacht und fuehrt in Arbeitsbereiche.
- Es gibt noch workflowartige Karten und Beispiel-/Demo-Elemente.
- Die Seite beantwortet noch nicht hart genug: "Was muss heute erledigt werden?"

2.0-Entscheidung:

- Heute wird eine Tageswarteschlange, keine Erklaerseite.
- Nur Eintraege mit Handlung bleiben sichtbar:
  - faellige Lieferungen,
  - offene/faellige Rechnungen,
  - blockierende Pruefpunkte,
  - zuletzt bearbeitete Entwuerfe.
- Demo-Beispiele verschwinden aus der regulaeren Oberflaeche oder werden nur in einer Muster-Datenbank gezeigt.

Naechster Umbau:

1. Karten durch Aufgabenliste ersetzen.
2. Jede Zeile bekommt Status, kurze Beschreibung und Aktion.
3. Primaeraktion oben: `Kunde suchen oder Bestellung starten`.

## Kunden

Dateien:

- `src/getraenkeladen_tool/ui/customer_folder_panel.py`
- `src/getraenkeladen_tool/ui/customer_panel.py`

Aktueller Stand:

- `CustomerFolderPanel` ist faktisch der Kundenarbeitsplatz, traegt aber noch den alten Datei-/Ordnerbegriff.
- Es gibt mehrere Buttons nebeneinander: Ordner oeffnen, Datei oeffnen, Bestellung starten, Lieferschein, Rechnung.
- Kundendatenpflege liegt separat in `CustomerPanel` unter Stammdaten.
- Die Auswahl eines Kunden fuehrt noch nicht konsequent zu einem ruhigen Kontextbereich.

2.0-Entscheidung:

- `Kunden` wird ein eigener Arbeitsplatz mit Liste + Inspector.
- Der Begriff `Kundenordner` bleibt nur als Sekundaeraktion fuer Dateien.
- Primaeraktion nach Kundenauswahl: `Bestellung starten`.
- Belegaktionen erscheinen erst, wenn eine passende Bestellung oder Rechnung im Kontext ausgewaehlt ist.
- Kundendatenbearbeitung bleibt Sekundaeraktion, nicht Hauptweg.

Naechster Umbau:

1. `CustomerFolderPanel` zu einem 2.0-Kundenarbeitsplatz umbauen oder durch ein neues `CustomerWorkspacePanel` ersetzen.
2. Kundenliste links/mittig: Name, Ort, Status, letzte Bestellung, offene Rechnung.
3. Inspector rechts: Adresse, Kontakte, Zahlart, Lieferhinweise, letzte Bestellung, offene Belege.
4. Buttons reduzieren:
   - primaer: `Bestellung starten`
   - sekundär: `Letzte Belege`, `Kundenordner`, `Kundendaten bearbeiten`

## Bestellungen

Datei:

- `src/getraenkeladen_tool/ui/order_panel.py`

Aktueller Stand:

- Bestellverwaltung hat fachlich viel Logik, nutzt aber weiterhin einen Dialog fuer die zentrale Erfassung.
- Tabellen fuer Sortiment, Positionen, Pfand und Bestellungen konkurrieren um Aufmerksamkeit.
- Buttons wie `Aus Sortiment uebernehmen` sind funktional, aber noch nicht als gefuehrter Erfassungsfluss gestaltet.

2.0-Entscheidung:

- Bestellungen werden ein Hauptfenster-Arbeitsplatz.
- Dialoge duerfen nur noch Hilfsentscheidungen abdecken.
- Der Editor fuehrt von Kunde -> letzte Mengen -> aktuelle Mengen -> Pfand -> Summe -> Beleg.
- Summe, Warnungen und Primaeraktion bleiben sichtbar.

Naechster Umbau:

1. Bestellliste und Bestelleditor sichtbar trennen.
2. Editor in den Hauptbereich holen.
3. Dialog-Erfassung schrittweise abschalten oder nur als Uebergangsweg behalten.
4. Tastaturbedienung fuer Mengenfelder priorisieren.

## Rechnungen und Kasse

Dateien:

- `src/getraenkeladen_tool/ui/report_panel.py`
- `src/getraenkeladen_tool/ui/document_workflow_panel.py`
- `src/getraenkeladen_tool/ui/document_archive_panel.py`

Aktueller Stand:

- Offene Posten, Tagesliste, Kontakte und Dokumente sind technisch getrennt.
- Belegerzeugung laeuft ueber eigene Panels/Dialoge.
- Dateien oeffnen, PDF neu erzeugen und Zahlung pruefen sind nicht in einem gemeinsamen Rechnungskontext gebuendelt.

2.0-Entscheidung:

- `Rechnungen` wird der Beleg- und Zahlungsarbeitsplatz.
- Die Liste zeigt Rechnungen/Belege mit Status.
- Der Inspector zeigt Dateien, Zahlart, Faelligkeit, Betrag und naechste Aktion.
- Offene Posten werden als Status innerhalb von Rechnungen sichtbar, nicht als eigener mentaler Hauptbereich.

Naechster Umbau:

1. `ReportPanel` auf Rechnungsstatusliste fokussieren.
2. Belegdateien und Aktionen in Inspector verschieben.
3. `DocumentWorkflowPanel` aus dem Hauptfluss herausloesen und als Aktion an Bestellung/Rechnung anbinden.
4. Zahlungsstatus klarer markieren: offen, faellig, bezahlt.

## Stammdaten und Pruefpunkte

Dateien:

- `src/getraenkeladen_tool/ui/customer_panel.py`
- `src/getraenkeladen_tool/ui/product_panel.py`
- `src/getraenkeladen_tool/ui/checklist_panel.py`
- `src/getraenkeladen_tool/ui/settings_panel.py`

Aktueller Stand:

- Stammdaten sind als Tabs gebuendelt.
- Kunden/Artikelpflege ist weiterhin formular- und tabellenlastig.
- Pruefpunkte haben viele direkte Buttons, aber wenig Priorisierung nach Wirkung.
- `settings_panel.py` traegt in der Navigation aktuell die Tab-Beschriftung `Import`, was langfristig getrennt werden sollte.

2.0-Entscheidung:

- Stammdaten werden Adminbereich.
- Pruefpunkte werden nach Auswirkung priorisiert:
  - blockiert Bestellung,
  - Preisabweichung,
  - Kontaktdatenkonflikt,
  - Importhinweis.
- Bearbeitung erfolgt im Detailbereich oder in klaren kleinen Dialogen.

Naechster Umbau:

1. Pruefpunkte mit Prioritaet/Blockerstatus versehen.
2. Aktionsbuttons im Pruefkontext reduzieren.
3. Import und Einstellungen sprachlich trennen.

## Komponentenentscheidungen

### Buttons

Aktuelle Beobachtung:

- Viele Panels haben mehrere gleichgewichtige Buttons.
- Manche Buttontexte sind technisch oder dateibezogen.

2.0-Regel:

- ein primaerer Button pro Screen oder Auswahl,
- weitere Aktionen als sekundäre Buttons im Inspector,
- Buttontexte als konkrete Handlung.

### Tabellen

Aktuelle Beobachtung:

- Tabellen werden fast ueberall als Hauptdarstellung genutzt.
- Einige Tabellen enthalten mehr Spalten, als fuer die jeweilige Entscheidung noetig sind.

2.0-Regel:

- Tabellen sind Listen mit Auswahl,
- Detailinformationen gehen in den Inspector,
- Spalten werden pro Entscheidungsfrage reduziert.

### Dialoge

Aktuelle Beobachtung:

- Bestellung und Belegerzeugung laufen noch stark ueber Dialoge.

2.0-Regel:

- Kernworkflow bleibt im Hauptfenster,
- Dialoge nur fuer kleine Nebenschritte.

### Suchfelder

Aktuelle Beobachtung:

- Suche existiert in mehreren Panels, aber noch nicht als durchgehendes Suchmodell.

2.0-Regel:

- globale Suche in der Toolbar fuer Kunde/Rechnung/Artikel,
- lokale Suche in Listen fuer den aktuellen Bereich,
- leere Suche zeigt keine zufaellige Anfangsliste.

## Empfohlene Reihenfolge

1. Inspector-Basiskomponente und Shell-Kontextaktion.
2. Kundenarbeitsplatz 2.0.
3. Bestellarbeitsplatz 2.0.
4. Rechnungen/Kasse 2.0.
5. Heute als echte Tageswarteschlange.
6. Stammdaten/Pruefpunkte bereinigen.
7. Voller UAT und Regression.

## Erste Code-Aufgabe

Die erste echte Implementierungsaufgabe ist der Kundenarbeitsplatz:

- neue Inspector-Struktur in `layouts.py`,
- Kundenbereich in `main_window.py` weiterhin unter `Kunden`,
- `customer_folder_panel.py` visuell und sprachlich auf `Kunden` statt `Kundenordner`,
- Primaeraktion `Bestellung starten`,
- Sekundaeraktionen klar gruppieren,
- Tabellen auf entscheidungsrelevante Spalten reduzieren,
- Tests fuer Navigation und wichtigste Buttontexte anpassen.
