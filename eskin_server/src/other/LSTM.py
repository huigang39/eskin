import pandas as pd
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
import glob
import seaborn as sns

file = 'features.csv'

# 获取所有CSV文件
files = glob.glob(f'data/*/{file}')

# 文件名和对应的标签
labels = [os.path.basename(os.path.dirname(file)) for file in files]

# 读取所有文件并合并数据
all_features = []
all_labels = []

for file, label in zip(files, labels):
    df = pd.read_csv(file)
    all_features.append(df)
    all_labels.extend([label] * len(df))

features_df = pd.concat(all_features, ignore_index=True)
labels_df = pd.DataFrame(all_labels, columns=['label'])

# 数据预处理
scaler = MinMaxScaler()
scaled_features = scaler.fit_transform(features_df)

encoder = LabelEncoder()
encoded_labels = encoder.fit_transform(labels_df.values.ravel())

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(scaled_features, encoded_labels, test_size=0.2, random_state=42)

# 将数据调整为LSTM所需的格式 (samples, timesteps, features)
X_train = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
X_test = X_test.reshape(X_test.shape[0], 1, X_test.shape[1])

import numpy as np
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.models import load_model
import matplotlib.pyplot as plt

# 检查是否已经存在保存的模型
if os.path.exists('lstm.h5'):
    model = load_model('lstm.h5')
    print("Loaded saved model successfully!")
else:
    # 构建LSTM模型
    model = Sequential()
    model.add(LSTM(50, input_shape=(X_train.shape[1], X_train.shape[2])))
    model.add(Dropout(0.2))
    model.add(Dense(len(np.unique(encoded_labels)), activation='softmax'))

    model.compile(loss='sparse_categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # 显示模型结构
    model.summary()

    # 训练模型
    history = model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.1, verbose=1)

    # 保存模型
    model.save('my_model.h5')
    print("Saved model successfully!")

    # 可视化训练过程中的准确率和损失
    plt.plot(history.history['accuracy'], label='train_accuracy')
    plt.plot(history.history['val_accuracy'], label='val_accuracy')
    plt.plot(history.history['loss'], label='train_loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.title('Training History')
    plt.xlabel('Epoch')
    plt.ylabel('Accuracy/Loss')
    plt.legend()
    plt.show()

# 评估模型
loss, accuracy = model.evaluate(X_test, y_test, verbose=1)
print("Test Loss: {:.4f}, Test Accuracy: {:.2f}%".format(loss, accuracy * 100))

# 预测测试集的标签
y_pred = model.predict(X_test)

# 将预的标签转换类别
y_classes = np.argmax(y_pred, axis=1)
# 将编码的标签转换为原始标签
y_test_labels = encoder.inverse_transform(y_test)
y_pred_labels = encoder.inverse_transform(y_classes)

# 打印混淆矩阵和分类报告
from sklearn.metrics import confusion_matrix, classification_report

print("Confusion Matrix:")
cm = confusion_matrix(y_test_labels, y_pred_labels)
print(cm)

print("Classification Report:")
cr = classification_report(y_test_labels, y_pred_labels)
print(cr)

# 可视化混淆矩阵和分类报告
report = pd.DataFrame.from_dict(classification_report(y_test_labels, y_pred_labels, output_dict=True))
report = report.transpose()
report.drop(['support'], axis=1, inplace=True)

plt.figure(figsize=(15, 6))

plt.subplot(1, 2, 1)
sns.heatmap(cm, annot=True, cmap='Blues', xticklabels=encoder.classes_, yticklabels=encoder.classes_)
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')

plt.subplot(1, 2, 2)
sns.heatmap(report, annot=True, cmap='Blues')
plt.title('Classification Report')

plt.show()
