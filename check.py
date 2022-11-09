# get satellite image of a location using google maps api
import skimage.io as io
from urllib.request import urlopen
import cv2
import numpy as np
import matplotlib.pyplot as plt

def get_satellite_image(lat, lon, zoom=18, size="1000x1000", maptype="satellite",
                        format="png", scale = 1,
                        key="AIzaSyDYYY1xWo9eYMgRmaTDi43Ft5SNY7dDcF0"):

    url = "https://maps.googleapis.com/maps/api/staticmap?"
    url += "center=" + str(lat) + "," + str(lon)
    url += "&zoom=" + str(zoom)
    url += "&size=" + size
    url += "&maptype=" + maptype
    url += "&key=" + key
    url += "&format=" + format
    print(url)

    return url

def image(url):
    return io.imread(url)

if __name__ == "__main__":
    url = get_satellite_image(37.422, -122.084, zoom=18)
    resp = urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")

    img = cv2.imdecode(image, cv2.IMREAD_COLOR)
    # show the output image

    plt.imshow(img)
    plt.show()

