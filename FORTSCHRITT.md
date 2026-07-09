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
- Mac-Oberflaechentest "aus alter Bestellung weiterarbeiten" durchgefuehrt: Cafe Nord, alte Bestellung AUF-1040 kopiert, Menge von 9 auf 10 geaendert und als neue Bestellung COPY-UI-230623-2 gespeichert.
- Lieferschein aus der kopierten Bestellung ueber die Oberflaeche erzeugt: `Kunden/Cafe Nord/2026-06-23_LS_LS-COPY-UI-230623-2_Cafe_Nord.xlsx` und `.pdf`.
- Rechnung aus derselben kopierten Bestellung fachlich erzeugt und Dateien verifiziert: `Kunden/Cafe Nord/2026-06-23_RE_RE-COPY-UI-230623-2_Cafe_Nord.xlsx` und `.pdf`.
- UI-Befund aus dem 60+-Erstnutzer-Test umgesetzt: Aktionen zur markierten Bestellung stehen jetzt direkt bei der Bestellliste, Texte sind kuerzer und der Kundenordner erklaert den Ablauf als Kunde -> alte Bestellung -> Beleg.
- Nach dem Schliessen eines Rechnung-/Lieferschein-Dialogs wird die Kundenakte automatisch neu geladen, damit neue Dateien sofort sichtbar werden.
- Mac/Qt-Accessibility-Crash beim Computer-Use-Lesen einer grossen PySide-Oberflaeche dokumentiert; fachlich erzeugte Dateien sind vorhanden, der finale Rechnungsklick sollte im naechsten echten UI-Lauf nochmals ohne Accessibility-Abfrage geprueft werden.
- Kundensortiment lernt jetzt automatisch aus gespeicherten Bestellungen: pro Kunde werden zuletzt bestellte Menge, letztes Lieferdatum, Bestellhaeufigkeit, Gesamtmenge und ein Verlaufshinweis berechnet.
- Kundenordner und Bestelldialog zeigen die gelernte Verlaufsliste als Verkaufshilfe, damit beim Telefonat schnell sichtbar ist, was der Kunde frueher hatte und was sich als neue Bestellung anbietet.
- Mac-Oberflaechentest fuer Telefon-/Folgebestellung erfolgreich durchgespielt: Cafe Nord gesucht, gelernte letzte Mengen geprueft, Bestellung TEST-FLOW-240624-1 aus letzten Mengen gestartet, Wasser von 10 auf 4 geaendert und gespeichert.
- Aus TEST-FLOW-240624-1 wurden ueber die echte Oberflaeche Lieferschein LS-FLOW-240624-1 und Rechnung RE-FLOW-240624-1 jeweils als Excel und PDF erzeugt.
- Datei-Check bestaetigt: alle vier Artefakte liegen im Kundenordner, beide Excel-Dateien enthalten Wasser mit Menge 4 und Summenformeln.
- Auftragsnummern werden intern automatisch vergeben und sind im Bestellformular nicht mehr vom Anwender zu pflegen.
- Bestellungen koennen aus der Liste heraus geloescht werden; vor dem Ausblenden erscheint eine Ja/Nein-Bestaetigung, auch bei bereits verwendeten Bestellungen.
- Pruefliste ist aus Startseite und Hauptnavigation entfernt; Import-/Pruefservices bleiben fuer spaetere Nutzung im Hintergrund erhalten.
- Beleg-Dateinamen vermeiden doppelte Praefixe: aus `LS-FLOW-...` wird nicht mehr `LS_LS-FLOW-...`, aus `RE-FLOW-...` nicht mehr `RE_RE-FLOW-...`.
- Kundenordner-Aktionen sind in ruhigere Aktionsgruppen getrennt; markierte Bestellungen koennen jetzt direkt geoeffnet, kopiert, fakturiert oder geloescht werden.
- Belegpositionen und Pfandruecknahmen werden beim Erstellen von Rechnung/Lieferschein als Snapshot gespeichert, damit erzeugte Belege spaeter reproduzierbarer werden.
- Nach dem Speichern einer Bestellung aktualisiert der Kundenordner die Kundenakte und markiert die neue Bestellung automatisch fuer den naechsten Schritt.
- Eindeutige Suchtreffer lassen die Trefferliste eingeklappt; nur Mehrfachtreffer bleiben sichtbar. Das reduziert UI-Unruhe und vermeidet grosse Accessibility-Baeume auf macOS.
- Crashreport vom Mac-Oberflaechentest analysiert: Absturz liegt in Qt/macOS Accessibility (`libqcocoa`) beim Computer-Use-Auslesen, nicht in einer Python-Exception; Workflow wurde ueber Tests und Datenbank verifiziert.
- Startfenster startet groesser (1360x860) und bleibt dennoch verkleinerbar (Mindestgroesse 1024x640), damit die wichtigsten Arbeitsbereiche direkt sichtbar sind.
- Belegexport prueft freie Rechnungs-/Lieferscheinnummern vor dem Export und zeigt eine einfache Anwenderwarnung statt technischer Pydantic-/Service-Fehler.
- Mac-Oberflaechentest erfolgreich wiederholt: Cafe Nord gesucht, Bestellung AUF-001057 aus letzten Mengen gespeichert und Lieferschein LS-UI-240624-FINAL ueber die UI als Excel und PDF erzeugt.
- Datei-Check bestaetigt: `Kunden/Cafe Nord/2026-06-24_LS-UI-240624-FINAL_Cafe_Nord.xlsx` und `.pdf` liegen im Kundenordner; Dateinamen enthalten kein doppeltes LS-Praefix.
- Kundenordner rendert lange Datei- und Bestelllisten kompakter: sichtbar sind die neuesten Dateien/Bestellungen, die Gesamtzahl bleibt im Status und der echte Ordner bleibt voll erreichbar.
- Mac-Oberflaechentest fuer Rechnung erfolgreich wiederholt: Cafe Nord gesucht, Bestellung AUF-001058 aus letzten Mengen gespeichert und Rechnung RE-UI-240624-FINAL ueber die UI als Excel und PDF erzeugt.
- Datei-Check bestaetigt: `Kunden/Cafe Nord/2026-06-24_RE-UI-240624-FINAL_Cafe_Nord.xlsx` und `.pdf` liegen im Kundenordner; Dateinamen enthalten kein doppeltes RE-Praefix.
- Neuer Crashreport aus VS Code analysiert: wieder Qt/macOS Accessibility (`libqcocoa`), daher bleibt die UI-Haertung gegen grosse Accessibility-Baeume ein wichtiger Arbeitsstrang.
- Kundenordner-Import nutzt pro Kunde nur noch die fachlich neueste Excel-Belegdatei als letzte Menge; aeltere Dateien werden nachvollziehbar uebersprungen statt das Sortiment zurueckzusetzen.
- Windows-/Office-Sperrdateien wie `~$...xlsx` werden beim Kundenordner-Import ignoriert und nicht als defekte Belege gezaehlt.
- Einstellungen haben jetzt einen eigenen Bereich "Kundenordner einlesen", der die Lieferkundenliste aus dem Input-Ordner nutzt und echte Kundenordner-Excel in Sortiment und Pruefpunkte uebernimmt.
- Startseite repariert: Aktionskarten druecken ihre Buttons nicht mehr durch leeren Raum nach unten, sondern bleiben kompakt und oben ausgerichtet.
- Kundenordner-/Datei-Oeffnen aus der App gehaertet: Wenn Qt/Finder den Pfad nicht direkt oeffnet, versucht die App einen System-Fallback und zeigt eine Statusmeldung statt still nichts zu tun.
- Kundenauswahl wieder listenartig gemacht: Bei leerem Suchfeld bleibt die Kundenliste sichtbar und scrollbar, Tippen filtert die Liste, echte Auswahl erfolgt per Klick/Enter und wird mit "Ausgewaehlt: ..." bestaetigt.
- Pruefpunkte bleiben aus der Hauptnavigation heraus, koennen aber nach Stammdaten-/Kundenordnerimport direkt in den Einstellungen ueber "Pruefpunkte ansehen" als Dialog bearbeitet werden.
- Demo-Testfall fuer die Pruefliste erstellt: `Demo_Pruefliste/Input` enthaelt zentrale Stammdaten, `Demo_Pruefliste/Kundenordner` enthaelt bewusst widerspruechliche Kundenordnerdateien.
- Import-Smoke bestaetigt: 2 Demo-Kunden, 6 Sortimentszeilen, 10 offene Pruefpunkte sowie je eine alte Datei und eine Excel-Sperrdatei als uebersprungen.
- Pruefliste ueber Mac-Oberflaeche mit Demo-Daten geprueft: Einstellungen-Import erzeugt 10 Pruefpunkte, der Dialog zeigt Preisabweichungen, Artikelzuordnungen und Kundendaten-Konflikte.
- UI-Fund aus dem Prueflisten-Test umgesetzt: Artikelsuche spricht jetzt von `Artikelliste`, Kundendaten-Konflikte zeigen kein technisches `merge_conflict` mehr und Tabellenzellen haben besser lesbare Breiten mit Tooltips.

## In Arbeit

- Kundenordner-Import mit einem echten kompletten Windows-Datenbestand praktisch testen und die Treffer-/Konfliktqualitaet schaerfen.

## Offen

- Importlauf mit einem echten kompletten Windows-Kundenordner auf dem Firmenrechner testen.
- Offene Posten, Tagesliste und spaetere Windows-Verpackung.
- Startbildschirm mit Kennzahlen: heutige Lieferungen, offene Posten, faellige Kontakte.
- Tagesliste fuer Fahrer mit Adresse, Zeitfenster und Kundenhinweisen.
- Kontakt-/Wiedervorlage ohne Kunden, die sich selbst melden.
- Auswertung fuer Stopps, Mengen und Umsatz mit Excel-Export.

## Naechste Aufgabe

Echten Windows-Kundenordner importieren, Ergebnis mit Sachbearbeiter pruefen und die offenen Prueffaelle in einfache Entscheidungen uebersetzen.
