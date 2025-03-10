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
# plt.imshow(x_train[0].reshape(28, 28), cmap="gray")
# plt.title(f"Label: {y_train[0]}")
# plt.show()

from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# Define the model
model = Sequential([
    Conv2D(32, (4, 4), activation='relu', input_shape=(28, 28, 1)),  # Convolutional layer
    MaxPooling2D((2, 2)),                                           # Pooling layer
    Conv2D(64, (3, 3), activation='relu'),                          # Another convolutional layer
    MaxPooling2D((2, 2)),                                           # Another pooling layer
    Flatten(),                                                      # Flatten for dense layers
    Dense(128, activation='relu'),                                  # Fully connected layer
    Dense(10, activation='softmax')                                 # Output layer
])

# Compile and train the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(x_train.reshape(-1, 28, 28, 1), y_train, epochs=25, batch_size=32)


# Evaluate the model on test data
test_loss, test_accuracy = model.evaluate(x_test.reshape(-1, 28, 28, 1), y_test)
print(f"Test Accuracy: {test_accuracy * 100:.2f}%")


model.save('mnist_model.h5')
