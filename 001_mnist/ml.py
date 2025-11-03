# mnist_tf_train_test.py
import tensorflow as tf
tf.random.set_seed(42)

# --- Data ---
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()
x_train = (x_train[..., None] / 255.0).astype("float32")  # (N,28,28,1)
x_test  = (x_test[..., None]  / 255.0).astype("float32")

# --- Model ---
model = tf.keras.Sequential([
    tf.keras.layers.Conv2D(32, 3, activation="relu", padding="same", input_shape=(28,28,1)),
    tf.keras.layers.Conv2D(64, 3, activation="relu", padding="same"),
    tf.keras.layers.MaxPooling2D(),
    tf.keras.layers.Dropout(0.25),
    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(128, activation="relu"),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(10, activation="softmax"),
])

model.compile(optimizer="adam",
              loss="sparse_categorical_crossentropy",
              metrics=["accuracy"])

# --- Train ---
model.fit(x_train, y_train, epochs=5, batch_size=128, validation_split=0.2, verbose=1)

# --- Test ---
loss, acc = model.evaluate(x_test, y_test, verbose=0)
print(f"Test accuracy: {acc*100:.2f}%")

# Save the model 
model.save("mnist_cnn.keras")  # or .h5 if you prefer
