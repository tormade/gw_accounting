from PySide6.QtCore import Signal
from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .layouts import ContentSurface, PageHeader, set_button_role


MANAGEMENT_ROUTES = (
    ("Kunden", "Kunden bearbeiten", "Adressen, Ordner und Lieferhinweise ändern."),
    ("Artikel", "Artikel und Preise", "Preise, Pfand und Artikelnummern pflegen."),
    ("Prüfpunkte", "Prüfpunkte", "Import-Konflikte und Preisabweichungen klären."),
    ("Import", "Excel-Import", "Stammdaten aus Excel prüfen und übernehmen."),
    ("Belegarchiv", "Belegarchiv", "Erstellte Rechnungen und Lieferscheine finden."),
)


class ManagementHomePanel(QWidget):
    route_requested = Signal(str)

    def __init__(self) -> None:
        super().__init__()
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        surface = ContentSurface()
        root_layout.addWidget(surface)
        layout = surface.layout

        layout.addWidget(
            PageHeader(
                "Verwaltung",
                "Seltener genutzte Pflegeaufgaben. Für die tägliche Arbeit zuerst „Arbeiten“ nutzen.",
            )
        )

        route_grid = QGridLayout()
        route_grid.setSpacing(14)
        for index, (route_id, title, subtitle) in enumerate(MANAGEMENT_ROUTES):
            route_grid.addWidget(self._route_button(route_id, title, subtitle), index // 2, index % 2)
        route_grid.setColumnStretch(0, 1)
        route_grid.setColumnStretch(1, 1)
        layout.addLayout(route_grid)
        layout.addStretch()

    def _route_button(self, route_id: str, title: str, subtitle: str) -> QPushButton:
        button = QPushButton(f"{title}\n{subtitle}")
        button.setObjectName("managementRouteButton")
        set_button_role(button, "secondary")
        button.setProperty("routeId", route_id)
        button.clicked.connect(lambda _checked=False, selected_route=route_id: self.route_requested.emit(selected_route))
        return button
