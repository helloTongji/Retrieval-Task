import os
import argparse
import warnings
import numpy as np
import scipy.io as sio
#import model.dch as model
import model.dch_inception as model
import data_provider.image as dataset

import logging
logger = logging.getLogger(__name__)

from pprint import pprint

warnings.filterwarnings("ignore", category = DeprecationWarning)
warnings.filterwarnings("ignore", category = FutureWarning)

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

parser = argparse.ArgumentParser(description='Triplet Hashing')
parser.add_argument('--lr', '--learning-rate', default=0.001, type=float)
parser.add_argument('--output-dim', default=128, type=int)   # 256, 128, 64
parser.add_argument('--alpha', default=0.5, type=float)
parser.add_argument('--bias', default=0.0, type=float)
parser.add_argument('--gamma', default=20, type=float)
parser.add_argument('--iter-num', default=2000, type=int)
parser.add_argument('--q-lambda', default=0, type=float)
parser.add_argument('--dataset', default='kinetics', type=str)
parser.add_argument('--gpus', default='0,1', type=str) # well most of the cases
parser.add_argument('--log-dir', default='tflog', type=str)
parser.add_argument('-b', '--batch-size', default=1, type=int) # 20190609
parser.add_argument('-vb', '--val-batch-size', default=16, type=int)
parser.add_argument('--decay-step', default=10000, type=int)
parser.add_argument('--decay-factor', default=0.1, type=float)

tanh_parser = parser.add_mutually_exclusive_group(required=False)
tanh_parser.add_argument('--with-tanh', dest='with_tanh', action='store_true')
tanh_parser.add_argument('--without-tanh', dest='with_tanh', action='store_false')
parser.set_defaults(with_tanh=True)

parser.add_argument('--img-model', default='s3d', type=str)
parser.add_argument('--model-weights', type=str,
                    default='../../DeepHash/architecture/pretrained_model/reference_pretrain.npy')
parser.add_argument('--finetune-all', default=True, type=bool)
parser.add_argument('--save-dir', default="/home/xiaomi/DeepHash/DeepHash/model/dch_inception/models/", type=str)
parser.add_argument('--data-dir', default="/home/xiaomi/DeepHash/data/", type=str)
parser.add_argument('-e', '--evaluate', dest='evaluate', action='store_true')

args = parser.parse_args()

os.environ['CUDA_VISIBLE_DEVICES'] = args.gpus
# label will be removed in the further version (use kinetics-600)
label_dims = {'cifar10': 10, 'cub': 200, 'nuswide_81': 81, 'coco': 80, 'kinetics': 10} # 32x32 color images - 10 object classes
Rs = {'cifar10': 54000, 'nuswide_81': 5000, 'coco': 5000, 'kinetics': 54000} # guess: code len
args.R = Rs[args.dataset] # R is the 'R' from 'RD' 20190606
args.label_dim = label_dims[args.dataset]

# <image path><space><one hot label representation>
args.img_tr = os.path.join(args.data_dir, args.dataset, "train_kinetics.csv")
args.img_te = os.path.join(args.data_dir, args.dataset, "test_kinetics.csv")
args.img_db = os.path.join(args.data_dir, args.dataset, "val_kinetics.csv")

pprint(vars(args))

data_root = os.path.join(args.data_dir, args.dataset)
query_img, database_img = dataset.import_val_vid(data_root, args.img_te, args.img_db) # test_image, database_image
# return object Kinetics

if not args.evaluate:
    train_img = dataset.import_train_vid(data_root, args.img_tr) #/DeepHash/data_provider/image/__init__.py
    model_weights = model.train(train_img, database_img, query_img, args)
    args.model_weights = model_weights

maps = model.validation(database_img, query_img, args)
for key in maps:
    print(("{}\t{}".format(key, maps[key])))

pprint(vars(args))
