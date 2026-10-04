from __future__ import annotations

import math

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
)

from .dfa import DFA, OTHER_SYMBOL


class DFAGraphView(QGraphicsView):
    """Interactive visualization of a DFA."""

    NODE_RADIUS = 28.0
    HORIZONTAL_GAP = 125.0
    ARC_HEIGHT = 55.0

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setScene(QGraphicsScene(self))

        self.setRenderHint(
            self.renderHints()
        )

        self.setRenderHint(
            self.renderHints()
        )

        self.setBackgroundBrush(
            QColor("#10161c")
        )

        self.setFrameShape(
            QGraphicsView.Shape.NoFrame
        )

        self.setDragMode(
            QGraphicsView.DragMode.ScrollHandDrag
        )

        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        self._zoom_factor = 1.15
        self._min_zoom = 0.25
        self._max_zoom = 4.0

        self._dfa: DFA | None = None

        self._nodes: dict[
            int,
            QGraphicsPathItem,
        ] = {}

        self._inner_nodes: dict[
            int,
            QGraphicsPathItem,
        ] = {}

        self._edges: dict[
            tuple[int, int],
            list[QGraphicsPathItem | QGraphicsPolygonItem],
        ] = {}

        self._edge_labels: dict[
            tuple[int, int],
            QGraphicsSimpleTextItem,
        ] = {}

        self._start_items: list[
            QGraphicsPathItem
            | QGraphicsPolygonItem
            | QGraphicsSimpleTextItem
        ] = []

        self._node_pen = QPen(
            QColor("#d8e0e8"),
            2,
        )

        self._accept_pen = QPen(
            QColor("#8bc8f5"),
            2,
        )

        self._edge_pen = QPen(
            QColor("#8f9aa5"),
            2,
        )

        self._other_edge_pen = QPen(
            QColor("#66737f"),
            1.5,
            Qt.PenStyle.DashLine,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_dfa(self, dfa: DFA) -> None:
        self._dfa = dfa
        self._render_dfa()
        self.fit_graph()

    def clear_graph(self) -> None:
        scene = self.scene()

        if scene is not None:
            scene.clear()

        self._dfa = None
        self._nodes.clear()
        self._inner_nodes.clear()
        self._edges.clear()
        self._edge_labels.clear()
        self._start_items.clear()

    # ------------------------------------------------------------------
    # Zoom controls
    # ------------------------------------------------------------------

    def zoom_in(self) -> None:
        current = self.transform().m11()
        if current >= self._max_zoom:
            return

        self.scale(
            self._zoom_factor,
            self._zoom_factor,
        )

    def zoom_out(self) -> None:
        current = self.transform().m11()
        if current <= self._min_zoom:
            return

        self.scale(
            1 / self._zoom_factor,
            1 / self._zoom_factor,
        )

    def fit_graph(self) -> None:
        scene = self.scene()

        if scene is None:
            return

        rect = scene.itemsBoundingRect()

        if rect.isNull():
            return

        rect.adjust(
            -60,
            -60,
            60,
            60,
        )

        self.fitInView(
            rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    def _render_dfa(self) -> None:
        if self._dfa is None:
            return

        scene = self.scene()
        assert scene is not None

        scene.clear()

        self._nodes.clear()
        self._inner_nodes.clear()
        self._edges.clear()
        self._edge_labels.clear()
        self._start_items.clear()

        positions = self._calculate_positions(
            self._dfa
        )

        self._draw_edges(
            self._dfa,
            positions,
        )

        self._draw_nodes(
            self._dfa,
            positions,
        )

        self._draw_start_indicator(
            positions[0]
        )

        scene.setSceneRect(
            scene.itemsBoundingRect().adjusted(
                -80,
                -80,
                80,
                80,
            )
        )

    # ------------------------------------------------------------------
    # Node positioning
    # ------------------------------------------------------------------

    def _calculate_positions(
        self,
        dfa: DFA,
    ) -> list[QPointF]:

        positions: list[QPointF] = []

        state_count = dfa.state_count

        spacing = self.HORIZONTAL_GAP

        total_width = (
            max(0, state_count - 1)
            * spacing
        )

        start_x = -total_width / 2

        for state in range(state_count):
            positions.append(
                QPointF(
                    start_x + state * spacing,
                    0,
                )
            )

        return positions

    # ------------------------------------------------------------------
    # Nodes
    # ------------------------------------------------------------------

    def _draw_nodes(
        self,
        dfa: DFA,
        positions: list[QPointF],
    ) -> None:

        scene = self.scene()
        assert scene is not None

        for state, position in enumerate(
            positions
        ):
            ellipse = scene.addEllipse(
                position.x()
                - self.NODE_RADIUS,
                position.y()
                - self.NODE_RADIUS,
                self.NODE_RADIUS * 2,
                self.NODE_RADIUS * 2,
                self._accept_pen
                if state == dfa.accepting_state
                else self._node_pen,
                QBrush(QColor("#17212a")),
            )

            ellipse.setZValue(5)

            self._nodes[state] = ellipse

            if state == dfa.accepting_state:
                inner_radius = (
                    self.NODE_RADIUS - 6
                )

                inner = scene.addEllipse(
                    position.x()
                    - inner_radius,
                    position.y()
                    - inner_radius,
                    inner_radius * 2,
                    inner_radius * 2,
                    self._accept_pen,
                    Qt.BrushStyle.NoBrush,
                )

                inner.setZValue(6)

                self._inner_nodes[state] = inner

            label = QGraphicsSimpleTextItem(
                f"q{state}"
            )

            font = QFont(
                "Sans Serif",
                10,
            )
            font.setBold(True)

            label.setFont(font)

            label.setBrush(
                QBrush(
                    QColor("#edf2f5")
                )
            )

            rect = label.boundingRect()

            label.setPos(
                position.x()
                - rect.width() / 2,
                position.y()
                - rect.height() / 2,
            )

            label.setZValue(7)

            scene.addItem(label)

    # ------------------------------------------------------------------
    # START indicator
    # ------------------------------------------------------------------

    def _draw_start_indicator(
        self,
        q0: QPointF,
    ) -> None:

        scene = self.scene()
        assert scene is not None

        start_x = (
            q0.x()
            - self.NODE_RADIUS
            - 60
        )

        y = q0.y()

        path = QGraphicsPathItem()

        line_path = QPainterPath(
            QPointF(
                start_x,
                y,
            )
        )

        line_path.lineTo(
            QPointF(
                q0.x()
                - self.NODE_RADIUS
                - 4,
                y,
            )
        )

        path.setPath(
            line_path
        )

        path.setPen(
            QPen(
                QColor("#b8c2cc"),
                2,
            )
        )

        path.setZValue(3)

        scene.addItem(path)

        arrow = QGraphicsPolygonItem(
            QPolygonF(
                [
                    QPointF(
                        q0.x()
                        - self.NODE_RADIUS
                        - 4,
                        y,
                    ),
                    QPointF(
                        q0.x()
                        - self.NODE_RADIUS
                        - 14,
                        y - 6,
                    ),
                    QPointF(
                        q0.x()
                        - self.NODE_RADIUS
                        - 14,
                        y + 6,
                    ),
                ]
            )
        )

        arrow.setBrush(
            QBrush(
                QColor("#b8c2cc")
            )
        )

        arrow.setPen(
            QPen(
                Qt.PenStyle.NoPen
            )
        )

        arrow.setZValue(4)

        scene.addItem(arrow)

        text = QGraphicsSimpleTextItem(
            "START"
        )

        font = QFont(
            "Sans Serif",
            8,
        )
        font.setBold(True)

        text.setFont(font)

        text.setBrush(
            QBrush(
                QColor("#b8c2cc")
            )
        )

        text.setPos(
            start_x - 6,
            y - 26,
        )

        text.setZValue(4)

        scene.addItem(text)

        self._start_items.extend(
            [
                path,
                arrow,
                text,
            ]
        )

    # ------------------------------------------------------------------
    # Edge grouping
    # ------------------------------------------------------------------

    @staticmethod
    def _group_edges(
        dfa: DFA,
    ) -> dict[
        tuple[int, int],
        list[str],
    ]:

        grouped: dict[
            tuple[int, int],
            list[str],
        ] = {}

        for source in range(
            dfa.state_count
        ):
            for symbol in dfa.transition_symbols():
                target = dfa.transitions[
                    source
                ][symbol]

                grouped.setdefault(
                    (source, target),
                    [],
                ).append(symbol)

        return grouped

    # ------------------------------------------------------------------
    # Edges
    # ------------------------------------------------------------------

    def _draw_edges(
        self,
        dfa: DFA,
        positions: list[QPointF],
    ) -> None:

        scene = self.scene()
        assert scene is not None

        grouped = self._group_edges(
            dfa
        )

        for (
            source,
            target,
        ), symbols in grouped.items():

            start = positions[source]
            end = positions[target]

            label_text = (
                self._format_symbols(
                    symbols
                )
            )

            if source == target:
                path, label_pos = (
                    self._self_loop(
                        start
                    )
                )

            else:
                direction = (
                    1
                    if target > source
                    else -1
                )

                path, label_pos = (
                    self._curved_edge(
                        start,
                        end,
                        direction,
                    )
                )

            edge_pen = self._edge_pen

            if (
                OTHER_SYMBOL in symbols
                and len(symbols) == 1
            ):
                edge_pen = (
                    self._other_edge_pen
                )

            edge = QGraphicsPathItem(
                path
            )

            edge.setPen(
                edge_pen
            )

            edge.setBrush(
                Qt.BrushStyle.NoBrush
            )

            edge.setZValue(1)

            scene.addItem(edge)

            arrow = self._make_arrow(
                path
            )

            arrow.setBrush(
                QBrush(
                    edge_pen.color()
                )
            )

            arrow.setPen(
                QPen(
                    Qt.PenStyle.NoPen
                )
            )

            arrow.setZValue(2)

            scene.addItem(arrow)

            label = (
                QGraphicsSimpleTextItem(
                    label_text
                )
            )

            font = QFont(
                "Sans Serif",
                8,
            )
            font.setBold(True)

            label.setFont(font)

            label.setBrush(
                QBrush(
                    QColor("#c7d0d8")
                )
            )

            label.setPos(
                label_pos.x()
                - label.boundingRect().width()
                / 2,
                label_pos.y()
                - label.boundingRect().height()
                / 2,
            )

            label.setZValue(4)

            scene.addItem(label)

            self._edges[
                (source, target)
            ] = [
                edge,
                arrow,
            ]

            self._edge_labels[
                (source, target)
            ] = label

    @staticmethod
    def _format_symbols(
        symbols: list[str],
    ) -> str:

        readable: list[str] = []

        for symbol in symbols:

            if symbol == OTHER_SYMBOL:
                readable.append(
                    "OTHER"
                )

            elif symbol == "\n":
                readable.append(
                    "\\n"
                )

            elif symbol == "\t":
                readable.append(
                    "\\t"
                )

            elif symbol == " ":
                readable.append(
                    "SPACE"
                )

            else:
                readable.append(
                    symbol
                )

        return ", ".join(
            readable
        )

    # ------------------------------------------------------------------
    # Curved edges
    # ------------------------------------------------------------------

    def _curved_edge(
        self,
        start: QPointF,
        end: QPointF,
        direction: int,
    ) -> tuple[
        QPainterPath,
        QPointF,
    ]:

        dx = end.x() - start.x()
        dy = end.y() - start.y()

        distance = max(
            1.0,
            math.hypot(
                dx,
                dy,
            ),
        )

        ux = dx / distance
        uy = dy / distance

        px = -uy
        py = ux

        start_point = QPointF(
            start.x()
            + ux * self.NODE_RADIUS,
            start.y()
            + uy * self.NODE_RADIUS,
        )

        end_point = QPointF(
            end.x()
            - ux * self.NODE_RADIUS,
            end.y()
            - uy * self.NODE_RADIUS,
        )

        offset = (
            self.ARC_HEIGHT
            * direction
            * min(
                1.0,
                distance
                / (
                    self.HORIZONTAL_GAP
                    * 4
                ),
            )
        )

        control = QPointF(
            (
                start_point.x()
                + end_point.x()
            )
            / 2
            + px * offset,
            (
                start_point.y()
                + end_point.y()
            )
            / 2
            + py * offset,
        )

        path = QPainterPath(
            start_point
        )

        path.quadTo(
            control,
            end_point,
        )

        label_point = QPointF(
            control.x()
            - px * direction * 10,
            control.y()
            - py * direction * 10,
        )

        return (
            path,
            label_point,
        )

    # ------------------------------------------------------------------
    # Self-loop
    # ------------------------------------------------------------------

    def _self_loop(
        self,
        center: QPointF,
    ) -> tuple[
        QPainterPath,
        QPointF,
    ]:

        start = QPointF(
            center.x() - 12,
            center.y()
            - self.NODE_RADIUS
            + 2,
        )

        end = QPointF(
            center.x() + 12,
            center.y()
            - self.NODE_RADIUS
            + 2,
        )

        path = QPainterPath(
            start
        )

        path.cubicTo(
            QPointF(
                center.x() - 75,
                center.y() - 95,
            ),
            QPointF(
                center.x() + 75,
                center.y() - 95,
            ),
            end,
        )

        label_pos = QPointF(
            center.x(),
            center.y() - 102,
        )

        return (
            path,
            label_pos,
        )

    # ------------------------------------------------------------------
    # Arrow
    # ------------------------------------------------------------------

    @staticmethod
    def _make_arrow(
        path: QPainterPath,
    ) -> QGraphicsPolygonItem:

        point = path.pointAtPercent(
            0.995
        )

        previous = path.pointAtPercent(
            0.975
        )

        angle = math.atan2(
            point.y()
            - previous.y(),
            point.x()
            - previous.x(),
        )

        size = 8.0

        p1 = point

        p2 = QPointF(
            point.x()
            - size
            * math.cos(
                angle - math.pi / 6
            ),
            point.y()
            - size
            * math.sin(
                angle - math.pi / 6
            ),
        )

        p3 = QPointF(
            point.x()
            - size
            * math.cos(
                angle + math.pi / 6
            ),
            point.y()
            - size
            * math.sin(
                angle + math.pi / 6
            ),
        )

        return QGraphicsPolygonItem(
            QPolygonF(
                [
                    p1,
                    p2,
                    p3,
                ]
            )
        )