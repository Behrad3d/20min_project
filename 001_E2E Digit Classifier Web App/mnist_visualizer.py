import matplotlib.pyplot as plt
from tensorflow.keras.datasets import mnist

# Load data
(x_train, y_train), _ = mnist.load_data()

# Pick 25 random samples
import numpy as np
idx = np.random.choice(len(x_train), 25, replace=False)
images, labels = x_train[idx], y_train[idx]

# Plot
plt.figure(figsize=(6,6))
for i in range(25):
    plt.subplot(5,5,i+1)
    plt.imshow(images[i], cmap='gray')
    plt.title(str(labels[i]))
    plt.axis('off')
plt.tight_layout()
plt.show()