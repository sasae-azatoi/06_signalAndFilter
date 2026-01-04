import os
import glob
import numpy as np
import matplotlib.pyplot as plt

# 日本語フォントの設定
plt.rcParams['font.sans-serif'] = ['MS Gothic', 'Yu Gothic', 'Meiryo']
plt.rcParams['axes.unicode_minus'] = False

# s2pファイルのディレクトリ
s2p_dir = os.path.join(os.path.dirname(__file__), '../report_template/s2p')
fig_dir = os.path.join(os.path.dirname(__file__), '../report_template/fig')
os.makedirs(fig_dir, exist_ok=True)

# s2pファイルを全て取得
s2p_files = glob.glob(os.path.join(s2p_dir, '*.s2p'))

for s2p_path in s2p_files:

    # ファイル名から出力画像名を決定
    basename = os.path.splitext(os.path.basename(s2p_path))[0]
    png_path = os.path.join(fig_dir, f'{basename}.png')

    # s2pファイルの読み込み
    data = []
    with open(s2p_path, encoding='utf-8') as f:
        for line in f:
            if line.startswith('!') or line.startswith('#') or line.strip() == '':
                continue
            parts = line.split()
            if len(parts) < 5:
                continue
            data.append([float(x) for x in parts])

    data = np.array(data)
    if data.shape[0] == 0:
        continue
    
    freqs = data[:, 0]
    s21_mag = data[:, 3]  # S21のマグニチュード
    s21_phase = data[:, 4]  # S21の位相
    
    # S21のGainに変換（dB）
    s21_gain_db = 20 * np.log10(s21_mag)
    
    # 2つのサブプロットを作成
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    
    # Gainのプロット
    ax1.plot(freqs / 1000, s21_gain_db, 'b-', linewidth=2)
    ax1.set_xlabel('周波数 [kHz]', fontsize=12)
    ax1.set_ylabel('S21 ゲイン [dB]', fontsize=12)
    ax1.set_title(f'{basename} - S21 周波数特性', fontsize=14)
    ax1.grid(True, alpha=0.3, which='major')
    ax1.grid(True, alpha=0.15, which='minor', linestyle='--')
    ax1.minorticks_on()
    
    # Phaseのプロット
    ax2.plot(freqs / 1000, s21_phase, 'r-', linewidth=2)
    ax2.set_xlabel('周波数 [kHz]', fontsize=12)
    ax2.set_ylabel('S21 位相 [度]', fontsize=12)
    ax2.grid(True, alpha=0.3, which='major')
    ax2.grid(True, alpha=0.15, which='minor', linestyle='--')
    ax2.minorticks_on()
    
    plt.tight_layout()
    plt.savefig(png_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f'生成完了: {png_path}')
