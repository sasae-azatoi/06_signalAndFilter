import os
import glob
import numpy as np
import matplotlib.pyplot as plt

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

    # 2列目以降を全てプロット
    plt.figure(figsize=(8, 4))
    for i in range(1, data.shape[1]):
        plt.plot(freqs, data[:, i], label=f'col{i+1}')
    plt.xlabel('Frequency [Hz]')
    plt.ylabel('Value')
    plt.legend()
    plt.tight_layout()
    plt.savefig(png_path)
    plt.close()
