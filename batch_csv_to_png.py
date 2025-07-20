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

def read_csv_data(file_path):
    """
    CSVファイルからデータを読み込む
    """
    try:
        # ヘッダーをスキップしてデータ部分のみ読み込み
        df = pd.read_csv(file_path, skiprows=21, header=None, usecols=[2, 3, 4, 5, 6])
        df.columns = ['timestamp_ns', 'ch1_min', 'ch1_max', 'ch2_min', 'ch2_max']
        
        # 数値でない行を削除
        df = df.dropna()
        df = df[pd.to_numeric(df['timestamp_ns'], errors='coerce').notnull()]
        
        # データ型を数値に変換
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # タイムスタンプをマイクロ秒に変換
        df['timestamp_us'] = df['timestamp_ns'] / 1000
        
        # チャンネルの平均値を計算
        df['ch1_avg'] = (df['ch1_min'] + df['ch1_max']) / 2
        df['ch2_avg'] = (df['ch2_min'] + df['ch2_max']) / 2
        
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

def batch_convert_all_csv():
    """
    全てのCSVファイルをPNGに変換
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
        
        # データ読み込み
        df = read_csv_data(csv_file)
        
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

def create_signal_groups():
    """
    信号タイプ別にグループ化したグラフも作成
    """
    csv_folder = Path("report_template/csv")
    output_folder = Path("graphs")
    
    # 信号グループを定義
    signal_groups = {
        'sine_waves': [],
        'gaussian_pulse': [],
        'original_waves': [],
        'cutoff_tests': []
    }
    
    # CSVファイルをグループ分け
    for csv_file in csv_folder.glob("*.csv"):
        filename = csv_file.stem.lower()
        
        if filename.startswith('sine_') and 'khz' in filename:
            signal_groups['sine_waves'].append(csv_file)
        elif filename.startswith('gaussian'):
            signal_groups['gaussian_pulse'].append(csv_file)
        elif filename.startswith('original_wave'):
            signal_groups['original_waves'].append(csv_file)
        elif 'cutoff' in filename:
            signal_groups['cutoff_tests'].append(csv_file)
    
    # 各グループの比較グラフを作成
    for group_name, files in signal_groups.items():
        if len(files) > 1:
            print(f"\nCreating comparison for {group_name} group...")
            create_group_comparison(files, group_name, output_folder)

def create_group_comparison(files, group_name, output_folder):
    """
    グループ内のファイルを比較するグラフを作成
    """
    try:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 12))
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(files)))
        
        for i, file in enumerate(files):
            df = read_csv_data(file)
            if df is not None and len(df) > 0:
                label = file.stem
                
                # チャンネル1
                ax1.plot(df['timestamp_us'], df['ch1_avg'], 
                        label=label, color=colors[i], linewidth=1.2, alpha=0.8)
                
                # チャンネル2
                ax2.plot(df['timestamp_us'], df['ch2_avg'], 
                        label=label, color=colors[i], linewidth=1.2, alpha=0.8)
        
        # チャンネル1設定
        ax1.set_xlabel('Time (μs)')
        ax1.set_ylabel('Voltage (V)')
        ax1.set_title(f'Channel 1 Comparison - {group_name.replace("_", " ").title()}')
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax1.grid(True, alpha=0.3)
        
        # チャンネル2設定
        ax2.set_xlabel('Time (μs)')
        ax2.set_ylabel('Voltage (V)')
        ax2.set_title(f'Channel 2 Comparison - {group_name.replace("_", " ").title()}')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # 保存
        save_path = output_folder / f"{group_name}_comparison.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ Group comparison saved: {save_path}")
        
    except Exception as e:
        print(f"  ✗ Error creating group comparison for {group_name}: {e}")

if __name__ == "__main__":
    print("=== Batch CSV to PNG Converter ===")
    print("Converting all CSV files to PNG format...")
    
    # 全CSVファイルを変換
    success_count, failed_files = batch_convert_all_csv()
    
    # グループ比較グラフも作成
    print("\nCreating signal group comparisons...")
    create_signal_groups()
    
    print(f"\n=== Process Complete ===")
    print(f"Check the 'graphs' folder for all generated PNG files.")
    
    # 作成されたファイル一覧を表示
    output_folder = Path("graphs")
    png_files = list(output_folder.glob("*.png"))
    print(f"\nGenerated {len(png_files)} PNG files:")
    for png_file in sorted(png_files):
        print(f"  - {png_file.name}")
