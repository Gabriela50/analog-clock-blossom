from __future__ import annotations

import math
from datetime import datetime

from PySide6.QtCore import QPointF, QRectF, Qt, QTimer, QTime, Signal
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPen
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTabWidget,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from app.circular_schedule import ClockMark
from app.clock_model import ClockEngine
from app.database import SettingsRepository


class FeatureCard(QFrame):
    """
    Small visual card used in the welcome page.
    """

    def __init__(self, icon: str, title: str, description: str) -> None:
        super().__init__()
        self.setObjectName("FeatureCard")

        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        icon_label = QLabel(icon)
        icon_label.setObjectName("FeatureIcon")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel(title)
        title_label.setObjectName("FeatureTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description_label = QLabel(description)
        description_label.setObjectName("FeatureDescription")
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setWordWrap(True)

        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addWidget(description_label)


class WelcomePage(QWidget):
    """
    First screen shown before entering the clock.
    """

    start_requested = Signal()

    def __init__(self) -> None:
        super().__init__()
        self._start_button = QPushButton("Iniciar reloj")
        self._build_interface()

    def _build_interface(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(54, 42, 54, 42)
        main_layout.setSpacing(26)

        hero_card = QFrame()
        hero_card.setObjectName("HeroCard")
        hero_layout = QVBoxLayout(hero_card)
        hero_layout.setContentsMargins(42, 38, 42, 38)
        hero_layout.setSpacing(16)

        badge = QLabel("Taller de Estructuras de Datos")
        badge.setObjectName("BadgeLabel")
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("Reloj Analógico Blossom")
        title.setObjectName("WelcomeTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setWordWrap(True)

        subtitle = QLabel(
            "Aplicación desarrollada en Python con interfaz gráfica, programación orientada "
            "a objetos, base de datos SQLite y una lista circular doble aplicada a las "
            "marcas del reloj."
        )
        subtitle.setObjectName("WelcomeSubtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setWordWrap(True)

        self._start_button.setObjectName("HeroButton")
        self._start_button.clicked.connect(self.start_requested.emit)

        hero_layout.addWidget(badge)
        hero_layout.addWidget(title)
        hero_layout.addWidget(subtitle)
        hero_layout.addSpacing(10)
        hero_layout.addWidget(self._start_button, alignment=Qt.AlignmentFlag.AlignCenter)

        feature_grid = QGridLayout()
        feature_grid.setSpacing(18)

        feature_grid.addWidget(
            FeatureCard(
                "💖",
                "Tres manecillas",
                "Hora, minuto y segundo se calculan con lógica propia.",
            ),
            0,
            0,
        )
        feature_grid.addWidget(
            FeatureCard(
                "🎀",
                "Lista circular doble",
                "Cada marca conoce su elemento anterior y siguiente.",
            ),
            0,
            1,
        )
        feature_grid.addWidget(
            FeatureCard(
                "🌸",
                "Base de datos",
                "La personalización se guarda en SQLite.",
            ),
            0,
            2,
        )
        feature_grid.addWidget(
            FeatureCard(
                "💅",
                "Diseño personalizable",
                "El usuario puede cambiar color, nombre y recordatorio.",
            ),
            1,
            0,
        )
        feature_grid.addWidget(
            FeatureCard(
                "✨",
                "POO",
                "El proyecto separa lógica, interfaz y persistencia.",
            ),
            1,
            1,
        )
        feature_grid.addWidget(
            FeatureCard(
                "🩷",
                "Ejecución local",
                "Se ejecuta desde el portátil con Python.",
            ),
            1,
            2,
        )

        main_layout.addWidget(hero_card)
        main_layout.addLayout(feature_grid)
        main_layout.addStretch()


class AnalogClockWidget(QWidget):
    """
    Custom widget that draws the analog clock using PySide6.
    """

    def __init__(self, clock_engine: ClockEngine) -> None:
        super().__init__()
        self._clock_engine = clock_engine
        self._current_time = datetime.now()
        self._settings: dict[str, str] = {}
        self._selected_mark_value: int | None = 0

        self.setMinimumSize(540, 540)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

    def apply_settings(self, settings: dict[str, str]) -> None:
        self._settings = settings
        self.update()

    def update_time(self, current_time: datetime) -> None:
        self._current_time = current_time
        self.update()

    def select_mark(self, mark_value: int) -> None:
        self._selected_mark_value = mark_value
        self.update()

    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        side = min(self.width(), self.height()) - 70
        radius = max(side / 2, 120)
        center = QPointF(self.width() / 2, self.height() / 2)

        painter.translate(center)

        accent_color = QColor(self._settings.get("accent_color", "#EC4899"))
        dark_color = QColor("#831843")
        soft_color = QColor("#F9A8D4")
        second_color = QColor("#BE185D")

        self._draw_shadow(painter, radius)
        self._draw_background(painter, radius)
        self._draw_clock_face(painter, radius, accent_color, soft_color)
        self._draw_hour_numbers(painter, radius, dark_color)

        angles = self._clock_engine.calculate_hand_angles(self._current_time)

        self._draw_hand(
            painter=painter,
            angle_degrees=angles.hour_angle,
            length=radius * 0.42,
            width=11,
            color=dark_color,
        )

        self._draw_hand(
            painter=painter,
            angle_degrees=angles.minute_angle,
            length=radius * 0.65,
            width=7,
            color=accent_color,
        )

        if self._settings.get("show_seconds", "1") == "1":
            self._draw_hand(
                painter=painter,
                angle_degrees=angles.second_angle,
                length=radius * 0.76,
                width=3,
                color=second_color,
            )

        self._draw_center_circle(painter, accent_color)

    def _draw_shadow(self, painter: QPainter, radius: float) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(236, 72, 153, 45))
        painter.drawEllipse(QPointF(10, 16), radius, radius)

    def _draw_background(self, painter: QPainter, radius: float) -> None:
        gradient = QLinearGradient(QPointF(-radius, -radius), QPointF(radius, radius))
        gradient.setColorAt(0.0, QColor("#FFF7FB"))
        gradient.setColorAt(0.5, QColor("#FCE7F3"))
        gradient.setColorAt(1.0, QColor("#EDE9FE"))

        painter.setBrush(gradient)
        painter.setPen(QPen(QColor("#FFFFFF"), 5))
        painter.drawEllipse(QPointF(0, 0), radius, radius)

    def _draw_clock_face(
        self,
        painter: QPainter,
        radius: float,
        accent_color: QColor,
        soft_color: QColor,
    ) -> None:
        painter.setPen(QPen(accent_color, 8))
        painter.drawEllipse(QPointF(0, 0), radius - 9, radius - 9)

        painter.setPen(QPen(QColor("#FFF7FB"), 5))
        painter.drawEllipse(QPointF(0, 0), radius - 28, radius - 28)

        active_minute = self._current_time.minute

        for mark in self._clock_engine.minute_ring.iter_forward():
            angle_radians = math.radians(mark.angle_degrees)

            is_hour_mark = mark.value % 5 == 0
            is_active_mark = mark.value == active_minute
            is_selected_mark = mark.value == self._selected_mark_value

            outer_radius = radius - 45
            inner_radius = outer_radius - (22 if is_hour_mark else 10)

            start_point = QPointF(
                math.sin(angle_radians) * inner_radius,
                -math.cos(angle_radians) * inner_radius,
            )

            end_point = QPointF(
                math.sin(angle_radians) * outer_radius,
                -math.cos(angle_radians) * outer_radius,
            )

            painter.setPen(
                QPen(
                    accent_color if is_hour_mark else soft_color,
                    5 if is_hour_mark else 2,
                    Qt.PenStyle.SolidLine,
                    Qt.PenCapStyle.RoundCap,
                )
            )
            painter.drawLine(start_point, end_point)

            if is_active_mark:
                dot_radius = outer_radius - 32
                dot_point = QPointF(
                    math.sin(angle_radians) * dot_radius,
                    -math.cos(angle_radians) * dot_radius,
                )

                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(accent_color)
                painter.drawEllipse(dot_point, 7, 7)

            if is_selected_mark:
                selected_radius = outer_radius - 60
                selected_point = QPointF(
                    math.sin(angle_radians) * selected_radius,
                    -math.cos(angle_radians) * selected_radius,
                )

                painter.setPen(QPen(QColor("#BE185D"), 3))
                painter.setBrush(QColor("#FCE7F3"))
                painter.drawEllipse(selected_point, 13, 13)

                painter.setPen(QPen(QColor("#BE185D"), 2))
                painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))

                label_area = QRectF(
                    selected_point.x() - 16,
                    selected_point.y() - 16,
                    32,
                    32,
                )
                painter.drawText(
                    label_area,
                    Qt.AlignmentFlag.AlignCenter,
                    str(mark.value),
                )

    def _draw_hour_numbers(self, painter: QPainter, radius: float, text_color: QColor) -> None:
        painter.setPen(text_color)
        painter.setFont(QFont("Segoe UI", 19, QFont.Weight.Bold))

        number_radius = radius - 98

        for mark in self._clock_engine.hour_ring.iter_forward():
            angle_radians = math.radians(mark.angle_degrees)

            x_position = math.sin(angle_radians) * number_radius
            y_position = -math.cos(angle_radians) * number_radius

            text_area = QRectF(x_position - 25, y_position - 25, 50, 50)
            painter.drawText(text_area, Qt.AlignmentFlag.AlignCenter, mark.label)

    def _draw_hand(
        self,
        painter: QPainter,
        angle_degrees: float,
        length: float,
        width: int,
        color: QColor,
    ) -> None:
        painter.save()
        painter.rotate(angle_degrees)
        painter.setPen(
            QPen(
                color,
                width,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(QPointF(0, 18), QPointF(0, -length))
        painter.restore()

    def _draw_center_circle(self, painter: QPainter, accent_color: QColor) -> None:
        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(QColor(236, 72, 153, 70))
        painter.drawEllipse(QPointF(3, 4), 14, 14)

        painter.setBrush(accent_color)
        painter.drawEllipse(QPointF(0, 0), 13, 13)

        painter.setBrush(QColor("#FFFFFF"))
        painter.drawEllipse(QPointF(0, 0), 5, 5)


class SettingsPanel(QWidget):
    """
    Panel used to customize the clock and save settings in SQLite.
    """

    settings_saved = Signal(dict)

    def __init__(self, settings_repository: SettingsRepository) -> None:
        super().__init__()
        self._settings_repository = settings_repository

        self._name_input = QLineEdit()
        self._accent_color_input = QComboBox()
        self._show_seconds_input = QCheckBox("Mostrar manecilla de segundos")
        self._reminder_enabled_input = QCheckBox("Activar recordatorio")
        self._reminder_time_input = QTimeEdit()
        self._reminder_message_input = QLineEdit()
        self._save_button = QPushButton("Guardar configuración")
        self._reset_button = QPushButton("Restablecer valores")

        self._build_interface()
        self._load_settings()

    def _build_interface(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(44, 38, 44, 38)
        main_layout.setSpacing(20)

        title = QLabel("Personalización del reloj")
        title.setObjectName("SectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description = QLabel(
            "Los cambios se guardan en la base de datos SQLite y se mantienen al volver a abrir la aplicación."
        )
        description.setObjectName("DescriptionText")
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setWordWrap(True)

        form_box = QGroupBox("Configuración del usuario")
        form_layout = QFormLayout(form_box)
        form_layout.setSpacing(14)

        self._accent_color_input.addItem("Rosa pastel", "#EC4899")
        self._accent_color_input.addItem("Rosa suave", "#F472B6")
        self._accent_color_input.addItem("Lila elegante", "#A78BFA")
        self._accent_color_input.addItem("Lavanda", "#C084FC")
        self._accent_color_input.addItem("Durazno rosado", "#FB7185")
        self._accent_color_input.addItem("Menta cute", "#6EE7B7")

        self._reminder_time_input.setDisplayFormat("HH:mm")

        form_layout.addRow("Nombre:", self._name_input)
        form_layout.addRow("Color principal:", self._accent_color_input)
        form_layout.addRow("", self._show_seconds_input)
        form_layout.addRow("", self._reminder_enabled_input)
        form_layout.addRow("Hora del recordatorio:", self._reminder_time_input)
        form_layout.addRow("Mensaje:", self._reminder_message_input)

        buttons_layout = QHBoxLayout()
        self._save_button.setObjectName("PrimaryButton")
        self._reset_button.setObjectName("SecondaryButton")

        self._save_button.clicked.connect(self._save_settings)
        self._reset_button.clicked.connect(self._reset_settings)

        buttons_layout.addWidget(self._reset_button)
        buttons_layout.addWidget(self._save_button)

        main_layout.addWidget(title)
        main_layout.addWidget(description)
        main_layout.addWidget(form_box)
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()

    def _load_settings(self) -> None:
        settings = self._settings_repository.load_all_settings()

        self._name_input.setText(settings.get("user_name", "Estudiante"))

        selected_color = settings.get("accent_color", "#EC4899")

        for index in range(self._accent_color_input.count()):
            if self._accent_color_input.itemData(index) == selected_color:
                self._accent_color_input.setCurrentIndex(index)
                break

        self._show_seconds_input.setChecked(settings.get("show_seconds", "1") == "1")
        self._reminder_enabled_input.setChecked(settings.get("reminder_enabled", "1") == "1")

        reminder_time = QTime.fromString(settings.get("reminder_time", "07:00"), "HH:mm")

        if not reminder_time.isValid():
            reminder_time = QTime(7, 0)

        self._reminder_time_input.setTime(reminder_time)
        self._reminder_message_input.setText(
            settings.get("reminder_message", "Hora de estudiar estructuras de datos")
        )

    def _save_settings(self) -> None:
        user_name = self._name_input.text().strip() or "Estudiante"
        reminder_message = self._reminder_message_input.text().strip()

        if not reminder_message:
            reminder_message = "Hora de revisar tu actividad."

        self._settings_repository.save_setting("user_name", user_name)
        self._settings_repository.save_setting(
            "accent_color",
            str(self._accent_color_input.currentData()),
        )
        self._settings_repository.save_setting(
            "show_seconds",
            "1" if self._show_seconds_input.isChecked() else "0",
        )
        self._settings_repository.save_setting(
            "reminder_enabled",
            "1" if self._reminder_enabled_input.isChecked() else "0",
        )
        self._settings_repository.save_setting(
            "reminder_time",
            self._reminder_time_input.time().toString("HH:mm"),
        )
        self._settings_repository.save_setting("reminder_message", reminder_message)

        updated_settings = self._settings_repository.load_all_settings()
        self.settings_saved.emit(updated_settings)

        QMessageBox.information(
            self,
            "Configuración guardada",
            "La personalización fue guardada correctamente en SQLite.",
        )

    def _reset_settings(self) -> None:
        self._settings_repository.save_setting("user_name", "Estudiante")
        self._settings_repository.save_setting("accent_color", "#EC4899")
        self._settings_repository.save_setting("show_seconds", "1")
        self._settings_repository.save_setting("reminder_enabled", "1")
        self._settings_repository.save_setting("reminder_time", "07:00")
        self._settings_repository.save_setting(
            "reminder_message",
            "Hora de estudiar estructuras de datos",
        )

        self._load_settings()
        updated_settings = self._settings_repository.load_all_settings()
        self.settings_saved.emit(updated_settings)

        QMessageBox.information(
            self,
            "Valores restablecidos",
            "La configuración volvió a sus valores iniciales.",
        )


class ClockRingExplorer(QGroupBox):
    """
    Visual panel that demonstrates circular doubly linked list traversal.
    """

    mark_selected = Signal(int)

    def __init__(self, clock_engine: ClockEngine) -> None:
        super().__init__("Lista circular doble")
        self._clock_engine = clock_engine
        self._current_mark: ClockMark | None = self._clock_engine.minute_ring.find_by_value(0)

        self._mark_label = QLabel()
        self._details_label = QLabel()
        self._previous_button = QPushButton("Anterior")
        self._next_button = QPushButton("Siguiente")
        self._last_to_first_button = QPushButton("Mostrar 59 → 0")

        self._build_interface()
        self._refresh_content()

    def get_current_mark_value(self) -> int:
        if self._current_mark is None:
            return 0

        return self._current_mark.value

    def _build_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        explanation = QLabel(
            "Las marcas del reloj se recorren en ambos sentidos usando referencias al "
            "elemento anterior y al elemento siguiente."
        )
        explanation.setObjectName("DescriptionText")
        explanation.setWordWrap(True)

        self._mark_label.setObjectName("BigNumber")
        self._mark_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._details_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._details_label.setWordWrap(True)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self._previous_button)
        buttons_layout.addWidget(self._next_button)

        self._previous_button.clicked.connect(self._move_previous)
        self._next_button.clicked.connect(self._move_next)
        self._last_to_first_button.clicked.connect(self._show_last_to_first_connection)

        layout.addWidget(explanation)
        layout.addWidget(self._mark_label)
        layout.addWidget(self._details_label)
        layout.addLayout(buttons_layout)
        layout.addWidget(self._last_to_first_button)

    def _move_previous(self) -> None:
        if self._current_mark is not None and self._current_mark.previous is not None:
            self._current_mark = self._current_mark.previous

        self._refresh_content()

    def _move_next(self) -> None:
        if self._current_mark is not None and self._current_mark.next is not None:
            self._current_mark = self._current_mark.next

        self._refresh_content()

    def _show_last_to_first_connection(self) -> None:
        self._current_mark = self._clock_engine.minute_ring.find_by_value(59)
        self._refresh_content()

    def _refresh_content(self) -> None:
        if self._current_mark is None:
            self._mark_label.setText("--")
            self._details_label.setText("No hay marcas disponibles.")
            return

        previous_value = (
            self._current_mark.previous.value
            if self._current_mark.previous is not None
            else "N/A"
        )

        next_value = (
            self._current_mark.next.value
            if self._current_mark.next is not None
            else "N/A"
        )

        self._mark_label.setText(str(self._current_mark.value))
        self._details_label.setText(
            f"Anterior: {previous_value} | Actual: {self._current_mark.value} | "
            f"Siguiente: {next_value}\nÁngulo: {self._current_mark.angle_degrees:.0f}°"
        )

        self.mark_selected.emit(self._current_mark.value)


class ProjectInfoPanel(QWidget):
    """
    Panel that explains the technical value of the project.
    """

    def __init__(self) -> None:
        super().__init__()
        self._build_interface()

    def _build_interface(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(44, 38, 44, 38)
        layout.setSpacing(18)

        title = QLabel("Acerca del proyecto")
        title.setObjectName("SectionTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        summary = QLabel(
            "Este proyecto implementa un reloj analógico desarrollado completamente en Python. "
            "La interfaz gráfica se construyó con PySide6, la persistencia se maneja con SQLite "
            "y la estructura de datos principal es una lista circular doble."
        )
        summary.setObjectName("DescriptionText")
        summary.setWordWrap(True)
        summary.setAlignment(Qt.AlignmentFlag.AlignCenter)

        requirements_box = QGroupBox("Cumplimiento del taller")
        requirements_layout = QVBoxLayout(requirements_box)

        requirements = QLabel(
            "• Reloj analógico con tres manecillas.\n"
            "• Código, carpetas, archivos, clases, métodos y variables en inglés.\n"
            "• Textos visibles para el usuario en español.\n"
            "• Programación orientada a objetos.\n"
            "• Base de datos SQLite para guardar personalización.\n"
            "• Lista circular doble aplicada a las marcas del reloj.\n"
            "• Funcionalidad adicional: recordatorio configurable.\n"
            "• Ejecución local en el portátil."
        )
        requirements.setObjectName("DescriptionText")
        requirements.setWordWrap(True)

        structure_box = QGroupBox("Uso de la lista circular doble")
        structure_layout = QVBoxLayout(structure_box)

        structure_text = QLabel(
            "La clase CircularClockRing representa las marcas del reloj. Cada ClockMark "
            "tiene una referencia al elemento anterior y otra al siguiente. Esto permite "
            "recorrer los minutos hacia adelante y hacia atrás. Además, el minuto 59 apunta "
            "al minuto 0, demostrando el comportamiento circular."
        )
        structure_text.setObjectName("DescriptionText")
        structure_text.setWordWrap(True)

        requirements_layout.addWidget(requirements)
        structure_layout.addWidget(structure_text)

        layout.addWidget(title)
        layout.addWidget(summary)
        layout.addWidget(requirements_box)
        layout.addWidget(structure_box)
        layout.addStretch()


class ClockWindow(QMainWindow):
    """
    Main application window.
    """

    def __init__(self) -> None:
        super().__init__()

        self._settings_repository = SettingsRepository()
        self._clock_engine = ClockEngine()
        self._settings = self._settings_repository.load_all_settings()
        self._last_reminder_key = ""

        self._stack = QStackedWidget()
        self._welcome_page = WelcomePage()
        self._clock_widget = AnalogClockWidget(self._clock_engine)
        self._settings_panel = SettingsPanel(self._settings_repository)

        self._user_label = QLabel()
        self._date_label = QLabel()
        self._time_label = QLabel()
        self._minute_label = QLabel()
        self._reminder_label = QLabel()
        self._presentation_button = QPushButton("Modo presentación")
        self._ring_explorer: ClockRingExplorer | None = None

        self._timer = QTimer(self)

        self._build_window()
        self._connect_events()
        self._apply_settings(self._settings)
        self._start_clock()

    def _build_window(self) -> None:
        self.setWindowTitle("Reloj Analógico Blossom")
        self.resize(1180, 760)

        self._apply_visual_style()

        app_page = self._build_app_page()

        self._stack.addWidget(self._welcome_page)
        self._stack.addWidget(app_page)

        self.setCentralWidget(self._stack)

    def _build_app_page(self) -> QWidget:
        tabs = QTabWidget()
        tabs.addTab(self._build_clock_page(), "Reloj")
        tabs.addTab(self._settings_panel, "Personalización")
        tabs.addTab(ProjectInfoPanel(), "Acerca del proyecto")

        return tabs

    def _build_clock_page(self) -> QWidget:
        page = QWidget()
        main_layout = QHBoxLayout(page)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(24)

        clock_card = QFrame()
        clock_card.setObjectName("MainCard")
        clock_layout = QVBoxLayout(clock_card)
        clock_layout.setSpacing(10)

        title = QLabel("Reloj analógico")
        title.setObjectName("MainTitle")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Python + PySide6 + POO + Lista circular doble")
        subtitle.setObjectName("DescriptionText")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        clock_layout.addWidget(title)
        clock_layout.addWidget(subtitle)
        clock_layout.addWidget(self._clock_widget, stretch=1)

        side_panel = QFrame()
        side_panel.setObjectName("SidePanel")
        side_layout = QVBoxLayout(side_panel)
        side_layout.setSpacing(18)

        information_box = QGroupBox("Información del reloj")
        information_layout = QVBoxLayout(information_box)
        information_layout.setSpacing(10)

        self._user_label.setObjectName("UserLabel")
        self._date_label.setObjectName("DescriptionText")
        self._time_label.setObjectName("TimeLabel")
        self._minute_label.setObjectName("DescriptionText")
        self._reminder_label.setObjectName("DescriptionText")
        self._reminder_label.setWordWrap(True)

        self._presentation_button.setObjectName("PrimaryButton")
        self._presentation_button.clicked.connect(self._toggle_presentation_mode)

        information_layout.addWidget(self._user_label)
        information_layout.addWidget(self._date_label)
        information_layout.addWidget(self._time_label)
        information_layout.addWidget(self._minute_label)
        information_layout.addWidget(self._reminder_label)
        information_layout.addWidget(self._presentation_button)

        self._ring_explorer = ClockRingExplorer(self._clock_engine)
        self._ring_explorer.mark_selected.connect(self._clock_widget.select_mark)
        self._clock_widget.select_mark(self._ring_explorer.get_current_mark_value())

        side_layout.addWidget(information_box)
        side_layout.addWidget(self._ring_explorer)
        side_layout.addStretch()

        main_layout.addWidget(clock_card, stretch=3)
        main_layout.addWidget(side_panel, stretch=2)

        return page

    def _connect_events(self) -> None:
        self._timer.timeout.connect(self._update_clock)
        self._settings_panel.settings_saved.connect(self._apply_settings)
        self._welcome_page.start_requested.connect(self._show_clock_application)

    def _show_clock_application(self) -> None:
        self._stack.setCurrentIndex(1)

    def _start_clock(self) -> None:
        self._timer.start(1000)
        self._update_clock()

    def _update_clock(self) -> None:
        current_time = datetime.now()

        self._clock_widget.update_time(current_time)

        self._date_label.setText(current_time.strftime("Fecha: %d/%m/%Y"))
        self._time_label.setText(current_time.strftime("%H:%M:%S"))

        current_mark = self._clock_engine.get_current_minute_mark(current_time)

        if current_mark is not None:
            self._minute_label.setText(
                f"Minuto actual en la lista circular: {current_mark.value} "
                f"({current_mark.angle_degrees:.0f}°)"
            )

        self._check_reminder(current_time)

    def _apply_settings(self, settings: dict[str, str]) -> None:
        self._settings = settings
        self._clock_widget.apply_settings(settings)

        user_name = settings.get("user_name", "Estudiante")
        self._user_label.setText(f"Hola, {user_name}")

        reminder_enabled = settings.get("reminder_enabled", "1") == "1"
        reminder_time = settings.get("reminder_time", "07:00")
        reminder_message = settings.get("reminder_message", "Hora de estudiar estructuras de datos")

        if reminder_enabled:
            self._reminder_label.setText(
                f"Recordatorio activo: {reminder_time} - {reminder_message}"
            )
        else:
            self._reminder_label.setText("Recordatorio desactivado.")

    def _check_reminder(self, current_time: datetime) -> None:
        if self._settings.get("reminder_enabled", "1") != "1":
            return

        configured_time = self._settings.get("reminder_time", "07:00")
        current_key = current_time.strftime("%Y-%m-%d %H:%M")

        if current_time.strftime("%H:%M") != configured_time:
            return

        if self._last_reminder_key == current_key:
            return

        self._last_reminder_key = current_key

        QMessageBox.information(
            self,
            "Recordatorio",
            self._settings.get("reminder_message", "Hora de revisar tu actividad."),
        )

    def _toggle_presentation_mode(self) -> None:
        if self.isMaximized():
            self.showNormal()
            self._presentation_button.setText("Modo presentación")
        else:
            self.showMaximized()
            self._presentation_button.setText("Salir de presentación")

    def _apply_visual_style(self) -> None:
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #FDF2F8;
            }

            QWidget {
                font-family: Segoe UI;
                font-size: 14px;
                color: #6B214E;
            }

            QStackedWidget {
                background-color: #FDF2F8;
            }

            QTabWidget::pane {
                border: none;
                background-color: #FDF2F8;
            }

            QTabBar::tab {
                background-color: #FBCFE8;
                color: #831843;
                padding: 12px 24px;
                border-top-left-radius: 16px;
                border-top-right-radius: 16px;
                margin-right: 5px;
                font-weight: 800;
            }

            QTabBar::tab:selected {
                background-color: #FFFFFF;
                color: #DB2777;
            }

            QFrame#HeroCard {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #F9A8D4,
                    stop:0.45 #FBCFE8,
                    stop:1 #DDD6FE
                );
                border-radius: 32px;
                border: 2px solid #FFFFFF;
            }

            QLabel#BadgeLabel {
                background-color: rgba(255, 255, 255, 0.55);
                color: #9D174D;
                border-radius: 16px;
                padding: 8px 18px;
                font-weight: 900;
            }

            QLabel#WelcomeTitle {
                color: #831843;
                font-size: 40px;
                font-weight: 900;
            }

            QLabel#WelcomeSubtitle {
                color: #6B214E;
                font-size: 16px;
            }

            QFrame#FeatureCard {
                background-color: #FFFFFF;
                border: 1px solid #F9A8D4;
                border-radius: 24px;
                padding: 18px;
            }

            QFrame#FeatureCard:hover {
                background-color: #FFF7FB;
                border: 2px solid #EC4899;
            }

            QLabel#FeatureIcon {
                font-size: 36px;
            }

            QLabel#FeatureTitle {
                font-size: 17px;
                font-weight: 900;
                color: #9D174D;
            }

            QLabel#FeatureDescription {
                font-size: 13px;
                color: #7C2D5D;
            }

            QFrame#MainCard,
            QFrame#SidePanel,
            QGroupBox {
                background-color: #FFFFFF;
                border: 1px solid #F9A8D4;
                border-radius: 24px;
            }

            QFrame#MainCard {
                padding: 20px;
            }

            QFrame#SidePanel {
                padding: 20px;
            }

            QGroupBox {
                margin-top: 18px;
                padding: 20px;
                font-weight: 900;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 5px 12px;
                background-color: #FFFFFF;
                color: #DB2777;
                border-radius: 10px;
            }

            QLabel#MainTitle {
                font-size: 32px;
                font-weight: 900;
                color: #9D174D;
            }

            QLabel#SectionTitle {
                font-size: 32px;
                font-weight: 900;
                color: #9D174D;
            }

            QLabel#DescriptionText {
                font-size: 14px;
                color: #7C2D5D;
            }

            QLabel#UserLabel {
                font-size: 23px;
                font-weight: 900;
                color: #9D174D;
            }

            QLabel#TimeLabel {
                font-size: 38px;
                font-weight: 900;
                color: #EC4899;
            }

            QLabel#BigNumber {
                font-size: 58px;
                font-weight: 900;
                color: #EC4899;
            }

            QLineEdit,
            QComboBox,
            QTimeEdit {
                padding: 11px;
                border: 1px solid #F9A8D4;
                border-radius: 14px;
                background-color: #FFF7FB;
                color: #831843;
                selection-background-color: #F9A8D4;
            }

            QLineEdit:focus,
            QComboBox:focus,
            QTimeEdit:focus {
                border: 2px solid #EC4899;
                background-color: #FFFFFF;
            }

            QPushButton {
                background-color: #FCE7F3;
                color: #831843;
                border: 1px solid #F9A8D4;
                border-radius: 16px;
                padding: 11px 18px;
                font-weight: 900;
            }

            QPushButton:hover {
                background-color: #FBCFE8;
                border: 1px solid #EC4899;
            }

            QPushButton:pressed {
                background-color: #F9A8D4;
            }

            QPushButton#PrimaryButton,
            QPushButton#HeroButton {
                background-color: #EC4899;
                color: #FFFFFF;
                border: none;
                padding: 14px 22px;
            }

            QPushButton#HeroButton {
                font-size: 17px;
                min-width: 190px;
                border-radius: 18px;
            }

            QPushButton#PrimaryButton:hover,
            QPushButton#HeroButton:hover {
                background-color: #DB2777;
            }

            QPushButton#SecondaryButton {
                background-color: #FFFFFF;
                color: #9D174D;
                border: 1px solid #F9A8D4;
            }

            QCheckBox {
                spacing: 8px;
                color: #831843;
                font-weight: 600;
            }

            QMessageBox {
                background-color: #FFF7FB;
            }
            """
        )