# AI Audio Separation

Moises Live風のリアルタイムAIオーディオ分離ミュージックリミキサー

音楽ファイルをアップロード → AIがボーカル/ドラム/ベース/その他を分離 → カスタムミックスを作成

## 機能

### 🎵 AIステム分離
- **Demucs v4 (Hybrid Transformer)** による高品質な音声分離
- 4ステム分離: Vocals（ボーカル）、Drums（ドラム）、Bass（ベース）、Other（その他楽器）
- GPU (CUDA) 対応で高速処理、CPUでも動作

### 🎛️ リアルタイムミキサー
- 各ステムの個別ボリューム調整
- ミュート (M) / ソロ (S) ボタン
- マスターボリューム

### 🎹 ピッチ・テンポ変更
- ピッチ変更: ±12半音
- テンポ変更: 50%〜200%
- 高品質なタイムストレッチ (pyrubberband/librosa)

### 📁 入出力
- 対応形式: MP3, WAV, FLAC, M4A, AAC, OGG
- ドラッグ&ドロップ対応
- 各ステムを個別にWAVエクスポート
- カスタムミックスのエクスポート

### 🎨 モダンなUI
- パステル水色系のデザイン
- ダークモード / ライトモード切替
- リアルタイム波形表示
- 丸みを帯びた可愛らしいデザイン

## スクリーンショット

```
┌─────────────────────────────────────────────────────────────┐
│  🎵 AI Audio Separation                    [🌙/☀️] [─][□][×] │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   波形表示エリア                      │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ 🎤 Vocals│ │ 🥁 Drums │ │ 🎸 Bass  │ │ 🎹 Other │     │
│  │    ─○─   │ │    ─○─   │ │    ─○─   │ │    ─○─   │     │
│  │  [M] [S] │ │  [M] [S] │ │  [M] [S] │ │  [M] [S] │     │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘     │
│                                                             │
│  ┌──────────────────────┐  ┌──────────────────────┐       │
│  │ 🎹 ピッチ: ─○─ +2    │  │ ⏱️ テンポ: ─○─ 100% │       │
│  └──────────────────────┘  └──────────────────────┘       │
│                                                             │
│  ─────────────────────────○────────────────────────────    │
│  00:00                   02:30                    05:00    │
│                                                             │
│         [⏮️]  [⏪]  [▶️/⏸️]  [⏩]  [⏭️]                      │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │  📂 ファイル読込  │  │  💾 エクスポート  │                  │
│  └─────────────────┘  └─────────────────┘                  │
└─────────────────────────────────────────────────────────────┘
```

## インストール

### 必要条件

- Python 3.10以上
- Windows 10/11 (macOS/Linuxでも動作可能)
- CUDA対応GPU (推奨、なくても動作)

### インストール手順

```bash
# リポジトリをクローン
git clone https://github.com/yourusername/AI_Audio_Separation.git
cd AI_Audio_Separation

# 仮想環境を作成（推奨）
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# 依存パッケージをインストール
pip install -r requirements.txt
```

### PyTorch (CUDA対応) のインストール

GPU を使用する場合、CUDA対応のPyTorchをインストールしてください:

```bash
# CUDA 11.8の場合
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1の場合
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 使い方

### アプリケーションの起動

```bash
python -m src.main
```

### 基本的な使い方

1. **ファイルを開く**: 「ファイルを開く」ボタンをクリック、またはファイルをドラッグ&ドロップ
2. **分離を待つ**: AIが音声を4つのステムに分離（初回はモデルのダウンロードが必要）
3. **ミックスを調整**: 各ステムのボリュームを調整、ミュート/ソロを使用
4. **ピッチ・テンポを変更**: 必要に応じて調整
5. **エクスポート**: 「エクスポート」ボタンで保存

### キーボードショートカット

| キー | 機能 |
|------|------|
| `Ctrl+O` | ファイルを開く |
| `Ctrl+E` | エクスポート |
| `Ctrl+T` | テーマ切り替え |
| `Ctrl+Q` | 終了 |

## ビルド (EXE生成)

```bash
# PyInstallerでビルド
pip install pyinstaller
pyinstaller ai_audio_separation.spec

# 出力: AI_Audio_Separation/AI_Audio_Separation.exe
```

## 開発

### テストの実行

```bash
pytest tests/ -v
```

### コードフォーマット

```bash
black src/ tests/
ruff check src/ tests/ --fix
```

### 型チェック

```bash
mypy src/
```

## 技術スタック

| カテゴリ | 技術 |
|---------|------|
| GUI | PyQt6 |
| 音声分離AI | Demucs v4 (Meta AI) |
| オーディオ処理 | torchaudio, sounddevice, librosa |
| 波形表示 | pyqtgraph |
| ビルド | PyInstaller |

## プロジェクト構造

```
AI_Audio_Separation/
├── src/
│   ├── main.py                 # エントリーポイント
│   ├── app.py                  # メインアプリケーション
│   ├── ui/
│   │   ├── main_window.py      # メインウィンドウ
│   │   ├── stem_mixer.py       # ステムミキサーUI
│   │   ├── waveform_view.py    # 波形表示
│   │   ├── theme.py            # テーマ定義
│   │   └── widgets/            # カスタムウィジェット
│   ├── core/
│   │   ├── separator.py        # Demucs分離エンジン
│   │   ├── audio_player.py     # オーディオ再生
│   │   ├── mixer.py            # ミキシングエンジン
│   │   ├── pitch_tempo.py      # ピッチ・テンポ変更
│   │   └── exporter.py         # エクスポート
│   └── utils/                  # ユーティリティ
├── tests/                      # テスト
├── requirements.txt
├── pyproject.toml
└── README.md
```

## ライセンス

MIT License

## 謝辞

- [Demucs](https://github.com/facebookresearch/demucs) - Meta AI による音声分離モデル
- [Moises](https://moises.ai/) - インスピレーション元

## 参考リンク

- [Demucs GitHub](https://github.com/facebookresearch/demucs)
- [PyTorch Audio Tutorial](https://docs.pytorch.org/audio/stable/tutorials/hybrid_demucs_tutorial.html)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython-6/)
