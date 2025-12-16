"""
メインウィンドウ

アプリケーションのメインUI
"""

from pathlib import Path
from typing import Optional

from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QAction, QDragEnterEvent, QDropEvent, QIcon, QPainter, QPixmap, QColor, QPen, QBrush
from PyQt6.QtWidgets import (
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from src.ui.stem_mixer import StemMixerUI
from src.ui.theme import Theme, ThemeManager, get_stylesheet
from src.ui.waveform_view import WaveformView
from src.ui.widgets.pitch_tempo_control import PitchTempoControl
from src.ui.widgets.transport_bar import TransportBar
from src.utils.file_utils import get_file_filter, is_supported_format

def _create_moon_icon(size=32, color="#FFFFFF"):
    """月アイコン（ダークモード用）"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(color), 2))
    p.setBrush(QBrush(QColor(color)))
    # 月の形
    m = size // 5
    p.drawEllipse(m, m, size - 2*m, size - 2*m)
    # 右側を切り取る（暗い円で覆う）
    p.setBrush(QBrush(QColor("#1E293B")))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawEllipse(size//3, m-2, size - 2*m, size - 2*m)
    p.end()
    return QIcon(pixmap)

def _create_sun_icon(size=32, color="#FFFFFF"):
    """太陽アイコン（ライトモード用）"""
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(color), 2))
    p.setBrush(QBrush(QColor(color)))
    # 中心の円
    cx, cy = size // 2, size // 2
    r = size // 5
    p.drawEllipse(cx - r, cy - r, r * 2, r * 2)
    # 光線
    import math
    for i in range(8):
        angle = i * math.pi / 4
        x1 = cx + int((r + 3) * math.cos(angle))
        y1 = cy + int((r + 3) * math.sin(angle))
        x2 = cx + int((r + 7) * math.cos(angle))
        y2 = cy + int((r + 7) * math.sin(angle))
        p.drawLine(x1, y1, x2, y2)
    p.end()
    return QIcon(pixmap)




class MainWindow(QMainWindow):
    """
    メインウィンドウ

    アプリケーションの全UIを統合
    """

    # シグナル
    file_dropped = pyqtSignal(str)  # ファイルパス
    file_selected = pyqtSignal(str)  # ファイルパス
    export_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._theme_manager = ThemeManager()

        self._setup_window()
        self._setup_ui()
        self._setup_menu()
        self._setup_statusbar()
        self._apply_theme()

    def _setup_window(self) -> None:
        """ウィンドウ設定"""
        self.setWindowTitle("AI Audio Separation")
        self.setMinimumSize(900, 700)
        self.resize(1100, 800)

        # ドラッグ&ドロップを有効化
        self.setAcceptDrops(True)

    def _setup_ui(self) -> None:
        """UIをセットアップ"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

        # ヘッダー（タイトル + テーマ切り替え）
        header_layout = QHBoxLayout()

        title_label = QLabel("AI Audio Separation")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # テーマ切り替えボタン
        self._moon_icon = _create_moon_icon()
        self._sun_icon = _create_sun_icon()
        self._theme_btn = QPushButton()
        self._theme_btn.setFixedSize(40, 40)
        self._theme_btn.setIconSize(QSize(24, 24))
        self._theme_btn.setToolTip("テーマ切り替え")
        self._theme_btn.clicked.connect(self._toggle_theme)
        header_layout.addWidget(self._theme_btn)

        main_layout.addLayout(header_layout)

        # 波形表示
        self.waveform_view = WaveformView()
        main_layout.addWidget(self.waveform_view)

        # ステムミキサー
        self.stem_mixer = StemMixerUI()
        self.stem_mixer.setEnabled(False)
        main_layout.addWidget(self.stem_mixer)

        # ピッチ・テンポコントロール
        self.pitch_tempo_control = PitchTempoControl()
        self.pitch_tempo_control.set_enabled(False)
        main_layout.addWidget(self.pitch_tempo_control)

        # トランスポートバー
        self.transport_bar = TransportBar()
        self.transport_bar.set_enabled(False)
        main_layout.addWidget(self.transport_bar)

        # プログレスバー（分離処理用）
        self._progress_frame = QFrame()
        self._progress_frame.setProperty("class", "card")
        progress_layout = QVBoxLayout(self._progress_frame)

        self._progress_label = QLabel("処理中...")
        self._progress_bar = QProgressBar()
        self._progress_bar.setRange(0, 100)

        progress_layout.addWidget(self._progress_label)
        progress_layout.addWidget(self._progress_bar)

        self._progress_frame.hide()
        main_layout.addWidget(self._progress_frame)

        # ボタンエリア
        button_layout = QHBoxLayout()

        self._load_btn = QPushButton("ファイルを開く")
        self._load_btn.setMinimumWidth(150)
        self._load_btn.clicked.connect(self._on_load_clicked)

        self._export_btn = QPushButton("エクスポート")
        self._export_btn.setMinimumWidth(150)
        self._export_btn.setEnabled(False)
        self._export_btn.clicked.connect(self.export_requested.emit)

        button_layout.addWidget(self._load_btn)
        button_layout.addStretch()
        button_layout.addWidget(self._export_btn)

        main_layout.addLayout(button_layout)

        # ドロップエリアのヒント
        self._drop_hint = QLabel("音声ファイルをドラッグ&ドロップ、または「ファイルを開く」をクリック")
        self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._drop_hint.setStyleSheet("color: #64748B; padding: 40px;")
        main_layout.addWidget(self._drop_hint)

        main_layout.addStretch()

    def _setup_menu(self) -> None:
        """メニューバーをセットアップ"""
        menubar = self.menuBar()

        # ファイルメニュー
        file_menu = menubar.addMenu("ファイル")

        open_action = QAction("開く...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._on_load_clicked)
        file_menu.addAction(open_action)

        export_action = QAction("エクスポート...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_requested.emit)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("終了", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 表示メニュー
        view_menu = menubar.addMenu("表示")

        theme_action = QAction("テーマ切り替え", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)

        # ヘルプメニュー
        help_menu = menubar.addMenu("ヘルプ")

        about_action = QAction("このアプリについて", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _setup_statusbar(self) -> None:
        """ステータスバーをセットアップ"""
        self._statusbar = QStatusBar()
        self.setStatusBar(self._statusbar)

        # GPU/CPU表示
        import torch
        device = "GPU (CUDA)" if torch.cuda.is_available() else "CPU"
        self._device_label = QLabel(f"デバイス: {device}")
        self._statusbar.addPermanentWidget(self._device_label)

    def _apply_theme(self) -> None:
        """テーマを適用"""
        theme = self._theme_manager.current_theme
        self.setStyleSheet(get_stylesheet(theme))
        self._theme_btn.setIcon(self._moon_icon if theme == Theme.DARK else self._sun_icon)

    def _toggle_theme(self) -> None:
        """テーマを切り替え"""
        new_theme = self._theme_manager.toggle_theme()
        self._theme_btn.setIcon(self._moon_icon if new_theme == Theme.DARK else self._sun_icon)
        self.waveform_view.update_theme()

    def _on_load_clicked(self) -> None:
        """ファイル選択ダイアログを開く"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "音声ファイルを選択",
            "",
            get_file_filter(),
        )
        if file_path:
            self.file_selected.emit(file_path)

    def _show_about(self) -> None:
        """アプリ情報を表示"""
        QMessageBox.about(
            self,
            "AI Audio Separation について",
            "AI Audio Separation v1.0.0\n\n"
            "Moises Live風のリアルタイムAIオーディオ分離アプリ\n\n"
            "機能:\n"
            "• AIによる音声分離（Vocals, Drums, Bass, Other）\n"
            "• リアルタイムミキシング\n"
            "• ピッチ・テンポ変更\n"
            "• ステムエクスポート\n\n"
            "Powered by Demucs (Meta AI)",
        )

    # ドラッグ&ドロップ
    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """ドラッグ進入時"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls and is_supported_format(urls[0].toLocalFile()):
                event.acceptProposedAction()
                self._drop_hint.setStyleSheet(
                    "color: #38BDF8; padding: 40px; "
                    "background-color: rgba(56, 189, 248, 0.1); "
                    "border: 2px dashed #38BDF8; border-radius: 8px;"
                )

    def dragLeaveEvent(self, event) -> None:
        """ドラッグ離脱時"""
        self._drop_hint.setStyleSheet("color: #64748B; padding: 40px;")

    def dropEvent(self, event: QDropEvent) -> None:
        """ドロップ時"""
        self._drop_hint.setStyleSheet("color: #64748B; padding: 40px;")

        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if is_supported_format(file_path):
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()

    # 公開メソッド
    def show_progress(self, visible: bool = True) -> None:
        """プログレスバーの表示/非表示"""
        self._progress_frame.setVisible(visible)
        if visible:
            self._drop_hint.hide()
        else:
            self._drop_hint.show()

    def set_progress(self, value: int, message: str = "") -> None:
        """プログレスを設定"""
        self._progress_bar.setValue(value)
        if message:
            self._progress_label.setText(message)

    def set_loaded(self, loaded: bool) -> None:
        """ファイル読み込み状態を設定"""
        self.stem_mixer.setEnabled(loaded)
        self.pitch_tempo_control.set_enabled(loaded)
        self.transport_bar.set_enabled(loaded)
        self._export_btn.setEnabled(loaded)

        if loaded:
            self._drop_hint.hide()
        else:
            self._drop_hint.show()

    def show_status(self, message: str, timeout: int = 3000) -> None:
        """ステータスバーにメッセージを表示"""
        self._statusbar.showMessage(message, timeout)

    def show_error(self, title: str, message: str) -> None:
        """エラーダイアログを表示"""
        QMessageBox.critical(self, title, message)

    def show_info(self, title: str, message: str) -> None:
        """情報ダイアログを表示"""
        QMessageBox.information(self, title, message)
