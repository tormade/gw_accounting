# UX Layout Refresh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the desktop app feel like a guided, resize-friendly office cockpit instead of stacked forms.

**Architecture:** Add reusable layout widgets for headers, cards, split master/detail work areas, and action buttons. Rework the start page into a dashboard with a calendar and quick actions. Split the order page into two clear sub-areas: creating/editing an order and managing existing orders.

**Tech Stack:** Python, PySide6 widgets/layouts, pytest source-level UI tests, existing SQLite/service layer.

---

### Task 1: Shared Layout Widgets

**Files:**
- Create: `src/getraenkeladen_tool/ui/layouts.py`
- Modify: `src/getraenkeladen_tool/ui/theme.py`
- Test: `tests/test_main_window.py`

- [ ] Add tests that assert shared UI primitives exist: `PageHeader`, `ActionCard`, `ResponsiveSplitter`.
- [ ] Implement the widgets with PySide6 layouts and stable object names.
- [ ] Add stylesheet entries for `pageHeader`, `actionCard`, `workspaceSplitter`, and `calendarPanel`.

### Task 2: Start Cockpit

**Files:**
- Modify: `src/getraenkeladen_tool/ui/dashboard_panel.py`
- Test: `tests/test_main_window.py`

- [ ] Add tests for `QCalendarWidget`, quick action cards, and a two-column cockpit layout.
- [ ] Replace the stacked start layout with a dashboard: quick actions, metric cards, calendar, next steps.
- [ ] Keep the existing `new_delivery_requested` signal for the main “Neue Lieferung” route.

### Task 3: Order Page Split

**Files:**
- Modify: `src/getraenkeladen_tool/ui/order_panel.py`
- Test: `tests/test_order_panel_ui.py`

- [ ] Add tests for an inner tab layout with `Neuer Auftrag` and `Auftraege verwalten`.
- [ ] Move the order management list into its own tab and remove the fixed maximum table height.
- [ ] Use `QSplitter`/stretch factors so product entry and line tables grow with the window.

### Task 4: Verification

**Files:**
- Modify only if tests reveal issues.

- [ ] Run targeted UI tests.
- [ ] Run the full test suite.
- [ ] Start the PySide6 app briefly to catch import/layout errors.
- [ ] Commit and push the finished work.
