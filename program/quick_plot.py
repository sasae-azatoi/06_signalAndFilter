import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

def read_csv_data(file_path):
    """CSVファイルからデータを読み込む"""
    try:
        df = pd.read_csv(file_path, skiprows=21, header=None, usecols=[2, 3, 4, 5, 6])
        df.columns = ['timestamp_ns', 'ch1_min', 'ch1_max', 'ch2_min', 'ch2_max']
        df = df.dropna()
        df = df[pd.to_numeric(df['timestamp_ns'], errors='coerce').notnull()]
        
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        df['timestamp_us'] = df['timestamp_ns'] / 1000
        df['ch1_avg'] = (df['ch1_min'] + df['ch1_max']) / 2
        df['ch2_avg'] = (df['ch2_min'] + df['ch2_max']) / 2
        
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def quick_plot(csv_filename):
    """指定されたCSVファイルを素早くプロット"""
    csv_folder = Path("report_template/csv")
    file_path = csv_folder / csv_filename
    
    if not file_path.exists():
        print(f"File not found: {file_path}")
        return
    
    df = read_csv_data(file_path)
    if df is None:
        return
    
    plt.figure(figsize=(12, 8))
    plt.plot(df['timestamp_us'], df['ch1_avg'], label='Channel 1', linewidth=1.5, alpha=0.8)
    plt.plot(df['timestamp_us'], df['ch2_avg'], label='Channel 2', linewidth=1.5, alpha=0.8)
    
    plt.xlabel('Time (μs)')
    plt.ylabel('Voltage (V)')
    plt.title(f'Signal Analysis - {csv_filename}')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # 保存
    output_folder = Path("graphs")
    output_folder.mkdir(exist_ok=True)
    save_path = output_folder / f"{Path(csv_filename).stem}_quick_plot.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Graph saved: {save_path}")
    
    plt.show()

def compare_filters(signal_name):
    """指定された信号のフィルタ比較"""
    csv_folder = Path("report_template/csv")
    
    plt.figure(figsize=(15, 10))
    
    # 2x2のサブプロット
    plt.subplot(2, 2, 1)
    plot_channel_comparison(csv_folder, signal_name, 1, "Channel 1")
    
    plt.subplot(2, 2, 2) 
    plot_channel_comparison(csv_folder, signal_name, 2, "Channel 2")
    
    plt.subplot(2, 2, 3)
    plot_filter_effect(csv_folder, signal_name, ["", "_HPF", "_LPF"], "HP/LP Filter Comparison")
    
    plt.subplot(2, 2, 4)
    plot_filter_effect(csv_folder, signal_name, ["", "_BPF", "_BEF"], "BP/BE Filter Comparison")
    
    plt.suptitle(f'Complete Filter Analysis - {signal_name}', fontsize=16)
    plt.tight_layout()
    
    # 保存
    output_folder = Path("graphs")
    output_folder.mkdir(exist_ok=True)
    save_path = output_folder / f"{signal_name}_filter_comparison.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Filter comparison saved: {save_path}")
    
    plt.show()

def plot_channel_comparison(csv_folder, signal_name, channel, title):
    """チャンネル別のフィルタ比較"""
    filters = [("", "Original"), ("_BEF", "BEF"), ("_BPF", "BPF"), ("_HPF", "HPF"), ("_LPF", "LPF")]
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (suffix, label) in enumerate(filters):
        file_path = csv_folder / f"{signal_name}{suffix}.csv"
        if file_path.exists():
            df = read_csv_data(file_path)
            if df is not None:
                col = f'ch{channel}_avg'
                plt.plot(df['timestamp_us'], df[col], label=label, color=colors[i], linewidth=1.2, alpha=0.8)
    
    plt.xlabel('Time (μs)')
    plt.ylabel('Voltage (V)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)

def plot_filter_effect(csv_folder, signal_name, filter_suffixes, title):
    """特定フィルタの効果比較"""
    colors = ['blue', 'orange', 'purple']
    labels = {'': 'Original', '_HPF': 'HPF', '_LPF': 'LPF', '_BPF': 'BPF', '_BEF': 'BEF'}
    
    for i, suffix in enumerate(filter_suffixes):
        file_path = csv_folder / f"{signal_name}{suffix}.csv"
        if file_path.exists():
            df = read_csv_data(file_path)
            if df is not None:
                plt.plot(df['timestamp_us'], df['ch1_avg'], 
                        label=labels.get(suffix, suffix), color=colors[i], linewidth=1.5, alpha=0.8)
    
    plt.xlabel('Time (μs)')
    plt.ylabel('Voltage (V)')
    plt.title(title)
    plt.legend()
    plt.grid(True, alpha=0.3)

# 使用例
if __name__ == "__main__":
    print("Quick Plot Examples:")
    print("1. quick_plot('SINE_10kHz.csv')")
    print("2. compare_filters('SINE_10kHz')")
    print("3. quick_plot('gaussian_pullse.csv')")
    print("4. compare_filters('gaussian_pullse')")
    print()
    
    # デモンストレーション
    # quick_plot('SINE_10kHz.csv')
    # compare_filters('SINE_10kHz')
    
    # インタラクティブモード
    choice = input("Enter 'q' for quick plot or 'c' for filter comparison: ")
    if choice.lower() == 'q':
        filename = input("Enter CSV filename (e.g., SINE_10kHz.csv): ")
        quick_plot(filename)
    elif choice.lower() == 'c':
        signal = input("Enter signal name (e.g., SINE_10kHz): ")
        compare_filters(signal)
