from flask import Flask, request, jsonify, send_from_directory
import numpy as np
from PIL import Image, ImageOps
import base64
import tensorflow as tf
import io
import os 

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")

# Load the trained model
model = tf.keras.models.load_model('mnist_model.h5')

# Define the directory to save feedback images
FEEDBACK_DIR = "feedback_images"
os.makedirs(FEEDBACK_DIR, exist_ok=True)

@app.route('/')
def index():
    # Serve the main HTML page
    return send_from_directory('static', 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Check if the request contains a file (uploaded image)
        if 'file' in request.files:
            file = request.files['file']
            img = Image.open(file).convert('L')  # Convert to grayscale
        elif request.json and 'image' in request.json:
            # Handle canvas input (Base64 string)
            base64_image = request.json['image'].split(',')[1]  # Remove "data:image/png;base64,"
            image_data = base64.b64decode(base64_image)
            with open("decoded_image.png", "wb") as f:
                f.write(image_data)
            img = Image.open(io.BytesIO(image_data)).convert('L')  # Convert to grayscale
            img.save('converted_image.png')
        else:
            return jsonify({'error': 'No valid input provided'}), 400
        # invert 
        img = ImageOps.invert(img)
        # Resize to 28x28 and normalize
        img = img.resize((28, 28))
        img.save('debug_resized_input.png')
        img_array = np.array(img) / 255.0
        # Apply threshold to binarize the image
        img_array = np.where(img_array > 0.5, 1.0, 0.0)
        img_array = img_array.reshape(-1, 28, 28, 1)  # Flatten the image

        # Predict using the model
        prediction = model.predict(img_array)
        print(prediction)
        predicted_digit = np.argmax(prediction)

        return jsonify({'digit': int(predicted_digit)})
    except Exception as e:
        # Handle unexpected errors
        return jsonify({'error': str(e)}), 500


@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        # Parse the feedback
        data = request.json
        base64_image = data['image'].split(',')[1]  # Extract Base64 image
        correct_digit = data['correct_digit']       # Correct digit provided by the user

        # Decode the image and save it
        image_data = base64.b64decode(base64_image)
        img = Image.open(io.BytesIO(image_data))

        # Ensure the directory for the correct digit exists
        digit_dir = os.path.join(FEEDBACK_DIR, correct_digit)
        os.makedirs(digit_dir, exist_ok=True)

        # Save the image with a unique name
        img.save(os.path.join(digit_dir, f"{len(os.listdir(digit_dir))}.png"))

        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
