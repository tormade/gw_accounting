# PRD 0002: Rücklauf, Sofort-Rechnung, UAT und gezielter Polish

## Problem Statement

Der Büro-/Thekennutzer hat jetzt eine deutlich bessere Hauptnavigation und einen neuen Bereich `Arbeiten`, aber der wichtigste Tagesfluss ist noch nicht vollständig abgesichert. Nach der Bestellung ist der Standardweg fachlich: Lieferschein erzeugen, Papier-Lieferschein kommt zurück, Mengen und Pfand-Rückgabe werden geprüft oder angepasst, daraus wird die Rechnung erstellt. Gleichzeitig darf eine Sofort-Rechnung nur bewusst ausgelöst werden, weil sie den Rücklauf überspringt.

Ohne klare Absicherung besteht die Gefahr, dass der Nutzer versehentlich eine Rechnung erstellt, bevor der Rücklauf geprüft wurde, oder dass zurückgebrachte Lieferscheine weiterhin über verstreute Dialoge statt über einen einfachen Arbeitsweg bearbeitet werden. Außerdem muss der neue Hauptfluss nach dem Umbau einmal komplett als Anwenderfluss getestet und visuell geschliffen werden.

## Solution

Die App führt den Büro-/Thekennutzer im Bereich `Arbeiten` durch den Standardfluss:

1. Bestellung aufnehmen.
2. Lieferschein als Standardaktion erzeugen.
3. Bestellung als `Rücklauf offen` sichtbar machen.
4. Rücklauf öffnen, Mengen und Pfand-Rückgabe direkt prüfen oder anpassen.
5. Rechnung aus dem Rücklauf erstellen.
6. Offene Rechnung im Bereich `Rechnungen` prüfen.

Eine Sofort-Rechnung bleibt möglich, wird aber sekundär dargestellt und muss bewusst bestätigt werden. Sie überspringt den Rücklauf nur, wenn der Nutzer ausdrücklich bestätigt, dass Mengen und Pfand bereits final sind.

Nach Umsetzung wird ein kompletter UAT des Hauptflusses durchgeführt. Anschließend wird nur gezielt poliert: Lesbarkeit, Button-Zustände, Tabellenhöhen, leere Zustände, Fehlermeldungen und Textüberläufe.

## User Stories

1. As a Büro-/Thekennutzer, I want `Lieferschein erstellen` to be the obvious next action after saving an order, so that I follow the normal paper-based workflow.
2. As a Büro-/Thekennutzer, I want `Rechnung erstellen` after saving an order to feel secondary, so that I do not accidentally skip the Rücklauf.
3. As a Büro-/Thekennutzer, I want a confirmation before creating a Sofort-Rechnung, so that I consciously confirm that quantities and Pfand are final.
4. As a Büro-/Thekennutzer, I want the confirmation to explain the consequence of Sofort-Rechnung, so that I understand that no Rücklauf step will happen.
5. As a Büro-/Thekennutzer, I want to cancel Sofort-Rechnung easily, so that an accidental click does not create a wrong invoice.
6. As a Büro-/Thekennutzer, I want a created Lieferschein to put the order into `Rücklauf offen`, so that the work comes back into my daily list.
7. As a Büro-/Thekennutzer, I want open Rückläufe visible in `Arbeiten`, so that returned paper slips have one clear place.
8. As a Büro-/Thekennutzer, I want to open a Rücklauf from the list, so that I can process the specific customer and Lieferschein.
9. As a Büro-/Thekennutzer, I want to see customer name, order number, Lieferschein number and delivery date in the Rücklauf, so that I know which paper slip I am editing.
10. As a Büro-/Thekennutzer, I want the Rücklauf to show the existing order quantities, so that I can compare them with the returned paper slip.
11. As a Büro-/Thekennutzer, I want to change a delivered quantity in the Rücklauf, so that the invoice matches what was actually delivered.
12. As a Büro-/Thekennutzer, I want zero-quantity article rows to remain visible, so that known customer articles can still appear on the generated document.
13. As a Büro-/Thekennutzer, I want to enter Pfand-Rückgabe in the Rücklauf, so that returned empties reduce the invoice correctly.
14. As a Büro-/Thekennutzer, I want Pfand-Rückgabe separate from article Pfand, so that I do not confuse delivered deposit with returned empties.
15. As a Büro-/Thekennutzer, I want `Rechnung erstellen` to be the clear final action in the Rücklauf, so that I know when the slip is finished.
16. As a Büro-/Thekennutzer, I want invoice creation from Rücklauf to set the work state to final, so that the Rücklauf no longer appears as open.
17. As a Büro-/Thekennutzer, I want to return to the Rücklauf list after invoice creation, so that I can continue with the next paper slip.
18. As a Büro-/Thekennutzer, I want errors during invoice creation to be understandable, so that I can correct missing numbers or files without technical knowledge.
19. As a Büro-/Thekennutzer, I want the finished invoice to appear in `Rechnungen`, so that payment tracking remains in one place.
20. As a Büro-/Thekennutzer, I want the generated Excel/PDF to keep the known customer article rows, so that documents still match the existing Winklmeier working style.
21. As a Büro-/Thekennutzer, I want the Rücklauf UI to be readable for users over 60, so that small text and cramped controls do not slow down daily work.
22. As a Büro-/Thekennutzer, I want buttons to have stable widths and clear states, so that I can see which action is currently possible.
23. As a Büro-/Thekennutzer, I want empty states to tell me what to do next, so that an empty list does not feel broken.
24. As a Büro-/Thekennutzer, I want the complete flow tested once end to end, so that I can trust the new design in daily work.
25. As Thomas, I want the flow documented in progress notes, so that every milestone is understandable and reproducible.

## Implementation Decisions

- `Arbeiten` remains the primary workspace. Rückläufe are opened from the existing open-return list, not from a separate top-level navigation item.
- A Rücklauf is derived from an order with created Lieferschein and without created invoice. The visible user term is `Rücklauf offen`; existing internal status values may remain ASCII where needed.
- Invoice creation from Rücklauf reuses the existing document/export logic. The Rücklauf UI edits order quantities and Pfand-Rückgaben before invoking the existing invoice path.
- Sofort-Rechnung remains available from the order workflow but is guarded by a clear confirmation dialog.
- `Lieferschein erstellen` is the primary post-save action. `Rechnung erstellen` is secondary and confirmation-gated when used directly from an order.
- Status and worklist logic belongs in services or workflow modules, not directly in UI code.
- No schema migration is required for this milestone unless existing status fields cannot express `Rücklauf offen` and `Mengen final` reliably. Prefer using existing order/document state first.
- Visible German UI copy uses real umlauts.
- `Rechnungen` continues to own payment/open-item work. Rücklauf processing ends by producing an invoice/open item that appears there.

## Testing Decisions

- Good tests verify user-visible behavior and workflow state, not private widget layout details.
- The main seam is the full workflow: order saved, Lieferschein created, Rücklauf appears, Rücklauf adjusted, invoice created, open item visible.
- Service tests cover open Rücklauf detection and Sofort-Rechnung/Rücklauf status behavior.
- UI tests cover action gating: direct invoice confirmation, Rücklauf open action, Rücklauf invoice action, empty states and primary/secondary button wording.
- Existing tests around order panel, document workflow, report service, Excel/PDF generation and MainWindow navigation are the prior art.
- Full regression must pass before commit; `compileall src tests` remains the syntax/package sanity check.

## Out of Scope

- No Fahrer-App.
- No route planning or warehouse picklist.
- No new accounting integration beyond existing open items and export behavior.
- No redesign of all Stammdaten screens in this PRD.
- No replacement of Excel/PDF export templates.
- No automatic OCR or scan import for returned paper Lieferscheine.

## Further Notes

This PRD continues the accepted direction from ADR 0001. It intentionally focuses on finishing the working chain rather than another broad visual redesign. Polish happens after the UAT and only addresses concrete friction found in the flow.
