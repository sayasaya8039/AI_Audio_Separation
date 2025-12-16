# AI Audio Separation - 開発プラン

## プロジェクト概要
Moises Live風のリアルタイムAIオーディオ分離アプリケーション

## 技術スタック
- Python 3.13
- PyQt6 (GUI)
- Demucs (AI音声分離 - htdemucs_ft モデル)
- PyTorch + CUDA (GPU加速)
- PyInstaller (ビルド)

## 完了した機能 ✅

### コア機能
- [x] Demucsによる4ステム分離 (Vocals, Drums, Bass, Other)
- [x] GPU (CUDA) 対応
- [x] 高品質モデル (htdemucs_ft) 使用

### UI機能
- [x] メインウィンドウ
- [x] 波形表示 (WaveformView)
- [x] ステムミキサー (ボリューム/ミュート/ソロ)
- [x] ピッチ・テンポコントロール
- [x] トランスポートバー (再生/停止/シーク)
- [x] ダーク/ライトテーマ切り替え
- [x] ドラッグ&ドロップ対応
- [x] プログレス表示

### UI修正済み
- [x] 絵文字アイコン → QPainter描画アイコンに変更
- [x] テーマ切り替えボタン (月/太陽アイコン)
- [x] リセットボタンのレイアウト修正

### ビルド
- [x] PyInstallerでWindows実行ファイル作成
- [x] CUDA対応ビルド

## 今後の改善候補 📋

### 機能追加
- [ ] ステムのエクスポート機能
- [ ] リアルタイム再生
- [ ] ピッチ/テンポ変更の実装
- [ ] プリセット保存機能
- [ ] バッチ処理対応

### UI改善
- [ ] ステータスバーの情報充実
- [ ] キーボードショートカット追加
- [ ] 設定画面
- [ ] 言語切り替え

### パフォーマンス
- [ ] メモリ使用量の最適化
- [ ] 長時間ファイルの処理改善
- [ ] キャッシュ機能

## ファイル構成
```
AI_Audio_Separation/
├── src/
│   ├── main.py              # エントリーポイント
│   ├── core/
│   │   ├── separator.py     # Demucs分離エンジン
│   │   └── audio_engine.py  # オーディオ処理
│   ├── ui/
│   │   ├── main_window.py   # メインウィンドウ
│   │   ├── stem_mixer.py    # ステムミキサーUI
│   │   ├── waveform_view.py # 波形表示
│   │   ├── theme.py         # テーマ定義
│   │   └── widgets/
│   │       ├── stem_control.py       # ステムコントロール
│   │       ├── pitch_tempo_control.py # ピッチ/テンポ
│   │       └── transport_bar.py      # トランスポートバー
│   └── utils/
│       └── file_utils.py    # ファイルユーティリティ
├── ai_audio_separation.spec  # PyInstaller設定
├── requirements.txt          # 依存関係
└── PLAN.md                   # このファイル
```

## Git履歴
- `7734d96` [fix] UIの改善とCUDA対応
- `c0d965a` [feat] AI Audio Separation アプリの初期実装

## リポジトリ
https://github.com/sayasaya8039/AI_Audio_Separation
