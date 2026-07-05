# Designkonzept: Winklmeier Lieferservice-Cockpit 2026

## Ziel

Die App soll wie ein modernes lokales Arbeits-Cockpit fuer Getraenke Winklmeier wirken: markennah, freundlich, hochwertig und trotzdem klar genug fuer Menschen, die vor allem Excel und Papierablaeufe gewohnt sind.

## Leitidee

**Winklmeier Lieferservice-Cockpit**: helle Website-nahe Markenflaeche, roter Winklmeier-Akzent, schwarzer Servicekontakt und warme Arbeitsflaechen. Die Gestaltung greift die Homepage-Signale auf: Logo, Claim "Wir bringen's einfach", Lieferservice-Telefon, rote Markenstreifen und eine sachliche, regionale Anmutung.

Die App soll nicht wie eine generische KI-Chat-Oberflaeche aussehen. Sie bekommt eine eigene Handschrift: klare rote Serviceachsen, schwarze Markenbuttons fuer Startaktionen, warme Papierflaechen fuer Arbeitsruhe und gruen nur als ruhiger Status-/Fokusindikator.

## Gestaltungsregeln

- Karten und Arbeitsflaechen haben maximal 8px Radius, damit die App sachlich und erwachsen bleibt.
- Primaere Handlungen sind rot oder schwarz, passend zum Winklmeier-Logo; Gruen bleibt fuer Fokus, Kennzahlen und positive Arbeitszustaende.
- Tabellenkoepfe sind rot mit weisser Schrift, damit Listen klar gefuehrt werden und der Markenakzent sichtbar bleibt.
- Eingaben, Buttons und Navigation haben mindestens 44px Hoehe.
- Fokusrahmen sind stark sichtbar und nicht nur farblich subtil.
- Texte bleiben deutsch, handlungsnah und ohne technische Begriffe, wo Fachsprache nicht noetig ist.
- Die Hauptnavigation bleibt links und stabil, weil Wiederholung und Ortssicherheit fuer unsichere Nutzer wichtiger sind als modische Navigation.
- Der Kopfbereich zeigt sofort Marke, Claim und Telefonnummer, damit die Oberflaeche nach Winklmeier statt nach Standard-Software wirkt.

## Nutzer 60+

Die Oberflaeche setzt auf:

- hoeheren Kontrast,
- groessere Klickziele,
- klare Statusmeldungen,
- erkennbare Tabellenstruktur,
- wenige visuelle Effekte,
- keine versteckten Hover-only-Bedienungen,
- erkennbare Primaeraktion je Arbeitsbereich.

## Recherchegrundlage

Aktuelle UX-Richtung fuer 2026: digitale Produkte sollen wieder menschlicher, spezifischer und weniger generisch wirken. Fuer aeltere Nutzer ist nicht Zugang, sondern Bedienbarkeit die groesste Huerde: reduzierte Interaktionslast, hoher Kontrast, klare Rueckmeldung und verstaendliche Sprache sind wichtiger als dekorative Modernitaet.

WCAG 2.2 bestaetigt ausserdem die Bedeutung von sichtbarem Fokus und ausreichend grossen Bedienzielen. Diese Grundsaetze sind auf die PySide-Desktop-App uebertragen.

Die Winklmeier-Homepage setzt als Markenanker auf Weiss, Schwarz, Rot, das Logo, den Claim "Wir bringen's einfach" und den Lieferservice mit Telefonnummer. Diese Elemente werden in der Desktop-App als Kopfzeile und Aktionshierarchie uebersetzt, ohne die App in eine Marketingseite zu verwandeln.

## Umgesetzte Flaechen

- Globales Theme mit Winklmeier-Weiss/Rot/Schwarz, ruhigem Gruen fuer Status und warmem Papierhintergrund.
- Website-inspirierte Kopfzeile mit Logo, Claim und Lieferservice-Telefon.
- Sidebar mit groesseren Navigationszeilen und starker Auswahlmarkierung.
- Arbeitskarten eckiger und weniger generisch.
- Schnellaktionen als schwarze Markenbuttons mit rotem Hover, statt ueberall gleich lauter roter Flaechen.
- Formulare, Dropdowns und Buttons mit groesseren Bedienzielen.
- Tabellen mit klarer Kopfzeile und besser sichtbarer Auswahl.
- Offene Posten zeigen in der UI nun Rechnungsdatum, Faelligkeit und Zahlart.
