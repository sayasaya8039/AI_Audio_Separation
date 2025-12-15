"""
テーマ定義 - パステル水色系のダーク/ライトモード対応

CLAUDE.mdのデザインガイドラインに準拠
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict

from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


class Theme(Enum):
    """テーマの種類"""
    LIGHT = "light"
    DARK = "dark"


@dataclass
class ThemeColors:
    """テーマのカラー定義"""
    # 基本色
    background: str
    background_sub: str
    text: str
    text_sub: str
    accent: str

    # ステータス色
    success: str
    error: str
    warning: str

    # ステム色
    vocals: str
    drums: str
    bass: str
    other: str

    # UI要素
    border: str
    hover: str
    pressed: str


# ライトモードのカラー
LIGHT_COLORS = ThemeColors(
    background="#F0F9FF",
    background_sub="#E0F2FE",
    text="#334155",
    text_sub="#64748B",
    accent="#7DD3FC",
    success="#A7F3D0",
    error="#FECACA",
    warning="#FDE68A",
    vocals="#F472B6",
    drums="#FB923C",
    bass="#A78BFA",
    other="#4ADE80",
    border="#BAE6FD",
    hover="#E0F2FE",
    pressed="#BAE6FD",
)

# ダークモードのカラー
DARK_COLORS = ThemeColors(
    background="#0F172A",
    background_sub="#1E293B",
    text="#E0F2FE",
    text_sub="#94A3B8",
    accent="#38BDF8",
    success="#34D399",
    error="#F87171",
    warning="#FBBF24",
    vocals="#EC4899",
    drums="#F97316",
    bass="#8B5CF6",
    other="#22C55E",
    border="#334155",
    hover="#334155",
    pressed="#475569",
)


def get_stylesheet(theme: Theme) -> str:
    """指定されたテーマのQSSスタイルシートを生成"""
    colors = LIGHT_COLORS if theme == Theme.LIGHT else DARK_COLORS

    return f"""
    /* グローバルスタイル */
    QMainWindow, QWidget {{
        background-color: {colors.background};
        color: {colors.text};
        font-family: "Segoe UI", "Yu Gothic UI", sans-serif;
        font-size: 14px;
    }}

    /* ラベル */
    QLabel {{
        color: {colors.text};
    }}

    QLabel[class="subtitle"] {{
        color: {colors.text_sub};
        font-size: 12px;
    }}

    /* ボタン */
    QPushButton {{
        background-color: {colors.accent};
        color: {colors.background};
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: bold;
    }}

    QPushButton:hover {{
        background-color: {colors.hover};
        color: {colors.text};
    }}

    QPushButton:pressed {{
        background-color: {colors.pressed};
    }}

    QPushButton:disabled {{
        background-color: {colors.border};
        color: {colors.text_sub};
    }}

    /* アイコンボタン（ミュート/ソロ） */
    QPushButton[class="icon-button"] {{
        background-color: {colors.background_sub};
        border-radius: 6px;
        padding: 6px 12px;
        min-width: 30px;
    }}

    QPushButton[class="icon-button"]:checked {{
        background-color: {colors.accent};
        color: {colors.background};
    }}

    /* スライダー */
    QSlider::groove:horizontal {{
        border: none;
        height: 8px;
        background: {colors.background_sub};
        border-radius: 4px;
    }}

    QSlider::handle:horizontal {{
        background: {colors.accent};
        border: none;
        width: 18px;
        height: 18px;
        margin: -5px 0;
        border-radius: 9px;
    }}

    QSlider::handle:horizontal:hover {{
        background: {colors.text};
    }}

    QSlider::sub-page:horizontal {{
        background: {colors.accent};
        border-radius: 4px;
    }}

    /* 垂直スライダー */
    QSlider::groove:vertical {{
        border: none;
        width: 8px;
        background: {colors.background_sub};
        border-radius: 4px;
    }}

    QSlider::handle:vertical {{
        background: {colors.accent};
        border: none;
        width: 18px;
        height: 18px;
        margin: 0 -5px;
        border-radius: 9px;
    }}

    QSlider::add-page:vertical {{
        background: {colors.accent};
        border-radius: 4px;
    }}

    /* プログレスバー */
    QProgressBar {{
        border: none;
        border-radius: 6px;
        background-color: {colors.background_sub};
        text-align: center;
        color: {colors.text};
    }}

    QProgressBar::chunk {{
        background-color: {colors.accent};
        border-radius: 6px;
    }}

    /* グループボックス */
    QGroupBox {{
        background-color: {colors.background_sub};
        border: 1px solid {colors.border};
        border-radius: 12px;
        margin-top: 12px;
        padding: 16px;
        font-weight: bold;
    }}

    QGroupBox::title {{
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 8px;
        color: {colors.text};
    }}

    /* フレーム（カード） */
    QFrame[class="card"] {{
        background-color: {colors.background_sub};
        border: 1px solid {colors.border};
        border-radius: 12px;
        padding: 16px;
    }}

    /* スクロールエリア */
    QScrollArea {{
        border: none;
        background-color: transparent;
    }}

    QScrollBar:vertical {{
        border: none;
        background: {colors.background_sub};
        width: 8px;
        border-radius: 4px;
    }}

    QScrollBar::handle:vertical {{
        background: {colors.accent};
        border-radius: 4px;
        min-height: 30px;
    }}

    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    /* ファイルダイアログ */
    QFileDialog {{
        background-color: {colors.background};
    }}

    /* メニューバー */
    QMenuBar {{
        background-color: {colors.background};
        color: {colors.text};
    }}

    QMenuBar::item:selected {{
        background-color: {colors.hover};
    }}

    QMenu {{
        background-color: {colors.background_sub};
        color: {colors.text};
        border: 1px solid {colors.border};
        border-radius: 8px;
        padding: 4px;
    }}

    QMenu::item {{
        padding: 8px 24px;
        border-radius: 4px;
    }}

    QMenu::item:selected {{
        background-color: {colors.accent};
        color: {colors.background};
    }}

    /* ツールチップ */
    QToolTip {{
        background-color: {colors.background_sub};
        color: {colors.text};
        border: 1px solid {colors.border};
        border-radius: 6px;
        padding: 6px;
    }}

    /* ステム固有の色 */
    QFrame[stem="vocals"] {{
        border-left: 4px solid {colors.vocals};
    }}

    QFrame[stem="drums"] {{
        border-left: 4px solid {colors.drums};
    }}

    QFrame[stem="bass"] {{
        border-left: 4px solid {colors.bass};
    }}

    QFrame[stem="other"] {{
        border-left: 4px solid {colors.other};
    }}
    """


class ThemeManager:
    """テーマ管理クラス"""

    _instance = None
    _current_theme: Theme = Theme.DARK

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @property
    def current_theme(self) -> Theme:
        """現在のテーマを取得"""
        return self._current_theme

    @property
    def colors(self) -> ThemeColors:
        """現在のテーマの色を取得"""
        return LIGHT_COLORS if self._current_theme == Theme.LIGHT else DARK_COLORS

    def set_theme(self, theme: Theme) -> None:
        """テーマを設定"""
        self._current_theme = theme
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(theme))

    def toggle_theme(self) -> Theme:
        """テーマを切り替え"""
        new_theme = Theme.LIGHT if self._current_theme == Theme.DARK else Theme.DARK
        self.set_theme(new_theme)
        return new_theme

    def get_stem_color(self, stem_name: str) -> str:
        """ステムの色を取得"""
        colors = self.colors
        stem_colors = {
            "vocals": colors.vocals,
            "drums": colors.drums,
            "bass": colors.bass,
            "other": colors.other,
        }
        return stem_colors.get(stem_name.lower(), colors.accent)
