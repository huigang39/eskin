import pandas as pd
import tensorflow as tf

class data():
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)

    def data_re(self):
        # Extract features and labels
        x = self.df.iloc[:, :-1].values
        y = self.df.iloc[:, -1].values

        # Convert labels to one-hot encoding
        y = tf.one_hot(y, depth=10)

        # Split into train and validation sets
        split_idx = int(0.8 * len(x))
        x_train, y_train = x[:split_idx], y[:split_idx]
        x_val, y_val = x[split_idx:], y[split_idx:]

        return (x_train, y_train), (x_val, y_val)

    def train_data(self, batchsz_t):
        (x, y), _ = self.data_re()
        train_dataset = tf.data.Dataset.from_tensor_slices((x, y))
        train_dataset = train_dataset.batch(batchsz_t)
        train_dataset = train_dataset.prefetch(tf.data.experimental.AUTOTUNE)

        return train_dataset

    def val_data(self, batchsz_v):
        _, (x_val, y_val) = self.data_re()
        val_dataset = tf.data.Dataset.from_tensor_slices((x_val, y_val))
        val_dataset = val_dataset.batch(batchsz_v)

        return val_dataset

if __name__ == "__main__":
    data_load = data("data/emg_all_features_labeled.csv")
    data_it = data_load.train_data(64)
    for x, y in data_it:
        print("x.shape:", x.shape)
        print("y.shape:", y.shape)
