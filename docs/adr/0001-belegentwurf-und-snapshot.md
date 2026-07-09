# ADR 0001: Belegentwurf und Snapshot sind getrennte fachliche Zustaende

## Kontext

Die bisherige Kunden-Excel diente zugleich als Vorlage und Preisquelle. Kuenftig soll der Artikelstamm Preis und Pfand zentral vorgeben, waehrend erzeugte Rechnungen reproduzierbar bleiben muessen.

## Entscheidung

Eine Bestellung ist mengenorientiert. Ein Belegentwurf liest Preis und Pfand aus dem zentralen Artikelstamm und darf diese Werte vor dem Finalisieren einmalig pro Position aendern. Beim Finalisieren wird ein unveraenderlicher Beleg-Snapshot gespeichert. Excel- und PDF-Ausgaben sowie deren Neuerzeugung verwenden ausschliesslich diesen Snapshot.

## Folgen

- Preis- und Pfandaenderungen im Artikelstamm wirken auf noch nicht finalisierte Entwuerfe.
- Einmalige Abweichungen veraendern weder den Artikelstamm noch andere Belege.
- Eine nachtraeglich bearbeitete Excel-Datei ist keine Quelle fuer eine neue verbindliche PDF.
