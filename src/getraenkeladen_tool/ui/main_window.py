from PySide6.QtWidgets import QLabel, QMainWindow, QTabWidget, QVBoxLayout, QWidget


MAIN_TABS = ("Kunden", "Produkte", "Belege", "Listen")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Getraenke Winklmeier")
        self.resize(1040, 680)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._panel("Kunden", "Stammdaten, Lieferhinweise und Kontakttermine"), "Kunden")
        self.tabs.addTab(self._panel("Produkte", "Zentrale Artikelliste und Standardpreise"), "Produkte")
        self.tabs.addTab(self._panel("Belege", "Rechnungen und Lieferscheine vorbereiten"), "Belege")
        self.tabs.addTab(self._panel("Listen", "Offene Posten, Tageslieferungen und Kontaktliste"), "Listen")
        self.setCentralWidget(self.tabs)

    def _panel(self, title: str, subtitle: str) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        headline = QLabel(title)
        headline.setObjectName("headline")
        layout.addWidget(headline)

        muted = QLabel(subtitle)
        muted.setObjectName("muted")
        layout.addWidget(muted)
        layout.addStretch()

        return widget
