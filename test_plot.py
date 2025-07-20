import pandas as pd
import matplotlib
matplotlib.use('Agg')  # GUI不要のバックエンドを使用
import matplotlib.pyplot as plt
from pathlib import Path

def test_read_csv():
    """CSVファイルの読み込みテスト"""
    csv_folder = Path("report_template/csv")
    test_file = csv_folder / "SINE_10kHz.csv"
    
    print(f"Testing file: {test_file}")
    print(f"File exists: {test_file.exists()}")
    
    if not test_file.exists():
        print("File not found!")
        return None
        
    try:
        # ヘッダーをスキップしてデータ部分のみ読み込み
        df = pd.read_csv(test_file, skiprows=21, header=None, usecols=[2, 3, 4, 5, 6])
        print(f"Data shape: {df.shape}")
        print(f"First 5 rows:")
        print(df.head())
        
        df.columns = ['timestamp_ns', 'ch1_min', 'ch1_max', 'ch2_min', 'ch2_max']
        
        # 数値でない行を削除
        df = df.dropna()
        df = df[pd.to_numeric(df['timestamp_ns'], errors='coerce').notnull()]
        
        print(f"After cleaning shape: {df.shape}")
        
        # データ型を数値に変換
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # タイムスタンプをマイクロ秒に変換
        df['timestamp_us'] = df['timestamp_ns'] / 1000
        
        # チャンネルの平均値を計算
        df['ch1_avg'] = (df['ch1_min'] + df['ch1_max']) / 2
        df['ch2_avg'] = (df['ch2_min'] + df['ch2_max']) / 2
        
        print(f"Final data shape: {df.shape}")
        print(f"Time range: {df['timestamp_us'].min():.2f} to {df['timestamp_us'].max():.2f} μs")
        print(f"Ch1 voltage range: {df['ch1_avg'].min():.3f} to {df['ch1_avg'].max():.3f} V")
        print(f"Ch2 voltage range: {df['ch2_avg'].min():.3f} to {df['ch2_avg'].max():.3f} V")
        
        return df
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def test_plot(df):
    """プロットテスト"""
    if df is None:
        print("No data to plot")
        return
        
    try:
        plt.figure(figsize=(12, 8))
        plt.plot(df['timestamp_us'], df['ch1_avg'], label='Channel 1', linewidth=1.5, alpha=0.8)
        plt.plot(df['timestamp_us'], df['ch2_avg'], label='Channel 2', linewidth=1.5, alpha=0.8)
        
        plt.xlabel('Time (μs)')
        plt.ylabel('Voltage (V)')
        plt.title('Test Plot - SINE_10kHz')
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # 保存
        output_folder = Path("graphs")
        output_folder.mkdir(exist_ok=True)
        save_path = output_folder / "test_plot.png"
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Test plot saved: {save_path}")
        plt.close()
        
        print("Plot test completed successfully!")
        
    except Exception as e:
        print(f"Plot error: {e}")

if __name__ == "__main__":
    print("=== CSV Graph Generator Test ===")
    df = test_read_csv()
    test_plot(df)
    print("Test completed!")
