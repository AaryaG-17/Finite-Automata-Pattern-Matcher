from __future__ import annotations

import html

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QAction, QColor, QFont
from PySide6.QtWidgets import (
    QApplication,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QPlainTextEdit,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from .dfa import DFA
from .graph_view import DFAGraphView
from .matcher import DFAMatcher


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

QLineEdit, QPlainTextEdit, QTableWidget, QListWidget, QTextBrowser {
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

QLabel#subtitle, QLabel#muted {
    color: #9da8b2;
}

QLabel#status {
    color: #b7c9d8;
    padding: 4px 0;
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

QListWidget {
    padding: 5px;
}

QListWidget::item {
    padding: 7px;
}

QListWidget::item:selected {
    background: #29485f;
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
        self.matcher: DFAMatcher | None = None

        self.timer = QTimer(self)
        self.timer.setInterval(300)
        self.timer.timeout.connect(self._run_step)

        self._build_menu()
        self._build_ui()
        self._set_built_state(False)

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("File")

        reset_action = QAction("Reset", self)
        reset_action.setShortcut("Ctrl+R")
        reset_action.triggered.connect(self._reset_all)
        file_menu.addAction(reset_action)

        example_action = QAction(
            "Load Example",
            self,
        )
        example_action.setShortcut("Ctrl+E")
        example_action.triggered.connect(
            self._load_example
        )
        file_menu.addAction(example_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(
            QApplication.quit
        )
        file_menu.addAction(exit_action)

        help_menu = self.menuBar().addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(
            self._show_about
        )
        help_menu.addAction(about_action)

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        root = QVBoxLayout(central)
        root.setContentsMargins(14, 12, 14, 12)
        root.setSpacing(10)

        title = QLabel(
            "Finite Automata Pattern Matcher"
        )
        title.setObjectName("title")
        root.addWidget(title)

        subtitle = QLabel(
            "Build a deterministic finite automaton from a pattern, then use the machine itself to search the text."
        )
        subtitle.setObjectName("subtitle")
        root.addWidget(subtitle)

        # --------------------------------------------------------------
        # Input
        # --------------------------------------------------------------

        input_box = QGroupBox("Input")
        input_layout = QGridLayout(input_box)
        input_layout.setHorizontalSpacing(10)
        input_layout.setVerticalSpacing(8)

        input_layout.addWidget(
            QLabel("Text"),
            0,
            0,
        )

        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlaceholderText(
            "Enter the text to search..."
        )
        self.text_edit.setFixedHeight(90)

        input_layout.addWidget(
            self.text_edit,
            0,
            1,
            1,
            5,
        )

        input_layout.addWidget(
            QLabel("Pattern"),
            1,
            0,
        )

        self.pattern_edit = QLineEdit()
        self.pattern_edit.setPlaceholderText(
            "Enter the pattern..."
        )

        input_layout.addWidget(
            self.pattern_edit,
            1,
            1,
            1,
            2,
        )

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

        self.example_button = QPushButton(
            "Example"
        )
        self.example_button.clicked.connect(
            self._load_example
        )

        input_layout.addWidget(
            self.example_button,
            1,
            4,
        )

        self.reset_button = QPushButton(
            "Reset"
        )
        self.reset_button.clicked.connect(
            self._reset_all
        )

        input_layout.addWidget(
            self.reset_button,
            1,
            5,
        )

        root.addWidget(input_box)

        # --------------------------------------------------------------
        # Matching controls
        # --------------------------------------------------------------

        controls = QHBoxLayout()

        self.step_button = QPushButton("Step")
        self.step_button.clicked.connect(
            self._step_once
        )

        self.run_button = QPushButton("Run")
        self.run_button.clicked.connect(
            self._start_run
        )

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(
            self._pause_run
        )

        for button in (
            self.step_button,
            self.run_button,
            self.pause_button,
        ):
            controls.addWidget(button)

        controls.addStretch(1)

        self.status_label = QLabel(
            "Build a DFA to begin."
        )
        self.status_label.setObjectName(
            "status"
        )

        controls.addWidget(
            self.status_label
        )

        root.addLayout(controls)

        # --------------------------------------------------------------
        # Main splitter
        # --------------------------------------------------------------

        splitter = QSplitter(
            Qt.Orientation.Horizontal
        )
        splitter.setChildrenCollapsible(False)

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

        self.graph_view = DFAGraphView()

        # Graph controls.
        graph_controls = QHBoxLayout()

        zoom_out_button = QPushButton("−")
        zoom_out_button.setToolTip(
            "Zoom out"
        )
        zoom_out_button.clicked.connect(
            self.graph_view.zoom_out
        )

        zoom_in_button = QPushButton("+")
        zoom_in_button.setToolTip(
            "Zoom in"
        )
        zoom_in_button.clicked.connect(
            self.graph_view.zoom_in
        )

        fit_button = QPushButton("Fit")
        fit_button.setToolTip(
            "Fit the complete DFA in the view"
        )
        fit_button.clicked.connect(
            self.graph_view.fit_graph
        )

        graph_controls.addWidget(
            zoom_out_button
        )
        graph_controls.addWidget(
            zoom_in_button
        )
        graph_controls.addWidget(
            fit_button
        )
        graph_controls.addStretch()

        graph_layout.addLayout(
            graph_controls
        )

        graph_layout.addWidget(
            self.graph_view
        )

        splitter.addWidget(
            graph_box
        )

        # --------------------------------------------------------------
        # Right-side information panel
        # --------------------------------------------------------------

        side_box = QWidget()

        side_layout = QVBoxLayout(
            side_box
        )
        side_layout.setContentsMargins(
            0,
            0,
            0,
            0,
        )
        side_layout.setSpacing(10)

        # Transition table.
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

        side_layout.addWidget(
            table_box,
            2,
        )

        # Matching results.
        results_box = QGroupBox(
            "Matching Results"
        )

        results_layout = QVBoxLayout(
            results_box
        )

        self.progress_label = QLabel(
            "Processed: 0 / 0"
        )
        self.progress_label.setObjectName(
            "muted"
        )

        results_layout.addWidget(
            self.progress_label
        )

        self.current_char_label = QLabel(
            "Current character: —"
        )

        results_layout.addWidget(
            self.current_char_label
        )

        self.current_state_label = QLabel(
            "Current state: q0"
        )

        results_layout.addWidget(
            self.current_state_label
        )

        self.match_summary = QLabel(
            "Matches: 0"
        )
        self.match_summary.setObjectName(
            "muted"
        )

        results_layout.addWidget(
            self.match_summary
        )

        self.matches_list = QListWidget()

        results_layout.addWidget(
            self.matches_list,
            1,
        )

        side_layout.addWidget(
            results_box,
            1,
        )

        splitter.addWidget(
            side_box
        )

        splitter.setSizes(
            [1000, 430]
        )

        # --------------------------------------------------------------
        # Text preview
        # --------------------------------------------------------------

        text_box = QGroupBox(
            "Text Being Processed"
        )

        text_layout = QVBoxLayout(
            text_box
        )

        self.text_browser = QTextBrowser()
        self.text_browser.setOpenExternalLinks(
            False
        )
        self.text_browser.setMinimumHeight(
            95
        )

        text_layout.addWidget(
            self.text_browser
        )

        root.addWidget(
            text_box
        )

        self._set_text_preview(
            "Enter text and pattern, then click Build DFA."
        )

    def _set_built_state(
        self,
        built: bool,
    ) -> None:
        self.step_button.setEnabled(built)
        self.run_button.setEnabled(built)

        self.pause_button.setEnabled(
            built and self.timer.isActive()
        )

        self.reset_button.setEnabled(True)

    def _build_dfa(self) -> None:
        pattern = self.pattern_edit.text()
        text = self.text_edit.toPlainText()

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
                "Please keep the pattern at 80 characters or fewer so the state graph remains readable.",
            )
            return

        self.timer.stop()

        try:
            self.dfa = DFA.build(pattern)

        except (TypeError, ValueError) as exc:
            QMessageBox.warning(
                self,
                "Cannot build DFA",
                str(exc),
            )
            return

        self.matcher = DFAMatcher(
            self.dfa,
            text,
        )

        self.graph_view.set_dfa(
            self.dfa
        )

        self._populate_transition_table()
        self._clear_results()
        self._refresh_preview()

        self._set_built_state(True)

        self.status_label.setText(
            f"DFA built: {self.dfa.state_count} states, "
            f"{len(self.dfa.alphabet)} pattern symbols."
        )

    def _populate_transition_table(
        self,
    ) -> None:
        assert self.dfa is not None

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
            ["State", *symbols]
        )

        for state in range(
            self.dfa.state_count
        ):
            state_item = QTableWidgetItem(
                f"q{state}"
            )

            if state == 0:
                state_item.setText(
                    "→ q0"
                )

            if state == self.dfa.accepting_state:
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

            for col, symbol in enumerate(
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
                    col,
                    item,
                )

        self.table.resizeRowsToContents()

    def _clear_results(self) -> None:
        self.matches_list.clear()

        self.match_summary.setText(
            "Matches: 0"
        )

        self.progress_label.setText(
            f"Processed: 0 / "
            f"{len(self.matcher.text) if self.matcher else 0}"
        )

        self.current_char_label.setText(
            "Current character: —"
        )

        self.current_state_label.setText(
            "Current state: q0"
        )

        if self.dfa is not None:
            self.graph_view.highlight_state(0)
            self.graph_view.clear_highlight()

    def _refresh_preview(
        self,
        current_index: int | None = None,
        current_match_start: int | None = None,
    ) -> None:
        if (
            self.matcher is None
            or self.dfa is None
        ):
            self._set_text_preview(
                "Enter text and pattern, then click Build DFA."
            )
            return

        text = self.matcher.text
        matches = set(
            self.matcher.matches
        )

        pattern_len = len(
            self.dfa.pattern
        )

        parts: list[str] = []

        for index, char in enumerate(
            text
        ):
            escaped = html.escape(char)

            if char == "\n":
                escaped = "↵\n"
            elif char == "\t":
                escaped = "⇥"
            elif char == " ":
                escaped = "·"

            classes: list[str] = []

            if any(
                start <= index < start + pattern_len
                for start in matches
            ):
                classes.append("match")

            if current_index == index:
                classes.append("current")

            if (
                current_match_start is not None
                and current_match_start
                <= index
                < current_match_start + pattern_len
            ):
                classes.append("newmatch")

            class_name = " ".join(
                classes
            )

            if class_name:
                parts.append(
                    f'<span class="{class_name}">'
                    f"{escaped}"
                    "</span>"
                )
            else:
                parts.append(
                    escaped
                )

        body = (
            "".join(parts)
            if parts
            else "<span class='muted'>"
            "[empty text]"
            "</span>"
        )

        self.text_browser.setHtml(
            f"""
            <style>
            body {{
                font-family: monospace;
                font-size: 13px;
                color: #dfe6eb;
            }}

            .match {{
                background: #24402f;
            }}

            .newmatch {{
                background: #3c6c49;
            }}

            .current {{
                background: #8a5f24;
                color: #fff;
            }}

            .muted {{
                color: #7b8790;
            }}
            </style>

            <div style="white-space: pre-wrap;">
                {body}
            </div>
            """
        )

    def _set_text_preview(
        self,
        text: str,
    ) -> None:
        self.text_browser.setHtml(
            f"""
            <style>
            body {{
                font-family: sans-serif;
                color: #8f9aa4;
            }}
            </style>

            <div>
                {html.escape(text)}
            </div>
            """
        )

    def _step_once(self) -> None:
        if (
            self.matcher is None
            or self.dfa is None
        ):
            return

        result = self.matcher.step()

        if result is None:
            self.timer.stop()
            self.pause_button.setEnabled(
                False
            )
            self.status_label.setText(
                "Matching complete."
            )
            return

        self.graph_view.highlight_state(
            result.next_state
        )

        self.graph_view.highlight_transition(
            result.previous_state,
            result.next_state,
        )

        char_display = result.character

        if result.character == "\n":
            char_display = "\\n"
        elif result.character == "\t":
            char_display = "\\t"
        elif result.character == " ":
            char_display = "SPACE"

        self.current_char_label.setText(
            f"Current character: "
            f"{char_display!r}  |  "
            f"text index: {result.index}"
        )

        self.current_state_label.setText(
            f"Current state: q{result.next_state}"
            + (
                "  [ACCEPTING]"
                if result.next_state
                == self.dfa.accepting_state
                else ""
            )
        )

        self.progress_label.setText(
            f"Processed: "
            f"{self.matcher.processed_count} / "
            f"{len(self.matcher.text)}"
        )

        self.match_summary.setText(
            f"Matches: "
            f"{len(self.matcher.matches)}"
        )

        if (
            result.match_found
            and result.match_start is not None
        ):
            item = QListWidgetItem(
                f"Match "
                f"{len(self.matcher.matches)}"
                f" — starts at index "
                f"{result.match_start}"
            )

            self.matches_list.addItem(
                item
            )

            self.status_label.setText(
                f"Pattern found at index "
                f"{result.match_start}."
            )

        else:
            self.status_label.setText(
                f"Read index {result.index}: "
                f"state q{result.next_state}."
            )

        self._refresh_preview(
            result.index,
            result.match_start,
        )

        if self.matcher.finished:
            self.timer.stop()

            self.pause_button.setEnabled(
                False
            )

            self.status_label.setText(
                f"Matching complete — "
                f"{len(self.matcher.matches)} "
                f"occurrence(s) found."
            )

    def _start_run(self) -> None:
        if self.matcher is None:
            return

        if self.matcher.finished:
            self.matcher.reset()
            self._clear_results()
            self._refresh_preview()

        self.timer.start()

        self.pause_button.setEnabled(
            True
        )

        self.run_button.setEnabled(
            False
        )

    def _run_step(self) -> None:
        self._step_once()

        if (
            self.matcher is None
            or self.matcher.finished
        ):
            self.timer.stop()

            self.run_button.setEnabled(
                True
            )

            self.pause_button.setEnabled(
                False
            )

    def _pause_run(self) -> None:
        self.timer.stop()

        self.run_button.setEnabled(
            True
        )

        self.pause_button.setEnabled(
            False
        )

        self.status_label.setText(
            "Matching paused."
        )

    def _reset_all(self) -> None:
        self.timer.stop()

        self.dfa = None
        self.matcher = None

        self.graph_view.clear_graph()

        self.table.clear()
        self.table.setRowCount(0)
        self.table.setColumnCount(0)

        self.matches_list.clear()

        self.progress_label.setText(
            "Processed: 0 / 0"
        )

        self.current_char_label.setText(
            "Current character: —"
        )

        self.current_state_label.setText(
            "Current state: q0"
        )

        self.match_summary.setText(
            "Matches: 0"
        )

        self.status_label.setText(
            "Build a DFA to begin."
        )

        self._set_built_state(False)

        self._set_text_preview(
            "Enter text and pattern, then click Build DFA."
        )

    def _clear_results_after_match(self) -> None:
        if self.matcher is not None:
            self.matcher.reset()

        self._clear_results()
        self._refresh_preview()

    def _load_example(self) -> None:
        self.timer.stop()

        self.text_edit.setPlainText(
            "ABABABCABABAB"
        )

        self.pattern_edit.setText(
            "ABAB"
        )

        self._build_dfa()

    def _show_about(self) -> None:
        QMessageBox.information(
            self,
            "About",
            "Finite Automata Pattern Matcher\n\n"
            "An educational DFA-based exact pattern matching system.\n"
            "Built with Python and PySide6.\n\n"
            "The matcher uses the constructed DFA directly; "
            "it is not a wrapper around Python's built-in "
            "substring search.",
        )