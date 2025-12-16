"""Transport bar"""
from typing import Optional
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QIcon, QPainter, QPixmap, QColor, QPen, QPolygon
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QSlider, QVBoxLayout, QWidget

def create_icon(draw_func, size=32, color="#FFFFFF"):
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor(color), 2))
    painter.setBrush(QColor(color))
    draw_func(painter, size, color)
    painter.end()
    return QIcon(pixmap)

def draw_play(p, s, c):
    m = s // 4
    p.drawPolygon(QPolygon([QPoint(m, m), QPoint(s-m, s//2), QPoint(m, s-m)]))

def draw_pause(p, s, c):
    m, w = s // 4, s // 6
    p.fillRect(m, m, w, s-2*m, QColor(c))
    p.fillRect(s-m-w, m, w, s-2*m, QColor(c))

def draw_stop(p, s, c):
    m = s // 4
    p.fillRect(m, m, s-2*m, s-2*m, QColor(c))

def draw_skip_back(p, s, c):
    m, mid = s // 4, s // 2
    p.fillRect(m, m, 3, s-2*m, QColor(c))
    p.drawPolygon(QPolygon([QPoint(s-m, m), QPoint(mid, mid), QPoint(s-m, s-m)]))

def draw_skip_fwd(p, s, c):
    m, mid = s // 4, s // 2
    p.fillRect(s-m-3, m, 3, s-2*m, QColor(c))
    p.drawPolygon(QPolygon([QPoint(m, m), QPoint(mid, mid), QPoint(m, s-m)]))

def draw_rewind(p, s, c):
    m, mid = s // 5, s // 2
    p.drawPolygon(QPolygon([QPoint(mid, m), QPoint(m, mid), QPoint(mid, s-m)]))
    p.drawPolygon(QPolygon([QPoint(s-m, m), QPoint(mid, mid), QPoint(s-m, s-m)]))

def draw_forward(p, s, c):
    m, mid = s // 5, s // 2
    p.drawPolygon(QPolygon([QPoint(m, m), QPoint(mid, mid), QPoint(m, s-m)]))
    p.drawPolygon(QPolygon([QPoint(mid, m), QPoint(s-m, mid), QPoint(mid, s-m)]))

class TransportBar(QWidget):
    play_clicked = pyqtSignal()
    pause_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    seek_requested = pyqtSignal(float)
    skip_forward = pyqtSignal()
    skip_backward = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._is_playing = False
        self._duration = 0.0
        self._seeking = False
        self._play_icon = create_icon(draw_play)
        self._pause_icon = create_icon(draw_pause)
        self._stop_icon = create_icon(draw_stop)
        self._skip_back_icon = create_icon(draw_skip_back)
        self._skip_fwd_icon = create_icon(draw_skip_fwd)
        self._rewind_icon = create_icon(draw_rewind)
        self._forward_icon = create_icon(draw_forward)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(8)
        seek = QHBoxLayout()
        seek.setSpacing(12)
        self._current_time = QLabel("00:00")
        self._current_time.setMinimumWidth(50)
        self._seek_slider = QSlider(Qt.Orientation.Horizontal)
        self._seek_slider.setRange(0, 1000)
        self._seek_slider.sliderPressed.connect(self._on_seek_pressed)
        self._seek_slider.sliderReleased.connect(self._on_seek_released)
        self._seek_slider.valueChanged.connect(self._on_seek_value_changed)
        self._total_time = QLabel("00:00")
        self._total_time.setMinimumWidth(50)
        self._total_time.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        seek.addWidget(self._current_time)
        seek.addWidget(self._seek_slider, 1)
        seek.addWidget(self._total_time)
        layout.addLayout(seek)
        ctrl = QHBoxLayout()
        ctrl.setSpacing(16)
        ctrl.addStretch()
        isz = QSize(24, 24)
        self._skip_back_btn = QPushButton()
        self._skip_back_btn.setIcon(self._skip_back_icon)
        self._skip_back_btn.setIconSize(isz)
        self._skip_back_btn.setFixedSize(40, 40)
        self._skip_back_btn.clicked.connect(self.skip_backward.emit)
        self._rewind_btn = QPushButton()
        self._rewind_btn.setIcon(self._rewind_icon)
        self._rewind_btn.setIconSize(isz)
        self._rewind_btn.setFixedSize(40, 40)
        self._rewind_btn.clicked.connect(lambda: self.skip_backward.emit())
        self._play_btn = QPushButton()
        self._play_btn.setIcon(self._play_icon)
        self._play_btn.setIconSize(QSize(32, 32))
        self._play_btn.setFixedSize(56, 56)
        self._play_btn.clicked.connect(self._on_play_clicked)
        self._forward_btn = QPushButton()
        self._forward_btn.setIcon(self._forward_icon)
        self._forward_btn.setIconSize(isz)
        self._forward_btn.setFixedSize(40, 40)
        self._forward_btn.clicked.connect(lambda: self.skip_forward.emit())
        self._skip_fwd_btn = QPushButton()
        self._skip_fwd_btn.setIcon(self._skip_fwd_icon)
        self._skip_fwd_btn.setIconSize(isz)
        self._skip_fwd_btn.setFixedSize(40, 40)
        self._skip_fwd_btn.clicked.connect(self.skip_forward.emit)
        self._stop_btn = QPushButton()
        self._stop_btn.setIcon(self._stop_icon)
        self._stop_btn.setIconSize(isz)
        self._stop_btn.setFixedSize(40, 40)
        self._stop_btn.clicked.connect(self._on_stop_clicked)
        for b in [self._skip_back_btn, self._rewind_btn, self._play_btn, self._forward_btn, self._skip_fwd_btn, self._stop_btn]:
            ctrl.addWidget(b)
        ctrl.addStretch()
        layout.addLayout(ctrl)

    def _on_play_clicked(self):
        (self.pause_clicked if self._is_playing else self.play_clicked).emit()

    def _on_stop_clicked(self):
        self.stop_clicked.emit()

    def _on_seek_pressed(self):
        self._seeking = True

    def _on_seek_released(self):
        self._seeking = False
        if self._duration > 0:
            self.seek_requested.emit((self._seek_slider.value() / 1000.0) * self._duration)

    def _on_seek_value_changed(self, v):
        if self._seeking and self._duration > 0:
            self._current_time.setText(self._format_time((v / 1000.0) * self._duration))

    def set_playing(self, playing):
        self._is_playing = playing
        self._play_btn.setIcon(self._pause_icon if playing else self._play_icon)

    def set_duration(self, d):
        self._duration = d
        self._total_time.setText(self._format_time(d))

    def set_position(self, p):
        if not self._seeking:
            self._current_time.setText(self._format_time(p))
            if self._duration > 0:
                self._seek_slider.setValue(int((p / self._duration) * 1000))

    def reset(self):
        self._is_playing = False
        self._duration = 0.0
        self._play_btn.setIcon(self._play_icon)
        self._current_time.setText("00:00")
        self._total_time.setText("00:00")
        self._seek_slider.setValue(0)

    @staticmethod
    def _format_time(s):
        return f"{int(s//60):02d}:{int(s%60):02d}"

    def set_enabled(self, e):
        for b in [self._play_btn, self._stop_btn, self._skip_back_btn, self._skip_fwd_btn, self._rewind_btn, self._forward_btn]:
            b.setEnabled(e)
        self._seek_slider.setEnabled(e)
