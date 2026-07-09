# Stabilitaet und Fluessigkeit – Design

## Ziel

Die Desktop-Anwendung soll waehrend der Entwicklung robuster und bei langen
Dateioperationen fluessig bleiben. Ein Windows-EXE-Build ist nicht Teil dieses
Schritts. Die betroffenen Grundlagen werden jedoch so gestaltet, dass sie spaeter
ohne erneuten Umbau paketierbar sind.

## Umfang

1. Ressourcen- und Datenpfade werden zentral aufgeloest. Die Anwendung darf nicht
   von ihrem aktuellen Arbeitsverzeichnis abhaengen.
2. Belegdateinamen werden auf Windows-kompatible Namen normalisiert.
3. Belegerzeugung veroeffentlicht Dateien erst, wenn Excel- und PDF-Erzeugung
   vollstaendig erfolgreich waren. Bei Fehlern bleiben keine neu erzeugten
   Enddateien zurueck.
4. Fehler beim Starten der Datenbank werden als fachlich verstaendliche
   `ApplicationStartupError`-Ausnahme bereitgestellt; die UI zeigt sie als Dialog.
5. Excel-Import, Kundenordner-Onboarding sowie Belegerzeugung laufen ausserhalb
   des Qt-GUI-Threads. Die Oberflaeche zeigt einen laufenden Zustand, verhindert
   doppelte Ausfuehrungen und meldet Erfolg oder Fehler im vorhandenen Stil.

## Architektur

### Pfade und Ressourcen

`resources.py` stellt eine kleine Schnittstelle bereit:

- `application_data_dir()` fuer beschreibbare Anwendungsdaten;
- `resource_path(*parts)` fuer mitgelieferte Vorlagen und Markenassets;
- `development_default_dir(*parts)` fuer sinnvolle, vom Installationsort
  unabhaengige Vorschlagswerte in der Entwicklungsumgebung.

Der Code verwendet diese Funktionen anstelle von `Path.cwd()` und verstreuten
`__file__.parents[...]`-Berechnungen. Das ist in der Entwicklung voll testbar und
beruecksichtigt spaeter eine PyInstaller-Umgebung, ohne jetzt einen Build zu
erzeugen.

### Fehlergrenzen und Datenkonsistenz

`bootstrap_database()` faengt technische Datenbank- und Dateisystemfehler ab und
uebersetzt sie in `ApplicationStartupError`. `main()` faengt diese Ausnahme ab,
zeigt einen kurzen Dialog und beendet die Anwendung geordnet.

Die Belegerzeugung schreibt Excel und PDF zunaechst in eindeutige temporaere
Dateien im Zielordner. Erst wenn beide Operationen gelungen sind, werden die
Dateien auf ihre Endnamen verschoben und die Datenbanktransaktion bestaetigt.
Bei einem Fehler werden nur in diesem Aufruf erzeugte temporaere oder Enddateien
entfernt; bestehende Dokumente werden nie geloescht.

### Hintergrundarbeit

Ein wiederverwendbarer Qt-Worker kapselt eine parameterlose fachliche Funktion.
Er laeuft in einem `QThread` und liefert entweder ein Ergebnis oder die
aufbereitete Ausnahme zurueck. Die Panels besitzen jeweils hoechstens einen
laufenden Worker. Waehrenddessen sind die ausloesenden Aktionen deaktiviert und
eine Statusmeldung informiert ueber den Vorgang. Nach Abschluss werden Controls
wieder aktiviert, Sessions geschlossen und die bestehenden Erfolgs- bzw.
Fehlermeldungen aktualisiert.

Das Fachverhalten bleibt in Services. UI-Code erzeugt nur den Worker und
uebersetzt sein Ergebnis in sichtbaren Zustand.

## Fehlerbehandlung

- Windows-unzulaessige Zeichen, Steuerzeichen, reservierte Geraetenamen sowie
  problematische abschliessende Leerzeichen/Punkte werden neutralisiert.
- Fehler in Import, Onboarding und Dokumenterzeugung werden im Status und als
  Dialog sichtbar, statt ungefangen den Qt-Event-Loop zu verlassen.
- Ein Fehler beim Belegexport erzeugt keine neue, falsche Datenbankreferenz und
  keine teilweise neu erstellte Enddatei.

## Tests

- Unit-Tests fuer Ressourcenpfade und Windows-Dateinamen.
- Regressionstests fuer den atomaren Erfolg sowie Fehler nach Excel- oder
  PDF-Erzeugung.
- Tests fuer die Startfehler-Uebersetzung.
- Headless-Qt-Tests fuer Worker-Erfolg, Worker-Fehler und das Deaktivieren bzw.
  Wiederaktivieren der ausloesenden UI-Aktionen.
- Vollstaendiger bestehender Testlauf bleibt gruener Mindeststandard.

## Nicht im Umfang

- Erstellung oder Verteilung einer Windows-EXE.
- Netzlaufwerk-/Mehrbenutzerunterstuetzung fuer SQLite.
- Vollstaendiger Ersatz aller bestehenden Services durch Adapter.
- Fortschrittsprozente innerhalb von `openpyxl` oder ReportLab; die UI meldet
  stattdessen klar den laufenden Arbeitsschritt.
