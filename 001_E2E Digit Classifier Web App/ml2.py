# train_mnist_cnn_v2.py
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

tf.random.set_seed(42)

# -------- Data --------
(x_tr, y_tr), (x_te, y_te) = keras.datasets.mnist.load_data()
x_tr = (x_tr[..., None] / 255.).astype("float32")   # (N,28,28,1)
x_te = (x_te[..., None] / 255.).astype("float32")

BATCH = 128

data_aug = keras.Sequential([
    layers.RandomTranslation(0.18, 0.18, fill_mode="constant", fill_value=0.0),
    layers.RandomRotation(0.12, fill_mode="constant", fill_value=0.0),
    layers.RandomZoom(0.12, fill_mode="constant", fill_value=0.0),
    layers.RandomContrast(0.15),
], name="data_aug")

# -------- Model (same family, stronger) --------
def conv_bn_relu(x, f, k=3):
    x = layers.Conv2D(f, k, padding="same", use_bias=False, kernel_initializer="he_normal")(x)
    x = layers.BatchNormalization()(x)
    return layers.ReLU()(x)

inp = keras.Input((28,28,1))
x = data_aug(inp)

x = conv_bn_relu(x, 32); x = conv_bn_relu(x, 32)
x = layers.MaxPooling2D()(x); x = layers.Dropout(0.10)(x)

x = conv_bn_relu(x, 64); x = conv_bn_relu(x, 64)
x = layers.MaxPooling2D()(x); x = layers.Dropout(0.20)(x)

x = conv_bn_relu(x, 128)
x = layers.GlobalAveragePooling2D()(x)
x = layers.Dense(128, activation="relu")(x)
x = layers.Dropout(0.30)(x)
out = layers.Dense(10, activation="softmax")(x)

model = keras.Model(inp, out)

# -------- Compile --------
opt = keras.optimizers.Adam(learning_rate=3e-3)
model.compile(
    optimizer=opt,
    loss=keras.losses.SparseCategoricalCrossentropy(),
    metrics=["accuracy"]
)

# -------- Train --------
callbacks = [
    keras.callbacks.EarlyStopping(patience=4, restore_best_weights=True, monitor="val_accuracy"),
    keras.callbacks.ReduceLROnPlateau(factor=0.5, patience=2, min_lr=1e-5, monitor="val_accuracy"),
    keras.callbacks.ModelCheckpoint("mnist_cnn_v2.keras", save_best_only=True, monitor="val_accuracy"),
]
model.fit(
    x_tr, y_tr,
    validation_split=0.1,
    epochs=25,
    batch_size=BATCH,
    callbacks=callbacks,
    verbose=2
)

# -------- Evaluate & Save --------
test_loss, test_acc = model.evaluate(x_te, y_te, verbose=0)
print(f"Test accuracy: {test_acc*100:.2f}%")
model.save("mnist_cnn_v2.keras")
