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

## In Arbeit

- Kundenordner-Arbeitsplatz weiter abrunden und Beleg-Snapshots/Adapter schrittweise aus den alten Services trennen.

## Offen

- Importlauf mit einem echten kompletten Windows-Kundenordner testen.
- Belegpositionen langfristig als eigenen Snapshot persistieren, damit alte Belege voll reproduzierbar bleiben.
- Offene Posten, Tagesliste und spaetere Windows-Verpackung.
- Startbildschirm mit Kennzahlen: heutige Lieferungen, offene Posten, faellige Kontakte.
- Tagesliste fuer Fahrer mit Adresse, Zeitfenster und Kundenhinweisen.
- Kontakt-/Wiedervorlage ohne Kunden, die sich selbst melden.
- Auswertung fuer Stopps, Mengen und Umsatz mit Excel-Export.

## Naechste Aufgabe

Beleg-Snapshot-Datenmodell und Adapter-Grenze vorbereiten, danach Bedienprobe mit einem echten kompletten Kundenordner durchspielen.
