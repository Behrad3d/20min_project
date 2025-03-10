import tensorflow as tf
import matplotlib.pyplot as plt

# Load dataset
mnist = tf.keras.datasets.mnist
(x_train, y_train), (x_test, y_test) = mnist.load_data()

# Normalize the data to the range [0, 1]
x_train, x_test = x_train / 255.0, x_test / 255.0

# Flatten the images (28x28 -> 784) for input to the neural network
x_train = x_train.reshape(-1, 28 * 28)
x_test = x_test.reshape(-1, 28 * 28)

# Display a sample
plt.imshow(x_train[0].reshape(28, 28), cmap="gray")
plt.title(f"Label: {y_train[0]}")
plt.show()
