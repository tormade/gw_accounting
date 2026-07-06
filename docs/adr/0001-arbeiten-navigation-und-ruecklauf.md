# ADR 0001: Arbeiten-Navigation und Rücklaufprozess

## Status

Angenommen

## Kontext

Die Anwendung war bisher funktionsorientiert aufgebaut. Sichtbare Hauptbereiche waren unter anderem `Heute`, `Kunden`, `Bestellungen`, `Belege`, `Rechnungen` und `Stammdaten`.

Der primäre Nutzer ist jedoch der Büro-/Thekennutzer, der telefonisch Bestellungen aufnimmt, Lieferscheine erzeugt, zurückgekommene Papier-Lieferscheine bearbeitet und daraus Rechnungen erstellt. Eine funktionsorientierte Navigation zwingt diesen Nutzer, die interne Struktur der Software zu verstehen.

Zusätzlich soll die App nach erfolgreichem Import die operative Wahrheit sein. Excel und PDF bleiben Ausgabe und Nachweis, aber nicht mehr der laufende Arbeitsort.

## Entscheidung

Die Hauptnavigation wird auf drei Bereiche reduziert:

- `Arbeiten`
- `Rechnungen`
- `Verwaltung`

`Arbeiten` wird der primäre Tagesarbeitsplatz. Der erste Bildschirm zeigt zwei Aufgaben:

- Kundensuche / Bestellung aufnehmen
- offene Lieferschein-Rückläufe

Nach Kundenauswahl fokussiert `Arbeiten` auf den Kundenkontext. Nach Auswahl eines offenen Rücklaufs fokussiert `Arbeiten` auf die Rücklaufbearbeitung.

`Bestellungen` und `Belege` sind keine Hauptbereiche mehr. Bestellungen erscheinen im Kundenkontext; Belege erscheinen bei Bestellung, Kunde, Rechnung oder im Adminbereich.

Nach Lieferschein-Erstellung entsteht automatisch der Status `Rücklauf offen`. Die Rücklaufbearbeitung bleibt einfach: Mengen und Pfand-Rückgaben werden direkt angepasst, anschließend wird die Rechnung erstellt. `Mengen final` wird beim Rechnungserstellen aus dem Rücklauf automatisch gesetzt.

Eine Sofort-Rechnung bleibt möglich, ist aber sekundär zur Standardaktion `Lieferschein erstellen` und muss bewusst bestätigt werden. Sie überspringt `Rücklauf offen`.

## Konsequenzen

- Der Alltag beginnt nicht mehr in einem Dashboard, sondern im Bereich `Arbeiten`.
- `Heute`, `Kunden`, `Bestellungen` und `Belege` werden in den neuen Arbeitsfluss integriert oder in `Verwaltung` zurückgestuft.
- `Rechnungen` ist primär Kassen-/Offene-Posten-Arbeitsplatz.
- `Verwaltung` bündelt Kundenstamm, Artikelstamm, Import, Prüfpunkte, Belegarchiv und Einstellungen.
- Die UI darf radikal umgebaut werden, aber Kernlogik, Exportlogik und Belegberechnung bleiben stabil und werden nur gezielt erweitert.
- Sichtbare deutsche Texte verwenden echte Umlaute; technische Bezeichner können aus Stabilitätsgründen ASCII bleiben.

## Nicht-Ziele

- Keine neue Fahrer-App.
- Keine komplette Neuschreibung der Kern- oder Exportlogik.
- Keine große neue Tourenplanung.
- Keine Umstellung von Excel/PDF als Ausgabeformaten.
