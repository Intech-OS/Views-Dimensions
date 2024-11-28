from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import os
import io
import cv2
import numpy as np
import pandas as pd
from Dimension_detection import run1


app = FastAPI()

try:
    os.mkdir("images_uploaded")
except:
    pass

@app.post("/process-image/")
async def process_image(file: UploadFile = File(...)):
    try:
        filename = file.filename
        fileExtension = filename.split(".")[-1] in ("jpg", "jpeg", "png","PNG")
        if not fileExtension:
            raise HTTPException(status_code=415, detail="Unsupported file provided.")
        
        # 2. TRANSFORM RAW IMAGE INTO CV2 image
    
        # Read image as a stream of bytes
        image_stream = io.BytesIO(file.file.read())
        
        # Start the stream from the beginning (position zero)
        image_stream.seek(0)
        
        # Write the stream of bytes into a numpy array
        file_bytes = np.asarray(bytearray(image_stream.read()), dtype=np.uint8)
        
        # Decode the numpy array as an image
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        
        # Save it in a folder within the server
        img_path = f'images_uploaded/{filename}'
        cv2.imwrite(img_path, image)

    except Exception:
        return {"message": "There was an error uploading the file"}
    finally:
        file.file.close()
        
    try:
        # Your image processing code here
        # You can replace this with the actual code to process the image
        sec_ip_path = run1(weights=r"trained_model/Dimensio_detection.pt",
                   source=img_path,
                   data=r'data\coco128.yaml',
                   imgsz=[640, 640],
                   conf_thres=0.25,
                   iou_thres=0.45,
                   max_det=1000,
                   device="",
                   view_img=False,
                   save_txt=False,
                   save_csv=False,
                   save_conf=False,
                   save_crop=False,
                   nosave=False,
                   classes=None,
                   agnostic_nms=False,
                   augment=False,
                   visualize=False,
                   update=False,
                   project=r'runs\detect',
                   name="exp1_",
                   exist_ok=False,
                   line_thickness=3,  # bounding box thickness (pixels)
                   hide_labels=True,  # hide labels
                   hide_conf=True,
                   half=False,
                   dnn=False, vid_stride=1)


            # Assuming the code executes successfully
        
        '''kdf = pd.read_csv(os.path.join(sec_ip_path, "mapping.csv"))
        kdf.dropna(subset=["Tol",], inplace=True)
        tols = list(kdf["Tol"])

        
        if any(float(tol) < 0.1 for tol in tols):
            rtxt = "The required dimentional accuracy is difficult to achieve, post processing is required"
            
        else:
            rtxt = "No post processing required."
            '''
        return {"message": "Image processed successfully"}, 200
    except Exception as e:
        return {"error": str(e)}, 500
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)