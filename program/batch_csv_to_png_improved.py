import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI不要のバックエンドを使用
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# 日本語フォントの設定
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def detect_csv_format(file_path):
    """
    CSVファイルのフォーマットを検出
    """
    try:
        # データ行の開始位置を探す
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # "タイムスタンプ（ns）"が含まれる行を探す
        header_row = None
        for i, line in enumerate(lines):
            if 'タイムスタンプ（ns）' in line:
                header_row = i
                break
        
        if header_row is None:
            return None, None
            
        # ヘッダー行の内容を確認
        header_line = lines[header_row]
        columns = header_line.split(',')
        
        # フォーマットを判定
        if len(columns) >= 6 and '1 最小' in header_line and '1 最大' in header_line:
            # フォーマット1: タイムスタンプ, ch1_min, ch1_max, ch2_min, ch2_max
            return 'format1', header_row + 1
        elif len(columns) >= 4 and columns[3].strip() in ['1', '1,2'] or '1' in columns[3]:
            # フォーマット2: タイムスタンプ, ch1, ch2
            return 'format2', header_row + 1
        else:
            return None, None
            
    except Exception as e:
        print(f"Error detecting format for {file_path}: {e}")
        return None, None

def read_csv_data_auto(file_path):
    """
    CSVファイルのフォーマットを自動検出してデータを読み込む
    """
    format_type, skip_rows = detect_csv_format(file_path)
    
    if format_type is None:
        print(f"Unknown format: {file_path}")
        return None
    
    try:
        if format_type == 'format1':
            # フォーマット1: タイムスタンプ, ch1_min, ch1_max, ch2_min, ch2_max
            df = pd.read_csv(file_path, skiprows=skip_rows, header=None, usecols=[2, 3, 4, 5, 6])
            df.columns = ['timestamp_ns', 'ch1_min', 'ch1_max', 'ch2_min', 'ch2_max']
            
            # データクリーニング
            df = df.dropna()
            df = df[pd.to_numeric(df['timestamp_ns'], errors='coerce').notnull()]
            
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # チャンネルの平均値を計算
            df['ch1_avg'] = (df['ch1_min'] + df['ch1_max']) / 2
            df['ch2_avg'] = (df['ch2_min'] + df['ch2_max']) / 2
            
        elif format_type == 'format2':
            # フォーマット2: タイムスタンプ, ch1, ch2
            df = pd.read_csv(file_path, skiprows=skip_rows, header=None, usecols=[2, 3, 4])
            df.columns = ['timestamp_ns', 'ch1_avg', 'ch2_avg']
            
            # データクリーニング
            df = df.dropna()
            df = df[pd.to_numeric(df['timestamp_ns'], errors='coerce').notnull()]
            
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # タイムスタンプをマイクロ秒に変換
        df['timestamp_us'] = df['timestamp_ns'] / 1000
        
        return df
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def create_dual_channel_plot(df, title, save_path):
    """
    2チャンネルの信号をプロットして保存
    """
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # チャンネル1とチャンネル2をプロット
        ax.plot(df['timestamp_us'], df['ch1_avg'], label='Channel 1', linewidth=1.5, alpha=0.8, color='blue')
        ax.plot(df['timestamp_us'], df['ch2_avg'], label='Channel 2', linewidth=1.5, alpha=0.8, color='red')
        
        # グラフの設定
        ax.set_xlabel('Time (μs)', fontsize=12)
        ax.set_ylabel('Voltage (V)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3)
        
        # 軸の範囲を適切に設定
        ax.set_xlim(df['timestamp_us'].min(), df['timestamp_us'].max())
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()  # メモリ節約のため図を閉じる
        
        return True
        
    except Exception as e:
        print(f"Error creating plot for {title}: {e}")
        return False

def batch_convert_all_csv_improved():
    """
    全てのCSVファイルをPNGに変換（改良版）
    """
    csv_folder = Path("report_template/csv")
    output_folder = Path("graphs")
    output_folder.mkdir(exist_ok=True)
    
    # 全CSVファイルを取得
    csv_files = list(csv_folder.glob("*.csv"))
    
    print(f"Found {len(csv_files)} CSV files to process...")
    
    success_count = 0
    failed_files = []
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"Processing {i}/{len(csv_files)}: {csv_file.name}")
        
        # データ読み込み（自動フォーマット検出）
        df = read_csv_data_auto(csv_file)
        
        if df is not None and len(df) > 0:
            # 出力ファイル名を生成
            output_filename = f"{csv_file.stem}.png"
            save_path = output_folder / output_filename
            
            # グラフタイトル
            title = f"Signal Analysis - {csv_file.stem}"
            
            # プロット作成
            if create_dual_channel_plot(df, title, save_path):
                print(f"  ✓ Saved: {save_path}")
                success_count += 1
            else:
                print(f"  ✗ Failed to create plot")
                failed_files.append(csv_file.name)
        else:
            print(f"  ✗ Failed to read data")
            failed_files.append(csv_file.name)
    
    # 結果サマリー
    print(f"\n=== Conversion Summary ===")
    print(f"Total files processed: {len(csv_files)}")
    print(f"Successfully converted: {success_count}")
    print(f"Failed conversions: {len(failed_files)}")
    
    if failed_files:
        print(f"Failed files:")
        for file in failed_files:
            print(f"  - {file}")
    
    return success_count, failed_files

if __name__ == "__main__":
    print("=== Improved Batch CSV to PNG Converter ===")
    print("Converting all CSV files to PNG format with auto-format detection...")
    
    # 全CSVファイルを変換
    success_count, failed_files = batch_convert_all_csv_improved()
    
    print(f"\n=== Process Complete ===")
    print(f"Check the 'graphs' folder for all generated PNG files.")
    
    # 作成されたファイル一覧を表示
    output_folder = Path("graphs")
    png_files = list(output_folder.glob("*.png"))
    print(f"\nTotal PNG files in graphs folder: {len(png_files)}")
    
    # 新しく作成されたファイルのみ表示
    new_files = [f for f in png_files if not f.name.startswith('SINE_') and 
                 not f.name.startswith('gaussian_') and 
                 not f.name.startswith('test_') and
                 not f.name.endswith('_comparison.png')]
    
    if new_files:
        print("Newly created files:")
        for new_file in sorted(new_files):
            print(f"  - {new_file.name}")
