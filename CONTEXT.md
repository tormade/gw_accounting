# Kontext: Getränke Winklmeier Büro-Werkzeug

## Glossar

### Operative Wahrheit

Die App ist nach erfolgreichem Import der Arbeitsort für Bestellung, Lieferschein, Rücklauf, Rechnung und Zahlung. Excel- und PDF-Dateien sind Ausgabe und Nachweis, aber nicht mehr der laufende Arbeitsort.

### Büro-/Thekennutzer

Die primäre Nutzerrolle. Diese Person nimmt telefonisch Bestellungen auf, erzeugt Lieferscheine, bearbeitet zurückgekommene Lieferscheine und erstellt Rechnungen.

### Arbeiten

Der primäre Tagesarbeitsplatz der App. Er bündelt Kundensuche, Bestellaufnahme und offene Lieferschein-Rückläufe.

Der erste Bildschirm zeigt zwei gleichwertig erkennbare Aufgaben: Kundensuche/Bestellung aufnehmen und offene Lieferschein-Rückläufe. Auf Desktop stehen sie nebeneinander, auf kleineren Bildschirmen untereinander.

Nach der Kundenauswahl fokussiert `Arbeiten` auf den ausgewählten Kunden. Die Rücklaufsliste tritt zurück, damit Kundendaten, Warnhinweise, neue Bestellung, empfohlene Artikel und letzte Bestellungen ohne parallele Ablenkung bearbeitet werden können.

Nach Auswahl eines offenen Rücklaufs fokussiert `Arbeiten` auf genau diesen Rücklauf. Sichtbar sind Kunde, Lieferscheinnummer, einfache Mengenliste, Pfand-Rückgabe und die Aktion `Rechnung erstellen`. Nach Rechnungserstellung kehrt der Nutzer zur Rücklaufliste zurück.

### Hauptnavigation

Die sichtbare Hauptnavigation besteht aus genau drei Bereichen: `Arbeiten`, `Rechnungen` und `Verwaltung`. Frühere Hauptbereiche wie `Heute`, `Kunden`, `Bestellungen` und `Belege` werden in diese drei Bereiche integriert oder als Admin-/Kontextfunktionen zurückgestuft.

### Rücklauf offen

Status für eine Bestellung, zu der ein Lieferschein erzeugt wurde und deren Rücklaufbearbeitung noch aussteht. Der Status entsteht automatisch nach der Lieferschein-Erstellung. Er bedeutet nicht zwingend, dass der Papier-Lieferschein physisch schon im Bürofach liegt, sondern dass dieser Vorgang vor der sicheren Rechnungsstellung noch bearbeitet werden muss. In diesem Status werden Mengen und Pfand-Rückgaben geprüft oder angepasst.

### Mengen final

Status nach der Rücklaufbearbeitung. Die gelieferten Mengen und Pfand-Rückgaben gelten als geprüft. Im Alltag wird dieser Status nicht über einen eigenen Button gesetzt, sondern automatisch beim Erstellen der Rechnung aus dem Rücklauf.

### Sofort-Rechnung

Eine Rechnung kann direkt nach dem Speichern einer Bestellung erstellt werden, wenn Mengen und Pfand-Rückgabe bereits final sind. Diese Aktion bleibt sichtbar, ist aber sekundär zur Standardaktion `Lieferschein erstellen` und muss bewusst bestätigt werden. Bei einer Sofort-Rechnung wird `Rücklauf offen` komplett übersprungen; der Vorgang wird direkt als final und abgerechnet behandelt.

### Sichtbarer Status

Statusangaben in der Oberfläche verwenden Alltagssprache statt technischer Statuswerte. Sichtbar sind Begriffe wie `Bestellung aufgenommen`, `Lieferschein erstellt`, `Rücklauf offen`, `Mengen final`, `Rechnung erstellt` und `Bezahlt`. Interne Statuswerte dürfen aus Stabilitätsgründen technisch und ASCII bleiben.

### Pfand-Rückgabe

Leergut, das der Kunde zurückgibt. Pfand-Rückgaben werden separat von Artikelpfand erfasst und negativ auf der Rechnung berücksichtigt.
