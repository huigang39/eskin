import numpy as np
import pandas as pd
import os
import glob

def extract_features(data):
    # 计算标准差
    std_dev = np.std(data)

    # 计算均方根
    rms = np.sqrt(np.mean(data**2))

    # 计算最小值和最大值
    min_val = np.min(data)
    max_val = np.max(data)

    # 计算零交叉率
    zero_crossings = np.sum(np.diff(np.sign(data)) != 0)

    # 计算均振幅变化
    mean_amp_change = np.mean(np.abs(np.diff(data)))

    # 计算振幅第一脉冲
    amp_first_pulse = np.abs(data[0])

    # 计算平均绝对值
    mean_abs_val = np.mean(np.abs(data))

    # 计算波形长度
    waveform_length = np.sum(np.abs(np.diff(data)))

    # 计算威利逊振幅
    wilson_amp = np.sqrt(np.sum(data**2) / len(data))

    return [std_dev, rms, min_val, max_val, zero_crossings, mean_amp_change, amp_first_pulse, mean_abs_val, waveform_length, wilson_amp]

if __name__ == "__main__":
    files = glob.glob('data/*/*.csv')

    for file in files:
        data = pd.read_csv(file, header=None)
        features = []

        # 提取特征值
        for i in range(len(data)):
            feature_row = extract_features(data.iloc[i])
            features.append(feature_row)

        # 获取文件名和标签
        label = os.path.basename(os.path.dirname(file))

        feature_columns = ['std_dev', 'rms', 'min_val', 'max_val', 'zero_crossings', 'mean_amp_change', 'amp_first_pulse', 'mean_abs_val', 'waveform_length', 'wilson_amp']

        # 保存特征值到CSV文件
        features_df = pd.DataFrame(features, columns=feature_columns)
        features_df.to_csv(f'data/{label}/features.csv', index=False)
