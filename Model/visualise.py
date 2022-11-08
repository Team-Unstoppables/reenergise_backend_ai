import numpy as np
import cv2



class PostProcessing:
    def __init__(self, img_path, preds):
        self.image = cv2.imread(img_path)
        self.preds = preds
        self.contours = np.uint8(preds)
        self.num_labels, self.labels, self.stats, self.centroids = cv2.connectedComponentsWithStats(self.contours, connectivity=8)


    def VisImg(self):
        contours = self.contours
        img = self.image.copy()
        contours, hierarchy = cv2.findContours(contours, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        img = cv2.resize(img, (512, 512))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = cv2.fillPoly(img, contours, (255, 0, 0))
        contours = [contour for contour in contours if cv2.contourArea(contour) > 100]
        for i in range(len(contours)):
            x, y, w, h = cv2.boundingRect(contours[i])
            cv2.putText(img, str(i+1), (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        # upscale the image to 1000 x 1000
        img = cv2.resize(img, (1000, 1000))
        cv2.imwrite(r'.\Outs\result2.jpg', img)

    def GetArea(self):
        contours = self.contours
        stats = self.stats
        areas = stats[1:, cv2.CC_STAT_AREA]
        for i in range(1, self.num_labels):
            if stats[i, cv2.CC_STAT_AREA] < 100:
                contours[self.labels == i] = 0
        #areas = np.sort(areas)
        return areas
    
