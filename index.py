import sys
import os
sys.path.extend(['Model'])
from flask import Flask, render_template, jsonify
import cv2
import numpy as np
import os
import math
from flask_cors import CORS
from Model import infer
from savings import main

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

# 156543.03 * Math.cos((22/7) / 180 * latitude) / (2 ** zoom)
def scaling_factor(lat):
    zoom = 18
    scale = 156543.03 * math.cos((22/7) / 180 * lat) / (2 ** zoom)
    return scale*scale

def get_satellite_image(lat, lon, zoom=18, size="1000x1000", maptype="satellite",
                        format="png", scale = 2,
                        key=os.environ.get("MAPS_API_KEY")):
    url = "https://maps.googleapis.com/maps/api/staticmap?"
    url += "center=" + str(lat) + "," + str(lon)
    url += "&zoom=" + str(zoom)
    url += "&size=" + size
    url += "&maptype=" + maptype
    url += "&key=" + key
    url += "&format=" + format
    print(url)

    return url

def get_image(place, zoom=18, size="1000x1000", maptype="satellite",
                        format="png", scale = 1,
                        key=os.environ.get("MAPS_API_KEY")):
    url = "https://maps.googleapis.com/maps/api/staticmap?"
    # replace %20 with + in place name
    place = place.replace("%20", "+")
    place = place.replace(" ", "+")
    url += "center=" + place
    url += "&zoom=" + str(zoom)
    url += "&size=" + size
    url += "&maptype=" + maptype
    url += "&key=" + key
    url += "&format=" + format
    print(url)
    return url

@app.route("/segment/<float(signed=True):lat>/<float(signed=True):lon>", methods=['GET'])
def segment(lat, lon):
    global latitude
    global longitude
    latitude = lat
    longitude = lon
    
    img_url = get_satellite_image(lat, lon)
    seg_obj = infer.Segmentation(img_url, vis=True)
    area = seg_obj.area
    # make scaled area global
    global scaled_area
    scaled_area = [scaling_factor(lat)*a for a in area]
    segmented_url = seg_obj.segmented_url
    return jsonify({'segmented_url': segmented_url, 'roof_number': str(len(scaled_area))})

@app.route("/segment/<place>", methods=['GET'])
def segment_place(place):
    img_url = get_image(place)
    seg_obj = infer.Segmentation(img_url, vis=True)
    global scaled_area
    scaled_area = [49*a for a in seg_obj.area]
    segmented_url = seg_obj.segmented_url
    return jsonify({'segmented_url': segmented_url, 'roof_number': str(len(scaled_area))})


@app.route('/results/<lat>/<lon>/<index>/<ac_temp>/<ac_type>/<model>/<cost>', methods=['GET'])
def results(lat, lon, index, ac_temp, ac_type, model, cost):
    print(scaled_area)
    area = scaled_area[int(index)]
    print("area", area)
    savings_data = main(lat, lon, area, float(ac_temp), float(cost), ac_type, model)
    savings_data['area'] = area
    return jsonify(savings_data)

@app.route('/canvas/<x1>/<y1>/<x2>/<y2>/<x3>/<y3>/<x4>/<y4>/<lat>/<lon>', methods=['GET'])
def canvas_area(x1, y1, x2, y2, x3, y3, x4, y4, lat, lon):
    x1, y1, x2, y2, x3, y3, x4, y4 = int(x1), int(y1), int(x2), int(y2), int(x3), int(y3), int(x4), int(y4)
    lat = float(lat)
    lon = float(lon)
    global scaled_area
    scale = scaling_factor(lat)
    scaled_area = [cv2.contourArea(np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]]))*scale]
    return jsonify({'area': str(scaled_area[0])})
    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

