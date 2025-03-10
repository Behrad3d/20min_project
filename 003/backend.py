from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
from flask_cors import CORS  # Import CORS
from ultralytics import YOLO
from fastapi.responses import JSONResponse
from io import BytesIO
from PIL import Image
import cv2

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load YOLOv8 model (segmentation model)
model = YOLO("yolov8n-seg.pt")

@app.post("/detect/")
async def detect_objects(file: UploadFile = File(...)):
    image = Image.open(BytesIO(await file.read()))
    image_np = np.array(image)

    # Get original image dimensions
    orig_width, orig_height = image.size
    print(f"image size({orig_width},{orig_height})")
    # Run YOLOv8 segmentation
    results = model(image_np)

    detections = []
    for result in results:
        for mask, box in zip(result.masks.data.cpu().numpy(), result.boxes.data):
            x1, y1, x2, y2, confidence, class_id = box.tolist()
            print(f"detected {model.names[int(class_id)]}, - confience:{confidence}")
            if confidence > 0.55:
            # Convert mask to contour points
                mask = (mask * 255).astype(np.uint8)  # Convert to binary mask
                contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                contour_points = [cnt.squeeze().tolist() for cnt in contours if len(cnt) > 2]  # Extract valid contours

                detections.append({
                    "label": model.names[int(class_id)],
                    "contours": contour_points
                })
    response = JSONResponse(content={"objects": detections, "width": orig_width, "height": orig_height})
    return response 
