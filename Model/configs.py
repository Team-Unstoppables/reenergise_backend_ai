def model_configs():
    model_infos = {
        'backbone': 'resnet50',
        'pretrained': True,
        'out_keys': ['block4'],
        'in_channel': 3,
        'n_classes': 2,
        'top_k_s': 64,
        'top_k_c': 16,
        'encoder_pos': True,
        'decoder_pos': True,
        'model_pattern': ['X', 'A', 'S', 'C'],
        'log_path': 'Results',
        'NUM_WORKERS': 0,
        'IS_VAL': False,
        'VAL_BATCH_SIZE': 1,
        'VAL_DATASET': r'./generate_dep_info/val_data.csv',
        'IS_TEST': True,
        'TEST_DATASET': r'./generate_dep_info/test_data.csv',
        'IMG_SIZE': [512, 512],
        'PHASE': 'seg',
        'DATA_PATH': r'./generate_dep_info',
        'PRIOR_MEAN': [0.4050815770832258, 0.4270536020305017, 0.39289652127756025],
        'PRIOR_STD': [0.02652672988917037, 0.024909359403410613, 0.025808072934281168],
        'load_checkpoint_path': r'./checkpoint/INRIA_ckpt_latest.pt',
    }
    return model_infos
