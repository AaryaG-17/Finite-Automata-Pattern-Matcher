from __future__ import annotations

import math

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QPainter,
    QPainterPath,
    QPen,
    QPolygonF,
)
from PySide6.QtWidgets import (
    QGraphicsEllipseItem,
    QGraphicsPathItem,
    QGraphicsPolygonItem,
    QGraphicsScene,
    QGraphicsSimpleTextItem,
    QGraphicsView,
    QWidget,
)

from .dfa import DFA, OTHER_SYMBOL


class DFAGraphView(QGraphicsView):
    """Custom QGraphicsView that renders a DFA as a readable state machine."""

    NODE_RADIUS = 32.0
    HORIZONTAL_GAP = 150.0
    ARC_HEIGHT = 95.0
    TOP_PADDING = 130.0
    BOTTOM_PADDING = 130.0
    SIDE_PADDING = 90.0

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        # Click-and-drag panning.
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        # Keep the point under the mouse cursor fixed while zooming.
        self.setTransformationAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )
        self.setResizeAnchor(
            QGraphicsView.ViewportAnchor.AnchorUnderMouse
        )

        # Zoom configuration.
        self._zoom_factor = 1.15
        self._min_zoom = 0.25
        self._max_zoom = 4.0

        self.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.setBackgroundBrush(QColor("#101418"))

        self._dfa: DFA | None = None
        self._nodes: dict[int, QGraphicsEllipseItem] = {}
        self._inner_nodes: dict[int, QGraphicsEllipseItem] = {}
        self._state_labels: dict[int, QGraphicsSimpleTextItem] = {}
        self._edges: dict[
            tuple[int, int],
            list[QGraphicsPathItem | QGraphicsPolygonItem],
        ] = {}
        self._edge_labels: dict[
            tuple[int, int],
            QGraphicsSimpleTextItem,
        ] = {}
        self._start_items: list[object] = []
        self._active_state: int | None = None
        self._active_edge: tuple[int, int] | None = None

        self._node_pen = QPen(QColor("#9aa5b1"), 2.0)
        self._node_brush = QBrush(QColor("#1a222b"))
        self._accept_pen = QPen(QColor("#d5dde7"), 2.0)
        self._active_pen = QPen(QColor("#77bdfb"), 4.0)
        self._edge_pen = QPen(QColor("#8693a0"), 2.0)
        self._other_edge_pen = QPen(
            QColor("#5c6670"),
            1.5,
            Qt.PenStyle.DashLine,
        )

    # ------------------------------------------------------------------
    # Zoom / Pan
    # ------------------------------------------------------------------

    def wheelEvent(self, event) -> None:
        """Zoom the graph with the mouse wheel."""

        if event.angleDelta().y() > 0:
            factor = self._zoom_factor
        else:
            factor = 1 / self._zoom_factor

        current_scale = self.transform().m11()
        new_scale = current_scale * factor

        if self._min_zoom <= new_scale <= self._max_zoom:
            self.scale(factor, factor)

    def zoom_in(self) -> None:
        """Zoom in one step."""

        current_scale = self.transform().m11()
        new_scale = current_scale * self._zoom_factor

        if new_scale <= self._max_zoom:
            self.scale(
                self._zoom_factor,
                self._zoom_factor,
            )

    def zoom_out(self) -> None:
        """Zoom out one step."""

        current_scale = self.transform().m11()
        new_scale = current_scale / self._zoom_factor

        if new_scale >= self._min_zoom:
            self.scale(
                1 / self._zoom_factor,
                1 / self._zoom_factor,
            )

    def fit_graph(self) -> None:
        """Fit the complete DFA graph inside the view."""

        scene = self.scene()

        if scene is None:
            return

        scene_rect = scene.sceneRect()

        if scene_rect.isNull() or scene_rect.width() <= 0:
            return

        self.resetTransform()

        self.fitInView(
            scene_rect,
            Qt.AspectRatioMode.KeepAspectRatio,
        )

    # ------------------------------------------------------------------
    # Graph management
    # ------------------------------------------------------------------

    def clear_graph(self) -> None:
        scene = QGraphicsScene(self)
        scene.setBackgroundBrush(QColor("#101418"))
        self.setScene(scene)

        self._nodes.clear()
        self._inner_nodes.clear()
        self._state_labels.clear()
        self._edges.clear()
        self._edge_labels.clear()
        self._start_items.clear()
        self._active_state = None
        self._active_edge = None
        self._dfa = None

    def set_dfa(self, dfa: DFA) -> None:
        self._dfa = dfa

        scene = QGraphicsScene(self)
        scene.setBackgroundBrush(QColor("#101418"))
        self.setScene(scene)

        self._nodes.clear()
        self._inner_nodes.clear()
        self._state_labels.clear()
        self._edges.clear()
        self._edge_labels.clear()
        self._start_items.clear()
        self._active_state = 0
        self._active_edge = None

        positions = self._layout_states(dfa)

        self._draw_edges(dfa, positions)
        self._draw_nodes(dfa, positions)
        self._draw_start_indicator(positions[0])

        scene.setSceneRect(
            QRectF(
                0,
                0,
                max(
                    900.0,
                    positions[-1].x()
                    + self.SIDE_PADDING
                    + self.NODE_RADIUS,
                ),
                self.TOP_PADDING
                + self.BOTTOM_PADDING
                + 2 * self.NODE_RADIUS
                + 2 * self.ARC_HEIGHT,
            )
        )

        self.fit_graph()
        self.highlight_state(0)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _layout_states(self, dfa: DFA) -> list[QPointF]:
        baseline = self.TOP_PADDING + self.NODE_RADIUS + 10
        center_x = self.SIDE_PADDING + self.NODE_RADIUS

        return [
            QPointF(
                center_x + i * self.HORIZONTAL_GAP,
                baseline,
            )
            for i in range(dfa.state_count)
        ]

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

        for state, pos in enumerate(positions):
            outer = QGraphicsEllipseItem(
                -self.NODE_RADIUS,
                -self.NODE_RADIUS,
                2 * self.NODE_RADIUS,
                2 * self.NODE_RADIUS,
            )

            outer.setPos(pos)
            outer.setBrush(self._node_brush)
            outer.setPen(
                self._accept_pen
                if state == dfa.accepting_state
                else self._node_pen
            )
            outer.setZValue(10)

            scene.addItem(outer)
            self._nodes[state] = outer

            if state == dfa.accepting_state:
                inner_radius = self.NODE_RADIUS - 6

                inner = QGraphicsEllipseItem(
                    -inner_radius,
                    -inner_radius,
                    2 * inner_radius,
                    2 * inner_radius,
                )

                inner.setPos(pos)
                inner.setBrush(Qt.BrushStyle.NoBrush)
                inner.setPen(self._accept_pen)
                inner.setZValue(10.1)

                scene.addItem(inner)
                self._inner_nodes[state] = inner

            label = QGraphicsSimpleTextItem(f"q{state}")

            font = QFont("Sans Serif", 10)
            font.setBold(True)

            label.setFont(font)
            label.setBrush(QBrush(QColor("#f2f5f7")))
            label.setZValue(11)

            label.setPos(
                pos.x() - label.boundingRect().width() / 2,
                pos.y() - label.boundingRect().height() / 2,
            )

            scene.addItem(label)
            self._state_labels[state] = label

    # ------------------------------------------------------------------
    # START indicator
    # ------------------------------------------------------------------

    def _draw_start_indicator(self, q0: QPointF) -> None:
        scene = self.scene()
        assert scene is not None

        start_x = q0.x() - self.NODE_RADIUS - 60
        y = q0.y()

        path = QGraphicsPathItem()

        line_path = QPainterPath(QPointF(start_x, y))
        line_path.lineTo(
            QPointF(
                q0.x() - self.NODE_RADIUS - 4,
                y,
            )
        )

        path.setPath(line_path)
        path.setPen(QPen(QColor("#b8c2cc"), 2))
        path.setZValue(3)

        scene.addItem(path)

        arrow = QGraphicsPolygonItem(
            QPolygonF(
                [
                    QPointF(
                        q0.x() - self.NODE_RADIUS - 4,
                        y,
                    ),
                    QPointF(
                        q0.x() - self.NODE_RADIUS - 14,
                        y - 6,
                    ),
                    QPointF(
                        q0.x() - self.NODE_RADIUS - 14,
                        y + 6,
                    ),
                ]
            )
        )

        arrow.setBrush(QBrush(QColor("#b8c2cc")))
        arrow.setPen(QPen(Qt.PenStyle.NoPen))
        arrow.setZValue(4)

        scene.addItem(arrow)

        text = QGraphicsSimpleTextItem("START")

        font = QFont("Sans Serif", 8)
        font.setBold(True)

        text.setFont(font)
        text.setBrush(QBrush(QColor("#b8c2cc")))
        text.setPos(start_x - 6, y - 26)
        text.setZValue(4)

        scene.addItem(text)

        self._start_items.extend(
            [path, arrow, text]
        )

    # ------------------------------------------------------------------
    # Edge grouping
    # ------------------------------------------------------------------

    @staticmethod
    def _group_edges(
        dfa: DFA,
    ) -> dict[tuple[int, int], list[str]]:
        grouped: dict[
            tuple[int, int],
            list[str],
        ] = {}

        for source in range(dfa.state_count):
            for symbol in dfa.transition_symbols():
                target = dfa.transitions[source][symbol]

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

        grouped = self._group_edges(dfa)

        for (source, target), symbols in grouped.items():
            start = positions[source]
            end = positions[target]

            label_text = self._format_symbols(symbols)

            if source == target:
                path, label_pos = self._self_loop(start)
            else:
                direction = 1 if target > source else -1

                path, label_pos = self._curved_edge(
                    start,
                    end,
                    direction,
                )

            edge_pen = self._edge_pen

            if (
                OTHER_SYMBOL in symbols
                and len(symbols) == 1
            ):
                edge_pen = self._other_edge_pen

            edge = QGraphicsPathItem(path)

            edge.setPen(edge_pen)
            edge.setBrush(Qt.BrushStyle.NoBrush)
            edge.setZValue(1)

            scene.addItem(edge)

            arrow = self._make_arrow(path)

            arrow.setBrush(
                QBrush(edge_pen.color())
            )
            arrow.setPen(
                QPen(Qt.PenStyle.NoPen)
            )
            arrow.setZValue(2)

            scene.addItem(arrow)

            label = QGraphicsSimpleTextItem(
                label_text
            )

            font = QFont("Sans Serif", 8)
            font.setBold(True)

            label.setFont(font)
            label.setBrush(
                QBrush(QColor("#c7d0d8"))
            )

            label.setPos(
                label_pos.x()
                - label.boundingRect().width() / 2,
                label_pos.y()
                - label.boundingRect().height() / 2,
            )

            label.setZValue(4)

            scene.addItem(label)

            self._edges[(source, target)] = [
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
                readable.append("OTHER")
            elif symbol == "\n":
                readable.append("\\n")
            elif symbol == "\t":
                readable.append("\\t")
            elif symbol == " ":
                readable.append("SPACE")
            else:
                readable.append(symbol)

        return ", ".join(readable)

    # ------------------------------------------------------------------
    # Curved edges
    # ------------------------------------------------------------------

    def _curved_edge(
        self,
        start: QPointF,
        end: QPointF,
        direction: int,
    ) -> tuple[QPainterPath, QPointF]:

        dx = end.x() - start.x()
        dy = end.y() - start.y()

        distance = max(
            1.0,
            math.hypot(dx, dy),
        )

        ux = dx / distance
        uy = dy / distance

        px = -uy
        py = ux

        start_point = QPointF(
            start.x() + ux * self.NODE_RADIUS,
            start.y() + uy * self.NODE_RADIUS,
        )

        end_point = QPointF(
            end.x() - ux * self.NODE_RADIUS,
            end.y() - uy * self.NODE_RADIUS,
        )

        offset = (
            self.ARC_HEIGHT
            * direction
            * min(
                1.0,
                distance
                / (self.HORIZONTAL_GAP * 4),
            )
        )

        control = QPointF(
            (start_point.x() + end_point.x()) / 2
            + px * offset,
            (start_point.y() + end_point.y()) / 2
            + py * offset,
        )

        path = QPainterPath(start_point)
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

        return path, label_point

    # ------------------------------------------------------------------
    # Self-loop
    # ------------------------------------------------------------------

    def _self_loop(
        self,
        center: QPointF,
    ) -> tuple[QPainterPath, QPointF]:

        start = QPointF(
            center.x() - 12,
            center.y() - self.NODE_RADIUS + 2,
        )

        end = QPointF(
            center.x() + 12,
            center.y() - self.NODE_RADIUS + 2,
        )

        path = QPainterPath(start)

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

        return path, label_pos

    # ------------------------------------------------------------------
    # Arrow
    # ------------------------------------------------------------------

    @staticmethod
    def _make_arrow(
        path: QPainterPath,
    ) -> QGraphicsPolygonItem:

        point = path.pointAtPercent(0.995)
        previous = path.pointAtPercent(0.975)

        angle = math.atan2(
            point.y() - previous.y(),
            point.x() - previous.x(),
        )

        size = 8.0

        p1 = point

        p2 = QPointF(
            point.x()
            - size * math.cos(
                angle - math.pi / 6
            ),
            point.y()
            - size * math.sin(
                angle - math.pi / 6
            ),
        )

        p3 = QPointF(
            point.x()
            - size * math.cos(
                angle + math.pi / 6
            ),
            point.y()
            - size * math.sin(
                angle + math.pi / 6
            ),
        )

        return QGraphicsPolygonItem(
            QPolygonF([p1, p2, p3])
        )

    # ------------------------------------------------------------------
    # Highlighting
    # ------------------------------------------------------------------

    def highlight_state(
        self,
        state: int | None,
    ) -> None:

        self._active_state = state

        for index, node in self._nodes.items():
            if index == state:
                node.setPen(self._active_pen)

            elif (
                self._dfa is not None
                and index == self._dfa.accepting_state
            ):
                node.setPen(self._accept_pen)

            else:
                node.setPen(self._node_pen)

        for index, inner in self._inner_nodes.items():
            inner.setPen(
                self._active_pen
                if index == state
                else self._accept_pen
            )

    def highlight_transition(
        self,
        source: int,
        target: int,
    ) -> None:

        self._active_edge = (
            source,
            target,
        )

        for key, items in self._edges.items():
            if key == (source, target):
                for item in items:
                    if isinstance(
                        item,
                        QGraphicsPathItem,
                    ):
                        item.setPen(
                            self._active_pen
                        )

                    elif isinstance(
                        item,
                        QGraphicsPolygonItem,
                    ):
                        item.setBrush(
                            QBrush(
                                self._active_pen.color()
                            )
                        )

            else:
                symbols = self._dfa.transitions[
                    key[0]
                ]

                target_symbols = [
                    s
                    for s, t in symbols.items()
                    if t == key[1]
                ]

                use_other = (
                    OTHER_SYMBOL in target_symbols
                    and len(target_symbols) == 1
                )

                for item in items:
                    if isinstance(
                        item,
                        QGraphicsPathItem,
                    ):
                        item.setPen(
                            self._other_edge_pen
                            if use_other
                            else self._edge_pen
                        )

                    elif isinstance(
                        item,
                        QGraphicsPolygonItem,
                    ):
                        item.setBrush(
                            QBrush(
                                (
                                    self._other_edge_pen
                                    if use_other
                                    else self._edge_pen
                                ).color()
                            )
                        )

    def clear_highlight(self) -> None:
        self._active_edge = None

        if self._dfa is None:
            return

        for key, items in self._edges.items():
            symbols = self._dfa.transitions[
                key[0]
            ]

            target_symbols = [
                s
                for s, t in symbols.items()
                if t == key[1]
            ]

            use_other = (
                OTHER_SYMBOL in target_symbols
                and len(target_symbols) == 1
            )

            pen = (
                self._other_edge_pen
                if use_other
                else self._edge_pen
            )

            for item in items:
                if isinstance(
                    item,
                    QGraphicsPathItem,
                ):
                    item.setPen(pen)

                elif isinstance(
                    item,
                    QGraphicsPolygonItem,
                ):
                    item.setBrush(
                        QBrush(pen.color())
                    )