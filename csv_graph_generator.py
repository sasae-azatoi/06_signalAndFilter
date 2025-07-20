import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
from pathlib import Path

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

def plot_dual_channel(df, title, save_path=None):
    """
    2チャンネルの信号をプロット
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # チャンネル1とチャンネル2をプロット
    ax.plot(df['timestamp_us'], df['ch1_avg'], label='Channel 1', linewidth=1.5, alpha=0.8)
    ax.plot(df['timestamp_us'], df['ch2_avg'], label='Channel 2', linewidth=1.5, alpha=0.8)
    
    # グラフの設定
    ax.set_xlabel('Time (μs)', fontsize=12)
    ax.set_ylabel('Voltage (V)', fontsize=12)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    
    # 軸の範囲を適切に設定
    ax.set_xlim(df['timestamp_us'].min(), df['timestamp_us'].max())
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Graph saved: {save_path}")
    
    plt.show()

def plot_comparison(df_list, labels, title, save_path=None):
    """
    複数のCSVファイルのチャンネル1を比較プロット
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(df_list)))
    
    # チャンネル1の比較
    for i, (df, label) in enumerate(zip(df_list, labels)):
        if df is not None:
            ax1.plot(df['timestamp_us'], df['ch1_avg'], 
                    label=f'Ch1 - {label}', color=colors[i], linewidth=1.2, alpha=0.8)
    
    ax1.set_xlabel('Time (μs)', fontsize=12)
    ax1.set_ylabel('Voltage (V)', fontsize=12)
    ax1.set_title('Channel 1 Comparison', fontsize=13, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # チャンネル2の比較
    for i, (df, label) in enumerate(zip(df_list, labels)):
        if df is not None:
            ax2.plot(df['timestamp_us'], df['ch2_avg'], 
                    label=f'Ch2 - {label}', color=colors[i], linewidth=1.2, alpha=0.8)
    
    ax2.set_xlabel('Time (μs)', fontsize=12)
    ax2.set_ylabel('Voltage (V)', fontsize=12)
    ax2.set_title('Channel 2 Comparison', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Comparison graph saved: {save_path}")
    
    plt.show()

def main():
    # CSVフォルダのパス
    csv_folder = Path("report_template/csv")
    output_folder = Path("graphs")
    output_folder.mkdir(exist_ok=True)
    
    # 利用可能なCSVファイルを表示
    csv_files = list(csv_folder.glob("*.csv"))
    print("Available CSV files:")
    for i, file in enumerate(csv_files):
        print(f"{i+1}: {file.name}")
    
    print("\nOptions:")
    print("1. Plot single CSV file (dual channel)")
    print("2. Compare multiple CSV files")
    print("3. Plot all SINE frequency files")
    print("4. Plot filter comparison for a specific signal")
    
    choice = input("\nSelect option (1-4): ")
    
    if choice == "1":
        # 単一ファイルプロット
        file_index = int(input("Select CSV file number: ")) - 1
        if 0 <= file_index < len(csv_files):
            selected_file = csv_files[file_index]
            df = read_csv_data(selected_file)
            if df is not None:
                title = f"Signal Analysis - {selected_file.stem}"
                save_path = output_folder / f"{selected_file.stem}_dual_channel.png"
                plot_dual_channel(df, title, save_path)
    
    elif choice == "2":
        # 複数ファイル比較
        file_indices = input("Select CSV file numbers (comma-separated): ")
        indices = [int(x.strip()) - 1 for x in file_indices.split(",")]
        
        df_list = []
        labels = []
        for idx in indices:
            if 0 <= idx < len(csv_files):
                df = read_csv_data(csv_files[idx])
                df_list.append(df)
                labels.append(csv_files[idx].stem)
        
        if df_list:
            title = "Multi-File Signal Comparison"
            save_path = output_folder / "comparison_plot.png"
            plot_comparison(df_list, labels, title, save_path)
    
    elif choice == "3":
        # SINE周波数ファイル全て
        sine_files = [f for f in csv_files if "SINE_" in f.name and "kHz.csv" in f.name]
        sine_files.sort(key=lambda x: float(x.stem.split('_')[1].replace('kHz', '')))
        
        df_list = []
        labels = []
        for file in sine_files:
            df = read_csv_data(file)
            if df is not None:
                df_list.append(df)
                labels.append(file.stem)
        
        if df_list:
            title = "SINE Wave Frequency Comparison"
            save_path = output_folder / "sine_frequency_comparison.png"
            plot_comparison(df_list, labels, title, save_path)
    
    elif choice == "4":
        # フィルタ比較
        signal_name = input("Enter signal name (e.g., SINE_10kHz, gaussian_pullse): ")
        filter_types = ["", "_BEF", "_BPF", "_HPF", "_LPF"]
        
        df_list = []
        labels = []
        for filter_type in filter_types:
            file_path = csv_folder / f"{signal_name}{filter_type}.csv"
            if file_path.exists():
                df = read_csv_data(file_path)
                if df is not None:
                    df_list.append(df)
                    filter_name = filter_type.replace("_", "") if filter_type else "Original"
                    labels.append(filter_name)
        
        if df_list:
            title = f"Filter Comparison - {signal_name}"
            save_path = output_folder / f"{signal_name}_filter_comparison.png"
            plot_comparison(df_list, labels, title, save_path)

if __name__ == "__main__":
    main()
