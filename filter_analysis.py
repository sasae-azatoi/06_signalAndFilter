import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
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

def create_filter_comparison(signal_name):
    """
    指定された信号のフィルタ比較グラフを作成
    """
    csv_folder = Path("report_template/csv")
    output_folder = Path("graphs")
    output_folder.mkdir(exist_ok=True)
    
    filter_configs = [
        ("", "Original", "blue"),
        ("_BEF", "BEF (Band Elimination)", "red"),
        ("_BPF", "BPF (Band Pass)", "green"),
        ("_HPF", "HPF (High Pass)", "orange"),
        ("_LPF", "LPF (Low Pass)", "purple")
    ]
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # チャンネル1とチャンネル2の全フィルタ比較
    for filter_suffix, filter_name, color in filter_configs:
        file_path = csv_folder / f"{signal_name}{filter_suffix}.csv"
        if file_path.exists():
            df = read_csv_data(file_path)
            if df is not None:
                ax1.plot(df['timestamp_us'], df['ch1_avg'], 
                        label=filter_name, color=color, linewidth=1.5, alpha=0.8)
                ax2.plot(df['timestamp_us'], df['ch2_avg'], 
                        label=filter_name, color=color, linewidth=1.5, alpha=0.8)
    
    # チャンネル1設定
    ax1.set_xlabel('Time (μs)')
    ax1.set_ylabel('Voltage (V)')
    ax1.set_title(f'Channel 1 - {signal_name}')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # チャンネル2設定
    ax2.set_xlabel('Time (μs)')
    ax2.set_ylabel('Voltage (V)')
    ax2.set_title(f'Channel 2 - {signal_name}')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 個別フィルタ効果の表示
    original_file = csv_folder / f"{signal_name}.csv"
    if original_file.exists():
        original_df = read_csv_data(original_file)
        if original_df is not None:
            # HPFとLPFの効果比較
            hpf_file = csv_folder / f"{signal_name}_HPF.csv"
            lpf_file = csv_folder / f"{signal_name}_LPF.csv"
            
            ax3.plot(original_df['timestamp_us'], original_df['ch1_avg'], 
                    label='Original', color='blue', linewidth=2)
            
            if hpf_file.exists():
                hpf_df = read_csv_data(hpf_file)
                if hpf_df is not None:
                    ax3.plot(hpf_df['timestamp_us'], hpf_df['ch1_avg'], 
                            label='HPF', color='orange', linewidth=1.5, alpha=0.8)
            
            if lpf_file.exists():
                lpf_df = read_csv_data(lpf_file)
                if lpf_df is not None:
                    ax3.plot(lpf_df['timestamp_us'], lpf_df['ch1_avg'], 
                            label='LPF', color='purple', linewidth=1.5, alpha=0.8)
            
            ax3.set_xlabel('Time (μs)')
            ax3.set_ylabel('Voltage (V)')
            ax3.set_title('HPF vs LPF Comparison (Ch1)')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
            
            # BPFとBEFの効果比較
            ax4.plot(original_df['timestamp_us'], original_df['ch1_avg'], 
                    label='Original', color='blue', linewidth=2)
            
            bpf_file = csv_folder / f"{signal_name}_BPF.csv"
            bef_file = csv_folder / f"{signal_name}_BEF.csv"
            
            if bpf_file.exists():
                bpf_df = read_csv_data(bpf_file)
                if bpf_df is not None:
                    ax4.plot(bpf_df['timestamp_us'], bpf_df['ch1_avg'], 
                            label='BPF', color='green', linewidth=1.5, alpha=0.8)
            
            if bef_file.exists():
                bef_df = read_csv_data(bef_file)
                if bef_df is not None:
                    ax4.plot(bef_df['timestamp_us'], bef_df['ch1_avg'], 
                            label='BEF', color='red', linewidth=1.5, alpha=0.8)
            
            ax4.set_xlabel('Time (μs)')
            ax4.set_ylabel('Voltage (V)')
            ax4.set_title('BPF vs BEF Comparison (Ch1)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
    
    plt.suptitle(f'Filter Analysis - {signal_name}', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # 保存
    save_path = output_folder / f"{signal_name}_complete_analysis.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Complete analysis saved: {save_path}")
    plt.show()

def create_frequency_response_comparison():
    """
    周波数応答の比較
    """
    csv_folder = Path("report_template/csv")
    output_folder = Path("graphs")
    output_folder.mkdir(exist_ok=True)
    
    # SINE波ファイルのリスト
    frequencies = [10, 20, 40, 50, 80, 100, 200, 400, 800, 1000]  # kHz
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    filter_types = [
        ("_HPF", "HPF", ax1),
        ("_LPF", "LPF", ax2),
        ("_BPF", "BPF", ax3),
        ("_BEF", "BEF", ax4)
    ]
    
    colors = plt.cm.viridis(np.linspace(0, 1, len(frequencies)))
    
    for filter_suffix, filter_name, ax in filter_types:
        for i, freq in enumerate(frequencies):
            file_path = csv_folder / f"SINE_{freq}kHz{filter_suffix}.csv"
            if file_path.exists():
                df = read_csv_data(file_path)
                if df is not None:
                    ax.plot(df['timestamp_us'], df['ch1_avg'], 
                           label=f'{freq}kHz', color=colors[i], linewidth=1.2, alpha=0.8)
        
        ax.set_xlabel('Time (μs)')
        ax.set_ylabel('Voltage (V)')
        ax.set_title(f'{filter_name} Frequency Response')
        ax.legend(fontsize=8, ncol=2)
        ax.grid(True, alpha=0.3)
    
    plt.suptitle('Filter Frequency Response Comparison', fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    save_path = output_folder / "frequency_response_comparison.png"
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"Frequency response comparison saved: {save_path}")
    plt.show()

if __name__ == "__main__":
    print("Signal and Filter Analysis")
    print("1. Analyze specific signal with all filters")
    print("2. Compare frequency response across all filters")
    print("3. Analyze gaussian pulse")
    print("4. Analyze original waves")
    
    choice = input("Select option (1-4): ")
    
    if choice == "1":
        signal = input("Enter signal name (e.g., SINE_10kHz): ")
        create_filter_comparison(signal)
    
    elif choice == "2":
        create_frequency_response_comparison()
    
    elif choice == "3":
        create_filter_comparison("gaussian_pullse")
    
    elif choice == "4":
        for i in range(1, 5):
            create_filter_comparison(f"original_wave{i}")
