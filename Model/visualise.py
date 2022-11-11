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
        cv2.drawContours(img, contours, -1, (255, 0 , 0), 1)
        contours = [contour for contour in contours if cv2.contourArea(contour) > 100]
        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            cv2.putText(img, str(i+1), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # upscale the image to 1000 x 1000
        img = cv2.resize(img, (1000, 1000))
        img_bytes = cv2.imencode('.jpg', img)[1].tobytes()
        link = cloudinary.uploader.upload(img_bytes)
        return link['url']
        

    def GetArea(self):
        contours = self.contours
        stats = self.stats
        areas = stats[1:, cv2.CC_STAT_AREA]
        for i in range(1, self.num_labels):
            if stats[i, cv2.CC_STAT_AREA] < 100:
                contours[self.labels == i] = 0
        #areas = np.sort(areas)
        return areas
    
