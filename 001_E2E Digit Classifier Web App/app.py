# app.py
import base64, io, numpy as np
from PIL import Image, ImageOps
from flask import Flask, request, jsonify, Response,render_template
import tensorflow as tf
import os, uuid
from PIL import Image
SAVE_DIR = "processed_samples"
os.makedirs(SAVE_DIR, exist_ok=True) 

app = Flask(__name__)
# model = tf.keras.models.load_model("mnist_cnn.keras") # Original model we used during the video (not super accurate)
model = tf.keras.models.load_model("mnist_cnn_v2.keras") #The best outcome 
# model = tf.keras.models.load_model("mnist_model.h5") # Faster model but not as good as the second one


@app.get("/")
def index():
    return render_template("index.html")

def preprocess_image_from_dataurl(data_url: str) -> np.ndarray:
    # data:image/png;base64,XXXX
    b64 = data_url.split(",")[1]
    img = Image.open(io.BytesIO(base64.b64decode(b64))).convert("L")  # grayscale
    # Invert so strokes are white (MNIST digits are white on black)
    img = ImageOps.invert(img)
    # Optional: center-crop to content bounding box
    arr = np.array(img)
    ys, xs = np.where(arr > 20)  # threshold for drawn pixels
    if len(xs) and len(ys):
        x0, x1 = xs.min(), xs.max()
        y0, y1 = ys.min(), ys.max()
        # add margin
        pad = 20
        x0 = max(0, x0 - pad); y0 = max(0, y0 - pad)
        x1 = min(arr.shape[1]-1, x1 + pad); y1 = min(arr.shape[0]-1, y1 + pad)
        img = Image.fromarray(arr[y0:y1+1, x0:x1+1])
    # Resize to 28x28 (MNIST size)
    img = img.resize((28, 28), Image.Resampling.LANCZOS)
    # Normalize to [0,1] and add channel & batch dims
    x = np.array(img).astype("float32") / 255.0
    x = x.reshape(1, 28, 28, 1)
    return x

@app.post("/predict")
def predict():
    data = request.get_json()
    x28 = preprocess_image_from_dataurl(data["image"])   # (1,28,28,1), float32 in [0,1]
    probs = model.predict(x28, verbose=0)[0]
    pred  = int(np.argmax(probs))
    conf  = float(probs[pred])

    # save ONLY the processed 28×28 as PNG (no raw image, no metadata)
    sample_id = uuid.uuid4().hex
    x_uint8 = (x28[0, ..., 0] * 255).astype("uint8")     # (28,28)
    Image.fromarray(x_uint8, mode="L").save(
        os.path.join(SAVE_DIR, f"{sample_id}_28x28.png")
    )

    return jsonify({
        "id": sample_id,                 # returned for client reference
        "prediction": pred,
        "confidence": conf,
        "probabilities": probs.tolist()
    })
if __name__ == "__main__":
    # Run: FLASK_DEBUG=1 python app.py
    app.run(host="0.0.0.0", port=4000, debug=True)
