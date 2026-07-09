# Fortschritt

## Aktueller Meilenstein

Onboarding-/Migrations-Tool als belastbare Datenbasis.

## Zielbild

Das Produktziel steht in `docs/zielbild.md`: ein schlankes lokales Windows-Buerowerkzeug fuer Kundenkontakt, Bestellung, Lieferschein, Rechnung, offene Posten, Tagesliste und Auswertung. Der wichtigste Hauptweg ist Kunde oeffnen -> letzte Mengen sehen -> neue Mengen erfassen -> Beleg erzeugen.

## Erledigt

- UI-Prototyp mit Kundenordner-Arbeitsplatz, Bestellverwaltung, Rechnungs-/Lieferschein-Erzeugung und Stammdatenpflege.
- Import der zentralen Artikel- und Lieferkundenlisten als Stammdaten.
- Archivieren statt Loeschen fuer Stammdaten und Auftraege.
- Excel-/PDF-Ausgabe fuer Rechnung und Lieferschein mit Lieferpauschale, Pfand und Summenformeln.
- Onboarding-Kern fuer echte Kundenordnerdateien.
- Golden-File-Tests fuer Metzgerei Karl Rechnung und Lieferschein.
- Golden-File-Test fuer Privat-Ueberweiser mit Faelligkeitsdatum.
- Robuster Ordnerlauf, der Ausreisser-Dateien meldet und ueberspringt.
- Artikel-Matching gegen die zentrale Artikelliste mit bestaetigten Alias-Schreibweisen.
- Kundensortiment-Datenmodell mit letzter Menge, alter Quelle und aktuellem zentralem Preis.
- Preisabweichungen zwischen Kunden-Excel und zentralem Artikelstamm werden als offene Prueffaelle erkannt.
- Prueflisten-UI fuer offene Kunden-/Artikel-/Preiskonflikte mit Erledigt/Wieder-oeffnen-Aktion.
- Pruefliste mit konkreten Aktionen: zentraler Preis, Excel-Preis oder Artikelalias bestaetigen.
- Pruefliste mit konkreten Aktionen fuer Kundendaten-Konflikte: zentrale Liste oder Kunden-Excel uebernehmen.
- Kundensortiment im Auftragsdialog: letzte Artikel sehen und direkt als Position uebernehmen.
- Persona-UX-Test fuer wenig IT-affine Anwender ausgewertet und Sofortverbesserungen umgesetzt.
- End-to-End-Test fuer realen Ablauf: Kunden-Excel importieren, zentrale Preise anwenden, Bestellung erstellen, Excel/PDF erzeugen.
- Belegfluss mit Hauptbutton fuer komplette Erstellung von Excel + PDF.
- PDF-Nacherzeugung aus vorhandener Excel liest Pfand-Rueckgaben aus denselben Zeilen wie der Excel-Export.
- Gespeicherte Preisentscheidungen aus der Pruefliste werden im Kundensortiment direkt angewendet.
- Rechnung-/Lieferschein-Erstellung sprachlich und visuell als gefuehrter Ablauf fuer Erstnutzer vereinfacht.
- Hauptnavigation auf Kundenordner-Arbeitsweise umgestellt: Kunde suchen, Ordnerdateien sehen, Bestellung und Belege von dort starten.
- UI-Altlasten entfernt: alter Direktbeleg-Sonderweg geloescht, verstecktes Belegarchiv aus dem Hauptfenster entkoppelt und sichtbare Texte auf Kundenordner/Bestellung vereinheitlicht.
- Persona-Review fuer einen wenig IT-affinen Erstnutzer umgesetzt: Vorlage aus Kundenordner klarer markiert, Beispielkontakte gekennzeichnet und Beleg-Korrekturen verstaendlicher benannt.
- Startseite ueberarbeitet: Hauptbuttons fuehren jetzt in unterschiedliche Arbeitsbereiche statt alle in denselben Kundenordner.
- Neues Bestellfenster kleiner und scrollbar gemacht, damit es auf kleineren Bildschirmen nutzbar bleibt.
- Kundenordner zeigt neueste Excel/PDF-Dateien zuerst und vermeidet das falsche Versprechen einer markierten Excel-Direktvorlage.
- Suchfelder erklaeren jetzt, dass ein Treffer angeklickt werden muss, und zeigen klar an, wenn nichts gefunden wurde.
- "Neue Bestellung aus letzten Mengen starten" befuellt jetzt automatisch die Bestellpositionen aus dem Kundensortiment und laesst ungeklaerte Artikel aus.
- Startseite vereinfacht: die grosse gruene Box erklaert jetzt den Kundenordner-Start statt ein unechtes Suchfeld zu zeigen.
- Mac-Oberflaechentest als wenig IT-affiner Erstnutzer durchgespielt: Startseite, Kundenordner, Kundensuche und leere Kundenordner geprueft.
- Kundenkontext wird geloescht, sobald die Suche wieder uneindeutig ist; dadurch koennen keine Aktionen mehr versehentlich auf dem vorherigen Kunden bleiben.
- Kundensuche klappt Treffer nach Auswahl ein und oeffnet sie beim Tippen wieder, damit die Auswahl nicht wie eine dauerhafte zweite Liste wirkt.
- App erzwingt eine helle Palette, damit Tabellen, Dropdowns und Eingabefelder auf macOS nicht durch System-Dark-Mode unlesbar werden.
- Kundenordner unterscheidet jetzt sichtbar zwischen "Neue Bestellung aus letzten Mengen starten" und "Neue leere Bestellung starten".
- Technische Zielarchitektur aus neuem Input uebernommen: Clean-Architecture-Richtung mit Kern, Vorgaengen, Adapter und UI-Schale.
- Architektur-Invarianten in `AGENTS.md` verankert und Roadmap um schrittweise technische Migration ergaenzt.
- Belegberechnung als UI- und DB-freie Kernregel umgesetzt und mit Golden-Werten fuer Metzgerei Karl abgesichert.
- Offene Posten, Excel, PDF und Belegvorschau nutzen dieselbe Kernberechnung.
- Erster Anwendungsvorgang `beleg_erzeugen` angelegt und im Bestell-Hauptweg fuer Lieferschein/Rechnung genutzt.
- Mac-Oberflaechentest aus 60+-Erstnutzer-Perspektive erneut durchgespielt und drei Stolperstellen verbessert.
- Suchfelder zeigen ohne Eingabe keine zufaellige Anfangsliste mehr, sondern warten auf eine konkrete Suche.
- Kundenordner ohne echten Ordner wird am Startknopf klar als "Ohne Kundenordner leere Bestellung starten" gekennzeichnet.
- Ungueltiges Speichern einer Bestellung zeigt jetzt ein klares Warnfenster, z. B. bei fehlender Bestellnummer.
- Kritischer Mac-Oberflaechentest erneut durchgefuehrt: Startseite, Kundenordner, Trefferliste und leere Kundenordner aus 60+-Erstnutzer-Sicht geprueft.
- Suchfelder sind sprachlich kuerzer und fehlertoleranter: klare Trefferliste, Doppelklick/Enter-Unterstuetzung als Bonus und kein technisches "unten"-Wording mehr.
- Hauptnavigation ist als "Hauptnavigation" benannt und fokussierbar, damit Tastatur- und Assistenzbedienung verlaesslicher werden.
- Startseite kennzeichnet Beispielkontakte jetzt eindeutig als Demo-Beispiele, damit sie nicht mit echten Tagesaufgaben verwechselt werden.
- Voller Mac-Oberflaechen-Haupttest abgeschlossen: Kunde Cafe Nord gesucht, Bestellung TEST-UI-230623-1 angelegt und daraus Lieferschein LS-UI-230623-1 sowie Rechnung RE-UI-230623-1 erzeugt.
- Lieferschein und Rechnung wurden jeweils als Excel und PDF im Kundenordner erzeugt und die Excel-Dateien enthalten Summenformeln fuer Positionen und Gesamtbetrag.
- Belegdialoge nach 60+-Erstnutzer-Test vereinfacht: Bei vorausgewaehlter Bestellung wird die Suchspalte ausgeblendet, alle Schritte sind als kurze Reiter sichtbar und die Summe bleibt prominent.
- Suchfelder zeigen bei eindeutigem Treffer jetzt, dass direkt weitergearbeitet werden kann, statt irrefuehrend noch einen Pflicht-Klick zu suggerieren.
- Beleg-Snapshot-Datenmodell eingefuehrt: Erzeugte Belege speichern Positionen, Pfand-Rueckgaben, Lieferpauschale und Brutto als reproduzierbare Snapshot-Zeilen.
- Offene Posten nutzen beim Erzeugen den gespeicherten Beleg-Snapshot-Brutto; DB-Bootstrap legt die Snapshot-Tabelle auch fuer bestehende Installationen an.
- UAT-/Regressionstest dokumentiert und wichtigste Befunde behoben: Zahlart-Texte mit Ueberweisung-Faelligkeit, Teil-Export-Schutz, erweiterte offene Posten, Preisabweichungen beim Vorbefuellen und idempotentes Re-Onboarding.
- Neues Designkonzept "Winklmeier Lieferservice-Cockpit 2026" umgesetzt: website-nahe Weiss/Rot/Schwarz-Marke, Kopfzeile mit Claim und Lieferservice-Telefon, eckige Arbeitsflaechen, groessere Bedienziele, staerkere Tabellenhierarchie und vollstaendigere Offene-Posten-Flaeche.
- Generische KI-UI-Anmutung weiter reduziert: neues "Winklmeier Betriebs-Cockpit 2026" mit nummerierter Navigation, Seiten-Kickern, Arbeitszonen fuer Route/Kasse/Pruefstand/Beleg, schwarzen Tabellenkoepfen mit roter Markenlinie und semantischen Card-Tones fuer alle Hauptflaechen.
- Radikaler UI-Schnitt begonnen: Hauptnavigation auf Aufgaben reduziert, Startseite als gefuehrtes Ablaufbrett neu gebaut, initial leere Suchlisten entfernt, Stammdaten von gequetschtem Split-Screen auf Bearbeiten-oben/Liste-unten umgestellt und horizontales Seiten-Scrollen abgeschaltet.
- Neue Designentscheidung dokumentiert: Die Betriebs-Cockpit-Richtung wird verworfen. Zielbild ist nun "Winklmeier Office 2026": Apple-like helle Shell, ruhige Sidebar/Toolbar, Listen plus Inspector, Lexware-Aufgabenlogik und SAP-Fiori-Objektarbeit.
- Phase 1 der neuen Office-Shell umgesetzt: schwerer Markenbanner entfernt, helle Toolbar mit globaler Suche/Neu/Aktualisieren eingefuehrt, Sidebar auf Apple-like helle Navigation ohne Nummern umgestellt, Hauptbereiche auf Heute/Kunden/Bestellungen/Rechnungen/Stammdaten reduziert und Pruefpunkte/Import unter Stammdaten gebuendelt.
- Winklmeier Office 2.0 als radikaler Produktumbau festgelegt: alle Oberflaechen, Buttons, Tabellen und Dialoge werden am Hauptfluss Kunde -> Bestellung -> Beleg -> Zahlung gemessen; der Masterplan steht in `docs/winklmeier-office-2.0-masterplan.md`.
- Bestehende Hauptscreens gegen den 2.0-Masterplan auditiert: konkrete Umbaukarte fuer Shell, Heute, Kunden, Bestellungen, Rechnungen/Kasse und Stammdaten steht in `docs/winklmeier-office-2.0-screen-audit.md`.
- Erster 2.0-Code-Schritt umgesetzt: Toolbar-Hauptaktion ist nicht mehr generisch `Neu`, sondern passt sich je Hauptbereich an und ist in Bereichen ohne sicheren Kontext deaktiviert.
- Winklmeier Office 2.0 Schrittfolge umgesetzt: wiederverwendbarer Inspector eingefuehrt, Kundenarbeitsplatz auf Liste + Kontext + `Bestellung starten` umgebaut, Bestelleditor ins Hauptfenster geholt, Rechnungen/Kasse auf Rechnungsliste + Zahlungs-Inspector umgestellt, Heute als Tagesliste statt Demo-/Workflow-Flaeche gebaut und Pruefpunkte/Import sprachlich bereinigt.
- Volle Regression nach dem 2.0-Umbau ist gruen: 223 Tests bestanden, `compileall src tests` erfolgreich.
- Winklmeier Office 2.0 wurde von Thomas abgenommen und im Programm erneut geprueft: volle Regression 223 Tests bestanden, `compileall src tests` erfolgreich, Screenshot-Smoke fuer alle fuenf Hauptbereiche unter `/private/tmp/getraenkeladen-design-preview/winklmeier-office-2-accepted`.
- Visueller Button-/Alignment-Audit nach Computer-Use-Anfrage durchgefuehrt: Hauptbereiche erneut als Screenshots geprueft, Aktionsbuttons in Bestellungen, Kunden-/Artikel-Stammdaten, Tagesliste und Rechnungen vereinheitlicht, zu lange Buttontexte gekuerzt; volle Regression 223 Tests bestanden.
- Kennzahlenbereich auf "Heute" visuell ueberarbeitet: kompakte Ueberblick-Zeilen ersetzen die zu hohen Leerkarten, Zahlen/Labels sind klar ausgerichtet und der Block bleibt scanbar neben der Tagesliste.
- Visueller Voll-UAT nach Office-2.0-Umbau durchgefuehrt: Heute, Kunden, Bestellungen, Belege, Rechnungen und Stammdaten per Computer-Use geprueft; Bestellung fuer Cafe Nord mit Lieferschein LS-UAT-050726-2 und Rechnung RE-UAT-050726-2 erfolgreich erzeugt.
- Design-Polish 2. Runde umgesetzt: Belegarchiv-Spalten fuer Belegnummer/Status verbreitert, irrefuehrender Farbhinweis im Belegdialog entfernt, Belegaktionen nutzen jetzt auch die bereits geladene Bestellung ohne zusaetzlichen Tabellenklick, VS-Code-Start auf stabile Benutzer-venv umgestellt; volle Regression 229 Tests bestanden.
- Original-Excel-Arbeitsweise umgesetzt: Belege werden bei vorhandener Kunden-Excel aus der neuesten echten Kunden-Excel fortgeschrieben, Artikelzeilen bleiben stehen, nicht bestellte Artikel bekommen leere Mengen, Pfand-Rueckgaben werden in vorhandene Pfandstufen wie 3,10 / 4,50 / 1,50 EUR geschrieben; Golden-Tests gegen Metzgerei-Karl-Originaldatei ergaenzt, volle Regression 231 Tests bestanden.
- Stammdaten-Reiter beschleunigt: Beim Oeffnen wird nur noch der aktuell sichtbare Stammdaten-Unterbereich aktualisiert; Kunden, Artikel und Pruefpunkte laden nicht mehr unnoetig gemeinsam im UI-Thread.
- Auswahllisten fuer Kunden, Bestellungen und Artikel zeigen jetzt sofort die verfuegbaren Eintraege und filtern beim Tippen weiter ein; Automations-Roadmap fuer sichere Vorschlaege mit Vorschau/Bestaetigung unter `docs/automationen-roadmap.md` ergaenzt.
- Automationen umgesetzt: Kunden-Schnellstart, Dublettenwarnungen, Bestell-Plausibilitaet, Belegpruefung, Kundenordner-Excel-Scan, Zahlungshinweis-Vorschau, Monatsabschluss-Checks, typische Mengen und Arbeits-Cockpit-Service; bewusst nicht umgesetzt: Sammelarbeitsliste "Heute fertig machen" und automatische Lieferpauschalen-Gewohnheit.
- Automation-UAT durchgefuehrt: alle Automationsservices mit isolierten UAT-Daten geprueft, reproduzierbarer UAT-Report fuer Schnellstart, Dubletten, Plausibilitaet, Belegpruefung, Kundenordner-Scan, Zahlungshinweis, Monatsabschluss, typische Mengen und Arbeits-Cockpit ist OK; Computer Use konnte lokale Python/PySide-Fenster wegen Tool-Timeout nicht auslesen.
- 60+-UAT fuer Bestellung -> Lieferschein -> Rechnung durchgefuehrt: 8 Artikel wurden als Kundenvorschlaege bereitgestellt, nur 2 Artikel mit Mengen erfasst, Lieferschein und Rechnung als Excel/PDF erzeugt; beide Excel-Dateien behalten alle 8 Artikelzeilen und haben genau 2 Mengenzeilen. Computer Use hat den sichtbaren UAT-Report in TextEdit erfolgreich ausgelesen.
- Sichtbarer 60+-UAT direkt im Programm nachgestellt: isolierte App oeffnet Kundenbereich, waehlt Kunde aus, startet Bestellung, uebernimmt 2 Mengenpositionen aus 8 vorgeschlagenen Artikeln, erzeugt Lieferschein und Rechnung per Excel+PDF; Abschlussreport von Computer Use gelesen.
- Vorbefuellung repariert: Neue Bestellung nutzt zuerst Kundensortiment/letzte Excel-Mengen und faellt jetzt auf die letzte vorhandene Kundenbestellung zurueck, wenn kein Sortiment mit Mengen vorhanden ist.
- Leerpositionen fachlich zugelassen: Bestellungen koennen Artikel mit Menge 0 speichern, Kundensortiment-Zeilen mit letzter Menge 0 werden als sichtbare Platzhalter uebernommen, Excel schreibt dafuer leere Mengenzellen und PDF zeigt keine 0,00-Zeilensumme; volle Regression 250 Tests bestanden.
- Deloma/GESOFT-Logiken 1/3/4/5 umgesetzt: Nachbestellvorlage als Service mit Mengen-/Leer-/Pruefzaehlung, Pfandprozess auf die festen Stufen 1,50 / 3,10 / 4,50 EUR zentralisiert und beim Speichern geprueft, Stammdatenimport hat Vorschau plus Bestaetigung, Rechnungsarbeitsplatz filtert nach offen/faellig/ueberfaellig/teilbezahlt und kann Teilzahlungen markieren; volle Regression 255 Tests und `compileall src tests` erfolgreich.
- Arbeitsautomationen weiter geschliffen: Nach dem Speichern bietet die Bestellung direkt Lieferschein/Rechnung/weitere Bestellung an, Bestell- und Belegnummern koennen per Button vorgeschlagen werden, bleiben aber jederzeit frei editierbar; Speicherhinweise werden jetzt nach Blockern, Warnungen und Hinweisen gruppiert. Volle Regression 259 Tests und `compileall src tests` erfolgreich.
- Weitere Automationen umgesetzt: unvollstaendige Bestellungen werden vor Speichern/Belegerstellung gemeldet, Belegfolgen werden auf fehlende Rechnungen, doppelte Belege und fehlende Dateien geprueft, Kundenordner zeigen neue Excel-Dateien mit Nummer/Datum/Mengenzeilen, typische Mengen enthalten letzte Menge/Spanne/Haeufigkeit, Kundenpreis-Abweichungen landen im Arbeits-Cockpit und der Import zeigt eine Sicherheitsgruppe fuer neu/geaendert/unsicher/uebersprungen. Volle Regression 265 Tests und `compileall src tests` erfolgreich.
- Bestellfenster vereinfacht: Der Erfassungsbereich nutzt keinen Zwei-Spalten-Splitter mehr, sondern einen linearen Ablauf mit `Bisher bestellt` und `Aktuelle Bestellung`; bei Kundenauswahl werden bekannte Kundenartikel automatisch als editierbare Vorschlagspositionen uebernommen, inklusive Menge 0 als sichtbarer Platzhalter. Volle Regression 267 Tests und `compileall src tests` erfolgreich.
- Fehler behoben: Wenn ein Kunde kein importiertes Kundensortiment hat, aber alte Bestellungen vorhanden sind, wird `Bisher bestellt` jetzt sichtbar aus der letzten Bestellung befuellt; vorher wurde nur die aktuelle Bestellung vorbefuellt und der Vorschlagsbereich blieb leer. Volle Regression 267 Tests und `compileall src tests` erfolgreich.
- A11y-/UX-Audit umgesetzt: Bestellaufnahme nutzt jetzt eine einzige sichtbare Mengenliste mit einklappbarem Zusatzartikel-Bereich, Belegdialoge haben einen dauerhaft sichtbaren Excel+PDF-Abschlussbereich, Pruefpunkte wurden auf Liste + Detail-Inspector mit kontextabhaengigen Aktionen umgebaut, Belegarchiv nutzt eine gemeinsame Belegliste mit Filter, Kundenakte trennt Uebersicht/Bestellungen/Dateien und Rechnungen fokussiert Kassenarbeit mit Nebenlisten. Volle Regression 267 Tests, `compileall src tests` und Offscreen-Start des Hauptfensters erfolgreich.
- Kundenansicht repariert und weiter vereinfacht: `Letzte Mengen` nutzt jetzt ebenfalls den Fallback auf die letzte Bestellung, wenn kein Kundensortiment vorhanden ist. Die Kundenansicht fuehrt klarer mit `Kunde suchen -> Letzte Mengen pruefen -> Neue Bestellung starten`, bleibt automatisch auf der Uebersicht und formuliert leere Zustaende selbsterklaerend. Volle Regression 269 Tests und `compileall src tests` erfolgreich.
- Globaler App-Header entfernt: Die obere Toolbar mit Logo, grober Suche, Neu/Aktualisieren und Hilfe war nicht selbsterklaerend und wurde zugunsten von Sidebar plus klaren Seitenkoepfen entfernt. Volle Regression 269 Tests, `compileall src tests` und Offscreen-Start des Hauptfensters erfolgreich.
- Visueller Detail-Polish nach Screenshot-Review: Kunden-Inspector kuerzt den naechsten Schritt und gibt ihm eine lesbare Hinweisflaeche, Zusatzartikel in Bestellungen nutzt statt Checkbox-GroupBox einen klaren Aufklapp-Button, Summenzeilen haben feste Hoehe und Abstand, Rechnungsaktionen sind kompakt nebeneinander und Buttontexte gekuerzt. Volle Regression 271 Tests, `compileall src tests` und Offscreen-Start erfolgreich.
- Bestellpositionen haben jetzt ein Kontextmenue: Rechtsklick auf eine Zeile in der Mengenliste kann die Position in die aktuelle neue Bestellung uebernehmen/kopieren oder entfernen; Produkt-ID, Menge, Preis und Pfand bleiben erhalten und die Summe wird neu berechnet. Volle Regression 273 Tests und `compileall src tests` erfolgreich.
- Artikelauswahl beim manuellen Hinzufuegen verbessert: Die Produktliste zeigt bei ausgewaehltem Kunden zuerst `Empfohlen fuer diesen Kunden` aus den bisherigen Kundenartikeln und darunter `Alle Artikel` ohne Dubletten; die Suche filtert beide Gruppen gemeinsam. Volle Regression 275 Tests und `compileall src tests` erfolgreich.
- Artikelauswahl nachgeschliffen: Gruppenueberschriften wie `Empfohlen fuer diesen Kunden` und `Alle Artikel` sind jetzt kleine fette Trenner und technisch nicht mehr auswaehlbar; Klicks auf Trenner schreiben keinen Text mehr ins Suchfeld. Volle Regression 276 Tests und `compileall src tests` erfolgreich.
- Stammdaten-Performance nachgemessen und verbessert: Kunden/Artikel/Pruefpunkte laden nicht mehr beim App-Start und werden beim erneuten Oeffnen nicht wieder komplett aufgebaut; grosser Tabellenaufbau pausiert Repaints. Messung mit echter DB-Kopie: Start ca. 650 ms -> 329 ms, erneutes Stammdaten-Oeffnen ca. 74 ms -> 6 ms. Volle Regression 279 Tests und `compileall src tests` erfolgreich.
- UAT-Fehler aus sichtbarem 60+-Test behoben: Nach Speichern/Neuladen wird die aktuell bearbeitete Bestellung im Bestellstapel wieder markiert, damit Lieferschein/Rechnung nicht versehentlich fuer eine alte Tabellenzeile erzeugt werden. Manuelles Artikel-Hinzufuegen leert danach den Produktpicker, Menge, Preis und Pfand, sodass der naechste Artikel wieder direkt per Maus aus der Vorschlagsliste gewaehlt werden kann. Volle Regression 281 Tests erfolgreich.
- PRD-Meilenstein 1 begonnen: Die Hauptnavigation zeigt jetzt nur noch `Arbeiten`, `Rechnungen` und `Verwaltung`. `Heute` und `Kunden` liegen intern unter `Arbeiten`, das Belegarchiv liegt unter `Verwaltung`; Rechnungen/offene Posten bleiben direkt erreichbar. Volle Regression 281 Tests und `compileall src tests` erfolgreich.
- `Arbeiten` hat eine neue Startfläche: links Kundensuche/Bestellaufnahme, rechts offene Lieferschein-Rückläufe aus Bestellungen mit erzeugtem Lieferschein und noch ohne Rechnung. Rückläufe können von dort direkt in den bestehenden Rechnungsdialog geöffnet werden; leere Zustände erklären den nächsten Schritt. Volle Regression 284 Tests und `compileall src tests` erfolgreich.
- Kundenfokus in `Arbeiten` nachgeschärft: Im Kunden-Inspector stehen jetzt neben Adresse, Kontakt, Zahlart, Lieferhinweisen, letzten Mengen und Bestellungen auch kompakte Rechnungswarnungen für offene, fällige und überfällige Posten. Volle Regression 285 Tests und `compileall src tests` erfolgreich.
- Bestellaufnahme ist jetzt inline in `Arbeiten`: `Neue Bestellung starten`, bestehende Bestellungen und Belegaktionen wechseln in den internen Tab `Bestellung`, ohne einen alten Top-Level-Bereich `Bestellungen` zu brauchen. Die vorhandene Erfassung mit empfohlenen Artikeln, 0-Mengen, Pfand-Rückgabe und Lieferschein/Rechnung bleibt erhalten. Volle Regression 286 Tests und `compileall src tests` erfolgreich.
- PRD-Meilenstein 2 umgesetzt: Sofort-Rechnung muss jetzt bewusst bestätigt werden und erklärt, dass sie den Rücklauf überspringt. Offene Lieferschein-Rückläufe öffnen in `Arbeiten` eine eigene Rücklauf-Werkstatt, in der Mengen und Pfand-Rückgabe geprüft und daraus die Rechnung erstellt wird. Ein kompletter Service-UAT deckt Bestellung -> Lieferschein -> Rücklauf -> Mengen/Pfand anpassen -> Rechnung -> offene Rechnung ab; Rücklauf-Sprache und Hauptbutton wurden gezielt poliert. Volle Regression 290 Tests und `compileall src tests` erfolgreich.
- UI-Grill-Ergebnis als Design festgehalten und erste Redesign-Scheibe umgesetzt: `Arbeiten` zeigt keine sichtbaren Workflow-Tabs `Start/Heute/Kunden/Bestellung/Rücklauf` mehr, sondern nutzt intern einen Zustands-Stack. Die Startfläche hat jetzt eine echte Kundensuche plus offene Rückläufe statt nur eines Such-Buttons oder Dashboards. Volle Regression 290 Tests und `compileall src tests` erfolgreich.
- `Heute`/Dashboard ist aus dem `Arbeiten`-Startfluss entfernt. `MainWindow` verdrahtet den täglichen Arbeitsstart jetzt direkt über Kundensuche und Rückläufe; alte Dashboard-Signale hängen nicht mehr als versteckter Workflow-Einstieg im Shell. Volle Regression 290 Tests und `compileall src tests` erfolgreich.
- Fenster- und Abstandsprobleme im neuen `Arbeiten`-Start behoben: Die Startfläche nutzt keine stretchende Standard-Card mehr, Kundensuche und Rückläufe bleiben oben kompakt ausgerichtet, die App startet größer und die Kundenordner-Zeile in der Verwaltung schrumpft sauber statt Buttons abzuschneiden. Volle Regression 291 Tests erfolgreich.
- `Arbeiten`-Start optisch nachgeschliffen: Kundensuche und Rückläufe stehen jetzt als vertikaler Arbeitsfluss statt gequetschter Zweispaltenfläche, Suchlisten wachsen nicht mehr leer in die Höhe, Sekundäraktionen sind kompakt und leere Rückläufe zeigen keinen deaktivierten Balken mehr. Visueller Offscreen-Preview geprüft; volle Regression 291 Tests und `compileall src tests` erfolgreich.
- Verwaltung entschlackt und sichtbare Texte bereinigt: `Verwaltung` startet jetzt mit einer ruhigen Einstiegsseite statt sichtbaren Admin-Tabs; Kunden, Artikel, Prüfpunkte, Import und Belegarchiv liegen als klare Routen dahinter. Sichtbare UI-Texte wurden systematisch von `ae/oe/ue` auf echte Umlaute umgestellt. Bürofluss-Test Bestellung -> Lieferschein -> Rücklauf -> Rechnung ist grün; volle Regression 292 Tests und `compileall src tests` erfolgreich.
- Bestellaufnahme als fokussierte Ein-Aufgabe-Seite umgebaut: Der sichtbare Bestellstapel ist aus der Erfassung entfernt, alte Bestellungen liegen nun im Kundenbereich unter `Frühere Bestellungen` und können von dort geöffnet werden. Die Bestellseite führt jetzt von Kundendaten über Mengenliste/Pfand zu einem klaren Abschluss `Speichern -> Lieferschein`; Zusatzartikel ist nur noch eine kleine Nebenaktion. Tabellen- und Buttonbreiten wurden für 1440px visuell geprüft. Volle Regression 293 Tests und `compileall src tests` erfolgreich.
- Rückweg in `Arbeiten` ergänzt: Kundenansicht, Bestellaufnahme und Rücklauf-Werkstatt haben jetzt `Zurück zur Übersicht` und führen wieder auf die Startfläche mit Kundensuche und offenen Lieferschein-Rückläufen. Offscreen-Smoke für Kunde -> Übersicht und Bestellung -> Übersicht erfolgreich; 118 fokussierte UI-Tests und `compileall src tests` erfolgreich.
- Rückweg-Button repariert: `QPushButton.clicked` wird nun per Lambda auf argumentlose Navigationssignale weitergeleitet, damit der sichtbare Button wirklich klickt. Der Fehler betraf Kundenansicht, Bestellaufnahme, Rücklauf-Werkstatt und den Startflächen-Button `Alle Kunden öffnen`. Echte Button-Klicktests und Offscreen-Smoke erfolgreich; 119 fokussierte UI-Tests und `compileall src tests` grün.
- Bürofluss-Polish umgesetzt: Der Excel-Import blockiert jetzt bei fehlenden Pflichtdateien statt unvollständige Daten still zu übernehmen; die Verwaltungsroute und Seite heißen einheitlich `Excel-Import`. Kunden- und Produktpflege erklären die drei wichtigsten Schritte direkt in der Seite, Archiv und Prüfpunkte haben klare Leerzustände. Sichtbarer Smoke lief bis zur Lieferschein-Belegwerkstatt; Kunde, Vorbefüllung, Menge-0-Positionen, Nummernvorschlag und Speichern wurden im laufenden Fenster geprüft. Der Mac-Computer-Use-Dienst brach beim finalen Belegerzeugungs-Klick ab, während der App-Prozess weiterlief; die fachliche Belegerzeugung bleibt durch Regressionstests abgedeckt.
- Eigenständige Startseite ergänzt: `Start` zeigt Kundenauswahl und offene Lieferschein-Rückläufe, während `Arbeiten` erst nach Auswahl eines Kunden den Kundenarbeitsplatz zeigt. Das Zurückspringen nach `Arbeiten` beim Klick auf `Start` war eine erneute Auswahlmeldung der Suchliste; die Startseite leert die Auswahl beim Aktualisieren gezielt. Ein Regressionstest deckt Kunde auswählen -> `Start` wählen ab; 122 fokussierte UI-Tests sind grün.
- Kundenarbeitsplatz vereinfacht: Der technische Button `Liste aktualisieren` ist entfernt. Kunden werden beim Öffnen der Startseite und beim Wechsel automatisch geladen; 70 Tests für Kundenansicht und Hauptfenster sind grün.
- Datenintegritäts- und Arbeitsfluss-Checkpoint abgeschlossen: Die Kundenpflege führt importierte Telefon-, Kontakt-, E-Mail-, Zahlart-, Öffnungszeiten- und interne Notizdaten verlustfrei mit; eindeutige Suchtreffer öffnen erst nach Klick oder Enter; Excel-Import, Kundenordner-Laden und Belegerzeugung laufen über einen gemeinsamen Qt-Hintergrundtask; im Belegworkflow kann die Bestellung sichtbar und vollständig zurückgesetzt werden; alle App-Buttons besitzen verbindliche semantische Rollen. Abschlussnachweis: 326 Tests bestanden, `compileall src tests` erfolgreich und isolierter Offscreen-Anwender-Smoke für Kundensuche, asynchrones Laden, Kundenänderung und Bestellwechsel erfolgreich.

## In Arbeit

- Echten Windows-Kundenordner fuer den naechsten Anwender-Smoke vorbereiten.
- Excel-Fortschreibung im naechsten UAT mit echten Kundenordnern visuell gegen Originalausdruck pruefen.
- Git-Worktree-Verknüpfung ist repariert; der Datenintegritäts- und Arbeitsfluss-Checkpoint ist fachlich, technisch und visuell geprüft.

## Offen

- Importlauf mit einem echten kompletten Windows-Kundenordner testen.
- Offene Posten, Tagesliste und spaetere Windows-Verpackung.
- Startbildschirm mit Kennzahlen: heutige Lieferungen, offene Posten, faellige Kontakte.
- Tagesliste fuer Fahrer mit Adresse, Zeitfenster und Kundenhinweisen.
- Kontakt-/Wiedervorlage ohne Kunden, die sich selbst melden.
- Auswertung fuer Stopps, Mengen und Umsatz mit Excel-Export.

## Naechste Aufgabe

Den Office-2.0-Bürofluss auf einem Windows-Zielsystem mit echter Kundenordner-Vorlage visuell prüfen. EXE-Paketierung und Windows-Export bleiben bis zu diesem späteren Meilenstein ausdrücklich ausgenommen.
