from __future__ import annotations

from PySide6.QtGui import QAction, QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QGridLayout,
    QGroupBox,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QLabel,
    QHBoxLayout,
)

from .dfa import DFA
from .graph_view import DFAGraphView


APP_STYLE = """
QMainWindow, QWidget {
    background: #0f1419;
    color: #edf2f5;
    font-size: 13px;
}

QGroupBox {
    border: 1px solid #28313a;
    border-radius: 8px;
    margin-top: 12px;
    padding: 12px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 5px;
    color: #d7dee5;
}

QLineEdit, QPlainTextEdit, QTableWidget {
    background: #151c23;
    border: 1px solid #303a44;
    border-radius: 6px;
    color: #edf2f5;
    selection-background-color: #315b7e;
}

QLineEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #5e9fd2;
}

QPushButton {
    background: #202a33;
    border: 1px solid #3a4652;
    border-radius: 6px;
    padding: 7px 13px;
    min-height: 16px;
}

QPushButton:hover {
    background: #2a3742;
}

QPushButton:disabled {
    color: #69757e;
    background: #181e23;
}

QPushButton#primaryButton {
    background: #2c5f88;
    border-color: #4f8fbe;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background: #3471a2;
}

QLabel#title {
    font-size: 21px;
    font-weight: 700;
}

QLabel#subtitle {
    color: #9da8b2;
}

QHeaderView::section {
    background: #1b232b;
    color: #dce4ea;
    border: none;
    border-bottom: 1px solid #303a44;
    padding: 6px;
    font-weight: 600;
}

QTableWidget {
    gridline-color: #263039;
}

QSplitter::handle {
    background: #252e37;
}
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle(
            "Finite Automata Pattern Matcher"
        )
        self.resize(1320, 860)
        self.setMinimumSize(1050, 700)
        self.setStyleSheet(APP_STYLE)

        self.dfa: DFA | None = None

        self._build_menu()
        self._build_ui()

    # ------------------------------------------------------------------
    # Menu
    # ------------------------------------------------------------------

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("File")

        reset_action = QAction(
            "Reset",
            self,
        )
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(
            self._reset_all
        )

        file_menu.addAction(
            reset_action
        )

        file_menu.addSeparator()

        exit_action = QAction(
            "Exit",
            self,
        )
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(
            QApplication.quit
        )

        file_menu.addAction(
            exit_action
        )

        help_menu = self.menuBar().addMenu("Help")

        about_action = QAction(
            "About",
            self,
        )
        about_action.triggered.connect(
            self._show_about
        )

        help_menu.addAction(
            about_action
        )

    # ------------------------------------------------------------------
    # Main UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(
            central
        )

        root.setContentsMargins(
            14,
            12,
            14,
            12,
        )

        root.setSpacing(10)

        # --------------------------------------------------------------
        # Title
        # --------------------------------------------------------------

        title = QLabel(
            "Finite Automata Pattern Matcher"
        )
        title.setObjectName("title")

        root.addWidget(title)

        subtitle = QLabel(
            "Build a deterministic finite automaton from a pattern, "
            "then use the machine to process the entered text."
        )
        subtitle.setObjectName("subtitle")

        root.addWidget(subtitle)

        # --------------------------------------------------------------
        # Input section
        # --------------------------------------------------------------

        input_box = QGroupBox(
            "Input"
        )

        input_layout = QGridLayout(
            input_box
        )

        input_layout.setHorizontalSpacing(
            10
        )

        input_layout.setVerticalSpacing(
            8
        )

        # Text label
        text_label = QLabel(
            "Text"
        )

        input_layout.addWidget(
            text_label,
            0,
            0,
        )

        # Text input
        self.text_edit = QPlainTextEdit()

        self.text_edit.setPlaceholderText(
            "Enter the complete input string"
        )

        self.text_edit.setMinimumHeight(
            90
        )

        input_layout.addWidget(
            self.text_edit,
            0,
            1,
            1,
            4,
        )

        # Pattern label
        pattern_label = QLabel(
            "Pattern"
        )

        input_layout.addWidget(
            pattern_label,
            1,
            0,
        )

        # Pattern input
        self.pattern_edit = QLineEdit()

        self.pattern_edit.setPlaceholderText(
            "Enter the pattern for which the DFA is to be constructed"
        )

        input_layout.addWidget(
            self.pattern_edit,
            1,
            1,
            1,
            2,
        )

        # Build button
        self.build_button = QPushButton(
            "Build DFA"
        )

        self.build_button.setObjectName(
            "primaryButton"
        )

        self.build_button.clicked.connect(
            self._build_dfa
        )

        input_layout.addWidget(
            self.build_button,
            1,
            3,
        )

        # Reset button
        self.reset_button = QPushButton(
            "Reset"
        )

        self.reset_button.clicked.connect(
            self._reset_all
        )

        input_layout.addWidget(
            self.reset_button,
            1,
            4,
        )

        root.addWidget(
            input_box
        )

        # --------------------------------------------------------------
        # Main content
        # --------------------------------------------------------------

        splitter = QSplitter()

        splitter.setChildrenCollapsible(
            False
        )

        root.addWidget(
            splitter,
            1,
        )

        # --------------------------------------------------------------
        # DFA visualization
        # --------------------------------------------------------------

        graph_box = QGroupBox(
            "DFA State Machine"
        )

        graph_layout = QVBoxLayout(
            graph_box
        )

        graph_controls = QHBoxLayout()

        zoom_out_button = QPushButton(
            "−"
        )

        zoom_out_button.setToolTip(
            "Zoom out"
        )

        zoom_out_button.clicked.connect(
            lambda: self.graph_view.zoom_out()
        )

        graph_controls.addWidget(
            zoom_out_button
        )

        zoom_in_button = QPushButton(
            "+"
        )

        zoom_in_button.setToolTip(
            "Zoom in"
        )

        zoom_in_button.clicked.connect(
            lambda: self.graph_view.zoom_in()
        )

        graph_controls.addWidget(
            zoom_in_button
        )

        fit_button = QPushButton(
            "Fit"
        )

        fit_button.setToolTip(
            "Fit the complete DFA in the view"
        )

        fit_button.clicked.connect(
            lambda: self.graph_view.fit_graph()
        )

        graph_controls.addWidget(
            fit_button
        )

        graph_controls.addStretch()

        graph_layout.addLayout(
            graph_controls
        )

        self.graph_view = DFAGraphView()

        graph_layout.addWidget(
            self.graph_view
        )

        splitter.addWidget(
            graph_box
        )

        # --------------------------------------------------------------
        # Transition table
        # --------------------------------------------------------------

        table_box = QGroupBox(
            "Transition Table"
        )

        table_layout = QVBoxLayout(
            table_box
        )

        self.table = QTableWidget()

        self.table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )

        self.table.setSelectionMode(
            QTableWidget.SelectionMode.NoSelection
        )

        self.table.verticalHeader().setVisible(
            False
        )

        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )

        table_layout.addWidget(
            self.table
        )

        splitter.addWidget(
            table_box
        )

        splitter.setSizes(
            [1000, 430]
        )

    # ------------------------------------------------------------------
    # DFA construction
    # ------------------------------------------------------------------

    def _build_dfa(self) -> None:
        pattern = self.pattern_edit.text()

        if not pattern:
            QMessageBox.warning(
                self,
                "Pattern required",
                "Please enter a non-empty pattern.",
            )
            return

        if len(pattern) > 80:
            QMessageBox.warning(
                self,
                "Pattern too long",
                "Please keep the pattern at 80 characters or fewer "
                "so the state graph remains readable.",
            )
            return

        try:
            self.dfa = DFA.build(
                pattern
            )

        except (
            TypeError,
            ValueError,
        ) as exc:
            QMessageBox.warning(
                self,
                "Cannot build DFA",
                str(exc),
            )
            return

        self.graph_view.set_dfa(
            self.dfa
        )

        self._populate_transition_table()

    # ------------------------------------------------------------------
    # Transition table
    # ------------------------------------------------------------------

    def _populate_transition_table(self) -> None:
        if self.dfa is None:
            return

        symbols = (
            self.dfa.transition_symbols()
        )

        self.table.clear()

        self.table.setColumnCount(
            len(symbols) + 1
        )

        self.table.setRowCount(
            self.dfa.state_count
        )

        self.table.setHorizontalHeaderLabels(
            [
                "State",
                *symbols,
            ]
        )

        for state in range(
            self.dfa.state_count
        ):
            state_item = QTableWidgetItem(
                f"q{state}"
            )

            if state == 0:
                state_item.setText(
                    f"→ q{state}"
                )

            if (
                state
                == self.dfa.accepting_state
            ):
                state_item.setText(
                    (
                        "→ "
                        if state == 0
                        else ""
                    )
                    + f"q{state} (accept)"
                )

            self.table.setItem(
                state,
                0,
                state_item,
            )

            for column, symbol in enumerate(
                symbols,
                start=1,
            ):
                target = (
                    self.dfa.transitions[
                        state
                    ][symbol]
                )

                item = QTableWidgetItem(
                    f"q{target}"
                )

                if (
                    target
                    == self.dfa.accepting_state
                ):
                    item.setForeground(
                        QColor("#9dd7ff")
                    )

                    font = item.font()
                    font.setBold(True)
                    item.setFont(font)

                self.table.setItem(
                    state,
                    column,
                    item,
                )

        self.table.resizeRowsToContents()

    # ------------------------------------------------------------------
    # Reset
    # ------------------------------------------------------------------

    def _reset_all(self) -> None:
        self.dfa = None

        self.text_edit.clear()
        self.pattern_edit.clear()

        self.graph_view.clear_graph()

        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

    # ------------------------------------------------------------------
    # About
    # ------------------------------------------------------------------

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About",
            "Finite Automata Pattern Matcher\n\n"
            "An educational DFA-based pattern matching "
            "visualization system.\n\n"
            "Built with Python and PySide6.",
        )