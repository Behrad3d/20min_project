# app.py
import base64, io, numpy as np
from PIL import Image, ImageOps
from flask import Flask, request, jsonify, Response
import tensorflow as tf
import os, uuid
from PIL import Image
SAVE_DIR = "processed_samples"
os.makedirs(SAVE_DIR, exist_ok=True) 

app = Flask(__name__)
# model = tf.keras.models.load_model("mnist_cnn.keras")
model = tf.keras.models.load_model("mnist_cnn_v2.keras")
# model = tf.keras.models.load_model("mnist_model.h5")



HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>MNIST Canvas Classifier</title>
<style>
  body { font-family: system-ui, sans-serif; display:flex; gap:24px; align-items:flex-start; padding:24px; }
  #wrap { display:flex; flex-direction:column; gap:12px; }
  canvas { border:1px solid #ccc; background:#fff; touch-action:none; }
  button { padding:8px 14px; border-radius:10px; border:1px solid #999; cursor:pointer; }
  #pred { font-size:20px; }
  #probs { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; white-space:pre; }
</style>
</head>
<body>
  <div id="wrap">
    <canvas id="canvas" width="280" height="280"></canvas>
    <div>
      <button id="clear">Clear</button>
      <button id="predict">Predict</button>
    </div>
  </div>
  <div>
    <div id="pred">Draw a digit (0–9) and click Predict</div>
    <pre id="probs"></pre>
  </div>
<script>
const c = document.getElementById('canvas');
const ctx = c.getContext('2d');
ctx.fillStyle = '#FFFFFF'; ctx.fillRect(0,0,c.width,c.height);
ctx.lineWidth = 18; ctx.lineCap = 'round'; ctx.strokeStyle = '#000000';

let drawing = false, last = null;

function pos(e){
  const r = c.getBoundingClientRect();
  const x = (e.touches? e.touches[0].clientX : e.clientX) - r.left;
  const y = (e.touches? e.touches[0].clientY : e.clientY) - r.top;
  return {x, y};
}
function draw(p){
  if(!last) { last = p; return; }
  ctx.beginPath();
  ctx.moveTo(last.x, last.y);
  ctx.lineTo(p.x, p.y);
  ctx.stroke();
  last = p;
}
c.addEventListener('mousedown', e=>{ drawing=true; last=null; draw(pos(e)); });
c.addEventListener('mousemove', e=>{ if(drawing) draw(pos(e)); });
window.addEventListener('mouseup', ()=> drawing=false);

c.addEventListener('touchstart', e=>{ e.preventDefault(); drawing=true; last=null; draw(pos(e)); });
c.addEventListener('touchmove',  e=>{ e.preventDefault(); if(drawing) draw(pos(e)); });
c.addEventListener('touchend',   e=>{ e.preventDefault(); drawing=false; });

document.getElementById('clear').onclick = ()=>{
  ctx.clearRect(0,0,c.width,c.height);
  ctx.fillStyle = '#FFFFFF'; ctx.fillRect(0,0,c.width,c.height);
  document.getElementById('pred').textContent = 'Cleared. Draw a digit and click Predict';
  document.getElementById('probs').textContent = '';
};

document.getElementById('predict').onclick = async ()=>{
  const dataURL = c.toDataURL('image/png');
  const res = await fetch('/predict', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({image:dataURL}) });
  const out = await res.json();
  document.getElementById('pred').textContent = 'Prediction: ' + out.prediction + ' (conf: ' + out.confidence.toFixed(3) + ')';
  const probs = out.probabilities.map((p,i)=> `${i}: ${p.toFixed(4)}`).join('\\n');
  document.getElementById('probs').textContent = probs;
};
</script>
</body>
</html>
"""

@app.get("/")
def index():
    return Response(HTML, mimetype="text/html")

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
