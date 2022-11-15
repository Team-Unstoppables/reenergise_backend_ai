import numpy as np
import os
import cloudinary
import cv2
import cloudinary.uploader

# config cloudinary
cloudinary.config(
    cloud_name = "uia22",
    api_key = os.environ.get("CLOUDINARY_KEY"),
    api_secret = os.environ.get("CLOUDINARY_SECRET")
)

class PostProcessing:
    def __init__(self, img, preds):
        self.image = img
        self.preds = preds
        self.contours = np.uint8(preds)
        self.num_labels, self.labels, self.stats, self.centroids = cv2.connectedComponentsWithStats(self.contours, connectivity=8)


    def VisImg(self):
        contours = self.contours
        img = self.image
        contours, hierarchy = cv2.findContours(contours, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # change img to numpy array
        img = np.array(img)
        img = cv2.resize(img, (512, 512))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        #draw contours without filling
        self.contours = [contour for contour in contours if cv2.contourArea(contour) > 100]
        cv2.drawContours(img, contours, -1, (255, 0 , 0), 1)
        for i in range(len(self.contours)):
            x, y, w, h = cv2.boundingRect(self.contours[i])
            cv2.circle(img, (x, y), 10, (0, 0, 0), -1)
            cv2.putText(img, str(i+1), (x-5, y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            # put a circle behind the number to make it more visible
            
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # upscale the image to 1000 x 1000
        img = cv2.resize(img, (1000, 1000))
        img_bytes = cv2.imencode('.jpg', img)[1].tobytes()
        link = cloudinary.uploader.upload(img_bytes)
        return link['url']
        

    def GetArea(self):
        contours = self.contours
        stats = self.stats
        areas = [cv2.contourArea(contour) for contour in contours]
        print(areas)
        return areas 
    
