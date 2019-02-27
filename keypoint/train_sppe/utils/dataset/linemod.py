import os
import h5py
import torch.utils.data as data
from functools import reduce

from ..pose import generateSampleBox
from opt import opt


class Linemod(data.Dataset):
    def __init__(self, train):
        if train:
            self.img_folder = '/home/penggao/projects/pose/kppose/linemod/%s/%s/%s/%s/train' % (
                opt.datatype, opt.nClasses, opt.kptype, opt.seq)
        else:
            self.img_folder = '/home/penggao/projects/pose/kppose/linemod/%s/%s/%s/%s/eval' % (
                'gt', opt.nClasses, opt.kptype, opt.seq)
        self.is_train = train
        self.inputResH = opt.inputResH
        self.inputResW = opt.inputResW
        self.outputResH = opt.outputResH
        self.outputResW = opt.outputResW
        self.sigma = 1
        self.scale_factor = (0.2, 0.3)
        self.rot_factor = 40
        self.label_type = 'Gaussian'

        self.nJoints_coco = opt.nClasses
        self.nJoints = opt.nClasses

        self.accIdxs = tuple([i for i in range(1, opt.nClasses + 1)])
        self.flipRef = ()

        if train:
            filepath = os.path.join(
                '/home/penggao/projects/pose/kppose/linemod/%s/%s/%s/%s/' % (
                    opt.datatype, opt.nClasses, opt.kptype, opt.seq), "annot_train.h5")
            with h5py.File(filepath, 'r') as annot:
                # train
                self.imgname_coco_train = annot['imgname'][:]
                self.bndbox_coco_train = annot['bndbox'][:]
                self.part_coco_train = annot['part'][:]
        else:
            filepath = os.path.join(
                '/home/penggao/projects/pose/kppose/linemod/%s/%s/%s/%s' % (
                    'gt', opt.nClasses, opt.kptype, opt.seq), "annot_eval.h5")
            with h5py.File(filepath, 'r') as annot:
                # val
                self.imgname_coco_val = annot['imgname'][:]
                self.bndbox_coco_val = annot['bndbox'][:]
                self.part_coco_val = annot['part'][:]
        if train:
            self.size_train = self.imgname_coco_train.shape[0]
        else:
            self.size_val = self.imgname_coco_val.shape[0]

    def __getitem__(self, index):
        sf = self.scale_factor

        if self.is_train:
            part = self.part_coco_train[index]
            bndbox = self.bndbox_coco_train[index]
            imgname = self.imgname_coco_train[index]
        else:
            part = self.part_coco_val[index]
            bndbox = self.bndbox_coco_val[index]
            imgname = self.imgname_coco_val[index]

        # lambda: short form of a function; map: in every ele of imgname
        imgname = reduce(lambda x, y: x + y,
                         map(lambda x: chr(int(x)), imgname))
        img_path = os.path.join(self.img_folder, imgname+'.png')

        metaData = generateSampleBox(img_path, bndbox, part, self.nJoints,
                                     'coco', sf, self, train=self.is_train)

        inp, out, setMask = metaData
        return inp, out, setMask, 'coco'

    def __len__(self):
        if self.is_train:
            return self.size_train
        else:
            return self.size_val
