from regenerate_with_format import parse_filename

# テスト用のファイル名
test_files = [
    "original_wave1.csv",
    "original_wave1_BEF.csv", 
    "SINE_CUTOFF_LPF(150kHz).csv",
    "SINE_CUTOFF_HPF(140kHz).csv",
    "SINE_CUTOFF1_BEF(75kHz).csv",
    "SINE_CUTOFF1_BPF(50kHz).csv",
    "SINE_CUTOFF2_BEF(140kHz).csv",
    "SINE_CUTOFF2_BPF(200kHz).csv"
]

print("=== ファイル名解析テスト ===")
for filename in test_files:
    signal_type, filter_type = parse_filename(filename)
    print(f"{filename} -> Signal: '{signal_type}', Filter: '{filter_type}'")
