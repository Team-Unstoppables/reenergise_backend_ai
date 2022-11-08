import sys
sys.path.append('Model')
import cv2
import torch
from STTNet import STTNet
import torch.nn.functional as F
from Utils.Datasets import get_data_loader
from Utils.Utils import make_numpy_img, inv_normalize_img, encode_onehot_to_mask, get_metrics, Logger
import matplotlib.pyplot as plt
import numpy as np
from collections import OrderedDict
from skimage import io
from visualise import PostProcessing
from configs import model_configs


class Segmentation:
    def __init__(self, img_path, vis=False):
        self.model_infos = model_configs()
        self.model = STTNet(**self.model_infos)
        self.load_model()
        self.img = self.read_image(img_path) 
        self.pred_label = self.predict(self.img)
        self.area = self.post_process(img_path, self.pred_label, vis)

    def load_model(self):
        # load the trained model
        state_dict = torch.load(self.model_infos['load_checkpoint_path'], map_location='cpu')
        model_dict = state_dict['model_state_dict']
        try:
            model_dict = OrderedDict({k.replace('module.', ''): v for k, v in model_dict.items()})
            self.model.load_state_dict(model_dict)
        except Exception as e:
            self.model.load_state_dict(model_dict)
                # if cuda is available, use cuda
        if torch.cuda.is_available():
            self.model.cuda()
        self.model.eval()
    
    def read_image(self, img_path):
        img= io.imread(img_path, as_gray=False)
        img= cv2.resize(img, (512, 512))
        img= img[:, :, :3]
        img = np.transpose(img, (2, 0, 1))
        img = img / 255.0
        img[0] = (img[0] - self.model_infos['PRIOR_MEAN'][0]) / self.model_infos['PRIOR_STD'][0]
        img[1] = (img[1] - self.model_infos['PRIOR_MEAN'][1]) / self.model_infos['PRIOR_STD'][1]
        img[2] = (img[2] - self.model_infos['PRIOR_MEAN'][2]) / self.model_infos['PRIOR_STD'][2]
        img = torch.from_numpy(img).unsqueeze(0).float()

        return img
    
    def predict(self, img):
        with torch.no_grad():
            if torch.cuda.is_available():
                img = img.cuda()
            logits, att_branch_output = self.model(img)
        pred_label = torch.argmax(logits, 1)
        pred_label = pred_label.cpu().numpy()
        pred_label = np.squeeze(pred_label, 0)

        return pred_label
    
    def post_process(self, img_path, pred_label, vis=False):
        post_process = PostProcessing(img_path, pred_label)
        if vis:
            post_process.VisImg()
        area = post_process.GetArea()
        return area


if __name__ == '__main__':
    img_path = r"E:\uia22\BuildingExtraction\Data\test\images\bellingham1_4000_2000.jpg"
    seg = Segmentation(img_path, vis=True)
    print(seg.area)