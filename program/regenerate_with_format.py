import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI不要のバックエンドを使用
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os

# 日本語フォントの設定
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

def detect_csv_format(file_path):
    """CSVファイルのフォーマットを検出"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        header_row = None
        for i, line in enumerate(lines):
            if 'タイムスタンプ（ns）' in line:
                header_row = i
                break
        
        if header_row is None:
            return None, None
            
        header_line = lines[header_row]
        columns = header_line.split(',')
        
        if len(columns) >= 6 and '1 最小' in header_line and '1 最大' in header_line:
            return 'format1', header_row + 1
        elif len(columns) >= 4 and columns[3].strip() in ['1', '1,2'] or '1' in columns[3]:
            return 'format2', header_row + 1
        else:
            return None, None
            
    except Exception as e:
        print(f"Error detecting format for {file_path}: {e}")
        return None, None

def read_csv_data_auto(file_path):
    """CSVファイルのフォーマットを自動検出してデータを読み込む"""
    format_type, skip_rows = detect_csv_format(file_path)
    
    if format_type is None:
        print(f"Unknown format: {file_path}")
        return None
    
    try:
        if format_type == 'format1':
            df = pd.read_csv(file_path, skiprows=skip_rows, header=None, usecols=[2, 3, 4, 5, 6])
            df.columns = ['timestamp_ns', 'ch1_min', 'ch1_max', 'ch2_min', 'ch2_max']
            
            df = df.dropna()
            df = df[pd.to_numeric(df['timestamp_ns'], errors='coerce').notnull()]
            
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df['ch1_avg'] = (df['ch1_min'] + df['ch1_max']) / 2
            df['ch2_avg'] = (df['ch2_min'] + df['ch2_max']) / 2
            
        elif format_type == 'format2':
            df = pd.read_csv(file_path, skiprows=skip_rows, header=None, usecols=[2, 3, 4])
            df.columns = ['timestamp_ns', 'ch1_avg', 'ch2_avg']
            
            df = df.dropna()
            df = df[pd.to_numeric(df['timestamp_ns'], errors='coerce').notnull()]
            
            for col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['timestamp_us'] = df['timestamp_ns'] / 1000
        
        return df
        
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def parse_filename(filename):
    """ファイル名から信号タイプとフィルタを解析"""
    stem = Path(filename).stem
    
    # 信号タイプの判定 - CUTOFFを最初にチェック
    if 'CUTOFF' in stem:
        # カットオフテストの場合 - 他と同じフォーマットにする
        if stem == 'SINE_CUTOFF_LPF(150kHz)':
            signal_type = "150kHz"  # LPF遮断周波数
            filter_type = "LPF"
        elif stem == 'SINE_CUTOFF_HPF(140kHz)':
            signal_type = "140kHz"  # HPF遮断周波数
            filter_type = "HPF"
        elif stem == 'SINE_CUTOFF1_BEF(75kHz)':
            signal_type = "75kHz"   # BEF遮断周波数
            filter_type = "BEF"
        elif stem == 'SINE_CUTOFF1_BPF(50kHz)':
            signal_type = "50kHz"   # BPF遮断周波数
            filter_type = "BPF"
        elif stem == 'SINE_CUTOFF2_BEF(140kHz)':
            signal_type = "140kHz"  # BEF遮断周波数
            filter_type = "BEF"
        elif stem == 'SINE_CUTOFF2_BPF(200kHz)':
            signal_type = "200kHz"  # BPF遮断周波数
            filter_type = "BPF"
        else:
            signal_type = "Cutoff test"
            filter_type = "Test"
    elif stem.startswith('SINE_') and 'kHz' in stem:
        # SINE波の場合
        parts = stem.split('_')
        frequency = parts[1]  # 例: "10kHz"
        signal_type = frequency
        
        # フィルタの判定
        if len(parts) > 2:
            filter_type = parts[2]  # BEF, BPF, HPF, LPF
        else:
            filter_type = "Original"
            
    elif stem.startswith('gaussian'):
        signal_type = "Gaussian pulse"
        if '_' in stem:
            filter_part = stem.split('_')[-1]
            filter_type = filter_part if filter_part in ['BEF', 'BPF', 'HPF', 'LPF'] else "Original"
        else:
            filter_type = "Original"
            
    elif stem.startswith('original_wave'):
        # 任意波形の場合
        parts = stem.split('_')
        if len(parts) >= 2:
            # wave1, wave2, wave3, wave4 の形で取得
            if parts[1].startswith('wave'):
                wave_num = parts[1]  # wave1, wave2, etc.
            else:
                wave_num = f"wave{parts[1]}"
            
            signal_type = f"Original {wave_num}"
            
            if len(parts) > 2:
                filter_type = parts[2]
            else:
                filter_type = "Original"
        else:
            signal_type = "Original wave"
            filter_type = "Original"
    
    else:
        signal_type = stem
        filter_type = "Original"
    
    return signal_type, filter_type

def create_formatted_title(signal_type, filter_type):
    """フォーマットされたタイトルを作成"""
    # フィルタタイプの処理
    if filter_type == "Original":
        filter_part = "Original"
    else:
        filter_part = filter_type
    
    # タイトルフォーマット: (周波数の値 or Original wave or gaussian pulse)-(フィルタの種類)-(Input/output characteristic)
    title = f"{signal_type} - {filter_part} - Input/Output Characteristic"
    
    return title

def create_dual_channel_plot_formatted(df, signal_type, filter_type, save_path):
    """新しいフォーマットで2チャンネルの信号をプロット"""
    try:
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # チャンネル1とチャンネル2をプロット
        ax.plot(df['timestamp_us'], df['ch1_avg'], label='Channel 1 (Input)', linewidth=1.5, alpha=0.8, color='blue')
        ax.plot(df['timestamp_us'], df['ch2_avg'], label='Channel 2 (Output)', linewidth=1.5, alpha=0.8, color='red')
        
        # フォーマットされたタイトルを作成
        title = create_formatted_title(signal_type, filter_type)
        
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
        plt.close()
        
        return True
        
    except Exception as e:
        print(f"Error creating plot: {e}")
        return False

def batch_regenerate_all_with_new_format():
    """新しいタイトルフォーマットで全てのCSVファイルを再生成"""
    csv_folder = Path("report_template/csv")
    output_folder = Path("graphs")  # 元のgraphsフォルダを更新
    
    # 既存のgraphsフォルダをバックアップ
    backup_folder = Path("graphs_backup")
    if output_folder.exists() and not backup_folder.exists():
        import shutil
        shutil.copytree(output_folder, backup_folder)
        print(f"Original graphs backed up to: {backup_folder}")
    
    # graphsフォルダをクリア
    if output_folder.exists():
        import shutil
        shutil.rmtree(output_folder)
    output_folder.mkdir(exist_ok=True)
    
    csv_files = list(csv_folder.glob("*.csv"))
    
    print(f"Found {len(csv_files)} CSV files to regenerate with new format...")
    
    success_count = 0
    failed_files = []
    
    for i, csv_file in enumerate(csv_files, 1):
        print(f"Processing {i}/{len(csv_files)}: {csv_file.name}")
        
        # ファイル名から信号タイプとフィルタを解析
        signal_type, filter_type = parse_filename(csv_file.name)
        print(f"  Signal: {signal_type}, Filter: {filter_type}")
        
        # データ読み込み
        df = read_csv_data_auto(csv_file)
        
        if df is not None and len(df) > 0:
            # 新しい命名規則でファイル名を作成
            safe_signal = signal_type.replace(' ', '_').replace('/', '_')
            safe_filter = filter_type.replace(' ', '_')
            output_filename = f"{safe_signal}_{safe_filter}_characteristic.png"
            save_path = output_folder / output_filename
            
            # プロット作成
            if create_dual_channel_plot_formatted(df, signal_type, filter_type, save_path):
                print(f"  ✓ Saved: {save_path}")
                success_count += 1
            else:
                print(f"  ✗ Failed to create plot")
                failed_files.append(csv_file.name)
        else:
            print(f"  ✗ Failed to read data")
            failed_files.append(csv_file.name)
    
    # 結果サマリー
    print(f"\n=== Regeneration Summary ===")
    print(f"Total files processed: {len(csv_files)}")
    print(f"Successfully regenerated: {success_count}")
    print(f"Failed regenerations: {len(failed_files)}")
    
    if failed_files:
        print(f"Failed files:")
        for file in failed_files:
            print(f"  - {file}")
    
    # 新しいフォルダの内容を確認
    new_files = list(output_folder.glob("*.png"))
    print(f"\nGenerated {len(new_files)} new formatted graphs in: {output_folder}")
    
    return success_count, failed_files

if __name__ == "__main__":
    print("=== Batch Regeneration with New Title Format ===")
    print("New format: (Signal Type) - (Filter Type) - Input/Output Characteristic")
    
    # 全CSVファイルを新フォーマットで再生成
    success_count, failed_files = batch_regenerate_all_with_new_format()
    
    print(f"\n=== Process Complete ===")
    print(f"All graphs regenerated with new title format!")
    print(f"Check the 'graphs_formatted' folder for all new PNG files.")
