import { useState, useRef, useEffect } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'
import axios from "axios";

function App() {
  const [image, setImage] = useState(null);
  const [objects, setObjects] = useState([]);
  const [hoveredObject, setHoveredObject] = useState(null);
  const [imageSize, setImageSize] = useState({
    origWidth: 1,
    origHeight: 1,
    displayedWidth: 1,
    displayedHeight: 1,
    scaleX: 1,
    scaleY: 1,
  });

  const imgRef = useRef(null);

  const handleImageUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const imageUrl = URL.createObjectURL(file);
    setImage(imageUrl);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post("http://127.0.0.1:8000/detect/", formData);
      setObjects(response.data.objects);
      setImageSize((prev) => ({
        ...prev,
        origWidth: response.data.width,
        origHeight: response.data.height,
      }));
      console.log("imagesizeset - orig:", imageSize.origWidth)
      console.log("imagesizeset - from Data:", response.data.width)
    } catch (error) {
      console.error("Error detecting objects:", error);
    }
  };

  // Update scaling when image loads or resizes
  const updateScaling = () => {
    if (imgRef.current) {
      const displayedWidth = imgRef.current.clientWidth;
      const displayedHeight = imgRef.current.clientHeight;
      console.error("Update scaling Image display width:", imgRef.current.clientWidth);
      // console.error("Image display width:", prev.origWidth);
      setImageSize((prev) => ({
        ...prev,
        displayedWidth: displayedWidth,
        displayedHeight: displayedHeight,
        scaleX: displayedWidth / prev.origWidth,
        scaleY: displayedHeight / prev.origHeight,
      }));
      console.info("update: set Image display width:", imageSize.displayedWidth);
      console.info("update: set Image orig width:", imageSize.origWidth);
      console.info("update: set Image scaleX:", imageSize.scaleX);
    }
  };

  // Trigger updateScaling after the image loads
  useEffect(() => {
    
    if (image) {
      console.error("update scaling");
      updateScaling();
      window.addEventListener("resize", updateScaling);
      return () => window.removeEventListener("resize", updateScaling);
    }
  }, [image]);

  return (
    <div className="flex flex-col items-center p-6 bg-gray-100 min-h-screen">
      <h1 className="text-2xl font-bold mb-4">Object Detection with Segmentation</h1>
      <input type="file" onChange={handleImageUpload} className="mb-4 p-2 border" />

      <div className="relative">
        {/* Original Image */}
        {image && (
          <img
            ref={imgRef}
            src={image}
            alt="Uploaded"
            className={`max-w-full h-auto transition-all duration-300 ${
              hoveredObject !== null ? "brightness-50" : "brightness-100"
            }`}
            onLoad={updateScaling}
          />
        )}

        {/* SVG Overlay for Object Outlines */}
        {image && (
          <svg
            className="absolute top-0 left-0"
            width={imageSize.displayedWidth}
            height={imageSize.displayedHeight}
            viewBox={`0 0 ${imageSize.displayedWidth} ${imageSize.displayedHeight}`}
            style={{
              position: "absolute",
              pointerEvents: "auto",
            }}
          >
            {objects.map((obj, index) => (
              <g
                key={index}
                onMouseEnter={() => setHoveredObject(index)}
                onMouseLeave={() => setHoveredObject(null)}
              >
                {obj.contours.map((contour, i) => (
                  <polygon
                    key={i}
                    points={contour.map(([x, y]) => `${x*imageSize.scaleX},${y*imageSize.scaleY}`).join(" ")}
                    fill={hoveredObject === index ? "rgba(255, 0, 0, 0.3)" : "transparent"}
                    stroke="red"
                    strokeWidth="2"
                    style={{
                      pointerEvents: "visibleFill",
                      mixBlendMode: hoveredObject === index ? "normal" : "multiply",
                    }}
                  />
                ))}
              </g>
            ))}
          </svg>
        )}
      </div>
    </div>
  )
}

export default App;


