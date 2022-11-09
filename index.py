import sys
import os
sys.path.extend(['Model'])
from flask import Flask, render_template, jsonify
import os
from flask_cors import CORS
from Model import infer

app = Flask(__name__)
CORS(app)

global area
global segmented_url

@app.route('/')
def index():
    return render_template('index.html')

def get_satellite_image(lat, lon, zoom=18, size="1000x1000", maptype="satellite",
                        format="png", scale = 1,
                        key=os.environ.get('MAPS_API_KEY')):

    url = "https://maps.googleapis.com/maps/api/staticmap?"
    url += "center=" + str(lat) + "," + str(lon)
    url += "&zoom=" + str(zoom)
    url += "&size=" + size
    url += "&maptype=" + maptype
    url += "&key=" + key
    url += "&format=" + format
    print(url)

    return url

@app.route("/segment/<float(signed=True):lat>/<float(signed=True):lon>", methods=['GET'])
def segment(lat, lon):
    img_url = get_satellite_image(lat, lon)
    seg_obj = infer.Segmentation(img_url, vis=True)
    global area 
    area = seg_obj.area
    segmented_url = seg_obj.segmented_url
    return jsonify({'segmented_url': segmented_url})


@app.route('/results/<index>', methods=['GET'])
def results(index):
    return jsonify({'area': str(area[int(index)])})


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

