# CSV信号解析ツール

このツールは、NI VB-8012オシロスコープで取得したCSVデータから2チャンネルの信号グラフを生成します。

## 機能

- 2チャンネルの信号を同時にプロット
- フィルタ効果の比較分析
- 周波数応答の比較
- 高品質なグラフの自動保存
- **66個の全CSVファイルを71個のPNGファイルに一括変換済み**

## 作成されたファイル

### プログラムファイル
1. **`csv_graph_generator.py`** - メイン分析ツール
2. **`filter_analysis.py`** - フィルタ専用分析ツール  
3. **`quick_plot.py`** - 簡単プロットツール
4. **`batch_csv_to_png.py`** - 基本バッチ変換ツール
5. **`batch_csv_to_png_improved.py`** - 改良版バッチ変換ツール（推奨）
6. **`test_plot.py`** - テスト用プログラム

### 生成されたグラフ（71個のPNGファイル）

#### SINE波信号（各周波数×4フィルタ）
- **10kHz**: `SINE_10kHz.png`, `SINE_10kHz_BEF.png`, `SINE_10kHz_BPF.png`, `SINE_10kHz_HPF.png`
- **20kHz**: `SINE_20kHz.png`, `SINE_20kHz_BEF.png`, `SINE_20kHz_BPF.png`, `SINE_20kHz_HPF.png`
- **40kHz**: `SINE_40kHz.png`, `SINE_40kHz_BEF.png`, `SINE_40kHz_BPF.png`, `SINE_40kHz_HPF.png`
- **50kHz**: `SINE_50kHz.png`, `SINE_50kHz_BEF.png`, `SINE_50kHz_BPF.png`, `SINE_50kHz_HPF.png`
- **80kHz**: `SINE_80kHz.png`, `SINE_80kHz_BEF.png`, `SINE_80kHz_BPF.png`, `SINE_80kHz_HPF.png`
- **100kHz**: `SINE_100kHz.png`, `SINE_100kHz_BEF.png`, `SINE_100kHz_BPF.png`, `SINE_100kHz_HPF.png`
- **200kHz**: `SINE_200kHz.png`, `SINE_200kHz_BEF.png`, `SINE_200kHz_BPF.png`, `SINE_200kHz_HPF.png`
- **400kHz**: `SINE_400kHz.png`, `SINE_400kHz_BEF.png`, `SINE_400kHz_BPF.png`, `SINE_400kHz_HPF.png`
- **800kHz**: `SINE_800kHz.png`, `SINE_800kHz_BEF.png`, `SINE_800kHz_BPF.png`, `SINE_800kHz_HPF.png`
- **1000kHz**: `SINE_1000kHz.png`, `SINE_1000kHz_BEF.png`, `SINE_1000kHz_BPF.png`, `SINE_1000kHz_HPF.png`

#### ガウシアンパルス信号
- `gaussian_pullse_BEF.png`, `gaussian_pullse_BPF.png`, `gaussian_pullse_HPF.png`, `gaussian_pullse_LPF.png`

#### 任意波形信号（各波形×4フィルタ）
- **Wave1**: `original_wave1.png`, `original_wave1_BEF.png`, `original_wave1_BPF.png`, `original_wave1_HPF.png`
- **Wave2**: `original_wave2.png`, `original_wave2_BEF.png`, `original_wave2_BPF.png`, `original_wave2_HPF.png`
- **Wave3**: `original_wave3.png`, `original_wave3_BEF.png`, `original_wave3_BPF.png`, `original_wave3_HPF.png`
- **Wave4**: `original_wave4.png`, `original_wave4_BEF.png`, `original_wave4_BPF.png`, `original_wave4_HPF.png`

#### カットオフテスト信号
- `SINE_CUTOFF_HPF(140kHz).png`, `SINE_CUTOFF_LPF(150kHz).png`
- `SINE_CUTOFF1_BEF(75kHz).png`, `SINE_CUTOFF1_BPF(50kHz).png`  
- `SINE_CUTOFF2_BEF(140kHz).png`, `SINE_CUTOFF2_BPF(200kHz).png`

#### 比較グラフ
- `sine_waves_comparison.png` - SINE波周波数比較
- `gaussian_pulse_comparison.png` - ガウシアンパルス比較
- `original_waves_comparison.png` - 任意波形比較

## 使用方法

### 1. 全CSVファイルの一括変換（推奨）
```bash
.\.venv\Scripts\python.exe batch_csv_to_png_improved.py
```

### 2. 個別ファイルのプロット
```python
from quick_plot import quick_plot
quick_plot('SINE_10kHz.csv')
```

### 3. フィルタ比較分析
```python
from quick_plot import compare_filters
compare_filters('SINE_10kHz')
```

### 4. インタラクティブ分析
```bash
.\.venv\Scripts\python.exe csv_graph_generator.py
.\.venv\Scripts\python.exe filter_analysis.py
.\.venv\Scripts\python.exe quick_plot.py
```

## フィルタタイプ

- **無し** - オリジナル信号
- **BEF** - Band Elimination Filter（帯域除去フィルタ）
- **BPF** - Band Pass Filter（帯域通過フィルタ）
- **HPF** - High Pass Filter（高域通過フィルタ）
- **LPF** - Low Pass Filter（低域通過フィルタ）

## データ形式

### フォーマット1（SINE波、ガウシアンパルス）
- 列3: タイムスタンプ（ns）
- 列4: チャンネル1最小値、列5: チャンネル1最大値
- 列6: チャンネル2最小値、列7: チャンネル2最大値

### フォーマット2（任意波形）
- 列3: タイムスタンプ（ns）
- 列4: チャンネル1電圧値
- 列5: チャンネル2電圧値

## グラフの特徴

- **解像度**: 300 DPI（高品質印刷対応）
- **サイズ**: 12×8インチ
- **カラー**: チャンネル1（青）、チャンネル2（赤）
- **軸**: 時間（μs）vs 電圧（V）
- **グリッド**: 読みやすいグリッド表示
- **凡例**: チャンネル識別のための判例

## 成果

✅ **66個の全CSVファイル**を**71個の高品質PNGグラフ**に変換完了  
✅ **自動フォーマット検出**により異なるCSV構造に対応  
✅ **2チャンネル同時表示**で信号比較が容易  
✅ **フィルタ効果の可視化**でフィルタ性能を確認可能  
✅ **周波数応答分析**で回路特性を把握可能
