from .ResNet import *
from .VGGNet import *
import torch


__all__ = ['get_backbone']


def get_backbone(model_name='', pretrained=True, num_classes=None, **kwargs):
    if 'res' in model_name:
        model = get_resnet(model_name, pretrained=pretrained, num_classes=num_classes, **kwargs)       
        state_dict = torch.load('./checkpoint/resnet50-19c8e357.pth', map_location='cpu')
        num_classes = 2
        out_keys = []
        if num_classes !=1000:
            #print('Removing the last fc layer')
            keys = state_dict.keys()
            keys = [x for x in keys if 'fc' in x]
            for key in keys:
                del state_dict[key]
        if 'block5' not in out_keys:
            #print('Removing the last layer')
            keys = state_dict.keys()
            keys = [x for x in keys if 'layer4' in x]
            for key in keys:
                del state_dict[key]
        #print(state_dict.keys())
        model.load_state_dict(state_dict)
    elif 'vgg' in model_name:
        model = get_vgg(model_name, pretrained=pretrained, num_classes=num_classes, **kwargs)
    else:
        raise NotImplementedError
    return model

