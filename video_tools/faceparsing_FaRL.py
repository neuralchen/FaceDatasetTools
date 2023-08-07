#!/usr/bin/env python3
# -*- coding:utf-8 -*-
#############################################################
# File: soft_erosion.py
# Created Date: Saturday July 3rd 2021
# Author: Chen Xuanhong
# Email: chenxuanhongzju@outlook.com
# Last Modified:  Wednesday, 18th May 2022 1:15:00 pm
# Modified By: Chen Xuanhong
# Copyright (c) 2021 Shanghai Jiao Tong University
#############################################################
import  os

import  torch

import  numpy as np

from   .soft_erosion import SoftErosion
from   .morphological_operation import dilate,erode
import torch
import torch.nn as nn
import torch.nn.functional as F
import FaRL.farl.network as mask_network
from   FaRL.farl.experiments.face_parsing.network import FaceParsingTransformer

# 0-- background
# 1-- face skin
# 2-- l_brow
# 3-- r_brow 
# 4-- l_eye
# 5-- r_eye
# 6-- nose
# 7-- u_lip
# 8-- mouth
# 9-- l_lip
# 10-- hair

def encode_segmentation_rgb(segmentation, no_neck=True):
    parse = segmentation

    # face_part_ids = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13] if no_neck else [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]
    face_part_ids = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13] if no_neck else [1, 2, 4, 5,6, 7, 8, 10, 11, 12, 13, 14]
    # mouth_id = 11
    # hair_id = 17
    face_map = torch.zeros([parse.shape[0], parse.shape[1]]).cuda()
    # mouth_map = torch.zeros([parse.shape[0], parse.shape[1]]).cuda()
    # hair_map = np.zeros([parse.shape[0], parse.shape[1]])

    for valid_id in face_part_ids:
        valid_index = torch.where(parse==valid_id)
        face_map[valid_index] = 1.0
    # valid_index = torch.where(parse==mouth_id)
    # mouth_map[valid_index] = 1.0
    # valid_index = np.where(parse==hair_id)
    # hair_map[valid_index] = 255
    #return np.stack([face_map, mouth_map,hair_map], axis=2)
    # return np.stack([face_map, mouth_map], axis=2)
    # results = torch.from_numpy(face_map + mouth_map)
    return face_map #+ mouth_map

def encode_segmentation_batch(parse, no_neck=True):
    # face_part_ids = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13] if no_neck else [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]
    # face_part_ids = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13] if no_neck else [1, 2, 4, 5,6, 7, 8, 10, 11, 12, 13, 14]
    face_part_ids = [7]
    # 1-- face skin
    # 2-- l_brow
    # 3-- r_brow 
    # 4-- l_eye
    # 5-- r_eye
    # 6-- nose
    # 7-- 
    # mouth_id = 11
    # hair_id = 17
    face_map = torch.zeros((parse.shape[0], parse.shape[1], parse.shape[2])).cuda()

    for valid_id in face_part_ids:
        face_map += torch.where(parse == valid_id, 1.0, 0.0)

    return face_map

def encode_segmentation_label_batch(parse, label=[0]):
    # face_part_ids = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13] if no_neck else [1, 2, 3, 4, 5, 6, 7, 8, 10, 11, 12, 13, 14]
    # face_part_ids = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13] if no_neck else [1, 2, 4, 5,6, 7, 8, 10, 11, 12, 13, 14]
    face_part_ids = label
    
    face_map = torch.zeros((parse.shape[0], parse.shape[1], parse.shape[2])).cuda()

    for valid_id in face_part_ids:
        face_map += torch.where(parse == valid_id, 1.0, 0.0)

    return face_map

class FaceParsing():
    def __init__(self):
        backbone            = mask_network.FaRLVisualFeatures(model_type='base', model_path='./FaRL/FaRL-Base-Patch16-LAIONFace20M-ep64.pth')
        head                = mask_network.MMSEG_UPerHead(num_classes=11, in_channels=[768, 768, 768, 768], channels=768)
        self.parsing_model  = FaceParsingTransformer(backbone, head, [512, 512])

        checkpoint          = torch.load("./FaRL/450300_100.pth", map_location=torch.device('cpu'))
        self.parsing_model.load_state_dict(checkpoint["networks"]["main"])

        self.parsing_model.eval()
        self.parsing_model.cuda()

        self.smooth_mask = SoftErosion(kernel_size=19, threshold=0.9, iterations=25).cuda()

    def reset_smooth_mask(self,iteration=10,kernel=17):

        self.smooth_mask = SoftErosion(kernel_size=kernel, threshold=0.9, iterations=iteration).cuda()
    
    def parsing(self, img):
        return self.parsing_model.forward(img)
    
    @torch.no_grad()
    def __call__(self, foreground: torch.Tensor, background: torch.Tensor):
        r"""
        Function invoked when calling the function for seemless fusion of face and original image.

        Args:
            foreground (`torch.Tensor`): B C H W
                [0,1.0] input face image, CUDA.
            background (`torch.Tensor`): B C H W
                [0,1.0] the original image, CUDA.
        Examples:

        Returns:
            'torch.Tensor'.
        """
        mask_pred = self.parsing_model.forward(foreground)[0]
        
        mask_pred = mask_pred.max(1)[1]# #[0] # HW
        
        # mask_pred = ((mask_pred > 0) * (mask_pred < 10)) #> 0.4
        mask_pred = encode_segmentation_batch(mask_pred)
        mask_pred = mask_pred.float()
        # if mask_pred.sum() >= 5000:
        soft_face_mask_tensor, _ = self.smooth_mask(mask_pred.unsqueeze_(1))
        soft_face_mask_tensor    = torch.clip(soft_face_mask_tensor[:,0,:,:],0.0,1.0)
        foreground =  foreground * soft_face_mask_tensor
        backgroud  =  background * (1 - soft_face_mask_tensor)
        return foreground + backgroud, soft_face_mask_tensor
    
    
    def getmask(self, mask_img: torch.Tensor, label = [1, 2, 3, 4, 5, 6, 10, 11, 12, 13]):
        r"""
        Function invoked when calling the function for seemless fusion of face and original image.

        Args:
            foreground (`torch.Tensor`):
                [0,1.0] input face image.
            background (`torch.Tensor`):
                [0,1.0] the original image.
        Examples:

        Returns:
            'torch.Tensor'.
        """

        mask_pred = self.parsing_model.forward(mask_img)[0]
        
        mask_pred = mask_pred.max(1)[1]# #[0] # HW
        
        mask_pred = encode_segmentation_label_batch(mask_pred, label)
        mask_pred = mask_pred.float()
        print(mask_pred.shape)
        # if mask_pred.sum() >= 5000:
        return mask_pred
    
    def unionmask_fusion(self, foreground: torch.Tensor, background: torch.Tensor):
        r"""
        Function invoked when calling the function for seemless fusion of face and original image.

        Args:
            foreground (`torch.Tensor`): B C H W
                [0,1.0] input face image, CUDA.
            background (`torch.Tensor`): B C H W
                [0,1.0] the original image, CUDA.
        Examples:

        Returns:
            'torch.Tensor'.
        """
        fore_mask = self.parsing_model.forward(foreground)[0]
        
        fore_mask = fore_mask.max(1)[1]# #[0] # HW
        fore_mask = ((fore_mask > 0) * (fore_mask < 10)) #> 0.4
        fore_mask = fore_mask.float()

        back_mask = self.parsing_model.forward(background)[0]
        back_mask = back_mask.max(1)[1]# #[0] # HW
        back_mask1 = ((back_mask > 0) * (back_mask < 10)) #> 0.4
        back_mask1 = back_mask1.float()

        hair_mask = (back_mask == 10) #> 0.4
        hair_mask = hair_mask.float().unsqueeze_(1)
        # background_mask = (back_mask == 0) #> 0.4
        # background_mask = background_mask.float()
        # fore_mask = torch.clip(fore_mask - hair_mask, 0.0, 1.0)
        fore_mask = torch.clip(fore_mask + back_mask1, 0.0, 1.0) 
        
        # fore_mask = torch.clip(fore_mask , 0.0, 1.0)
        fore_mask = dilate(fore_mask,31)
        # fore_mask = torch.clip(fore_mask, 0.0, 1.0)
        fore_mask = fore_mask.unsqueeze_(1)#.unsqueeze_(0)
        fore_mask, _ = self.smooth_mask(fore_mask)
        fore_mask = torch.clip(fore_mask, 0.0, 1.0)#.to(foreground.device)
        foreground= foreground * fore_mask
        background1 = background * (1 - fore_mask)
        results   = foreground + background1
        # hair_mask = erode(hair_mask,11)
        hair_mask, _ = self.smooth_mask(hair_mask)
        hair_mask = torch.clip(hair_mask, 0.0, 1.0)
        results   = results * (1-hair_mask) + background * hair_mask
        return results
    
    def hairmask_fusion(self, foreground: torch.Tensor, background: torch.Tensor):
        r"""
        Function invoked when calling the function for seemless fusion of face and original image.

        Args:
            foreground (`torch.Tensor`): B C H W
                [0,1.0] input face image, CUDA.
            background (`torch.Tensor`): B C H W
                [0,1.0] the original image, CUDA.
        Examples:

        Returns:
            'torch.Tensor'.
        """

        face_part_ids = [6, 17]
        

        back_mask = self.parsing_model.forward(background)[0]
        back_mask = back_mask.squeeze(0).argmax(0)
        hair_mask = torch.zeros([back_mask.shape[0], back_mask.shape[1]]).cuda()
        for valid_id in face_part_ids:
            valid_index = torch.where(back_mask==valid_id)
            hair_mask[valid_index] = 1.0

        if hair_mask.sum() >= 1000:


            mask_pred                = hair_mask.unsqueeze_(0).unsqueeze_(0)
            soft_face_mask_tensor, _ = self.smooth_mask(mask_pred)
            soft_face_mask_tensor    = torch.clip(soft_face_mask_tensor, 0.0, 1.0).to(foreground.device)
            foreground               = foreground * (1 - soft_face_mask_tensor)
            backgroud                = background * soft_face_mask_tensor
            # print("foreground after shape:",foreground.shape)
            results                  = foreground + backgroud
            return results
        else:
            return foreground
    
    def hairmask_fusion_batch(self, foreground: torch.Tensor, background: torch.Tensor):
        r"""
        Function invoked when calling the function for seemless fusion of face and original image.

        Args:
            foreground (`torch.Tensor`): B C H W
                imagenet value range, the input face image, CUDA.
            background (`torch.Tensor`): B C H W
                imagenet value range, the original image, CUDA.
        Examples:

        Returns:
            'torch.Tensor'.
        """

        face_part_ids = [6, 17]
        

        back_mask = self.parsing_model.forward(background)[0]
        back_mask = back_mask.argmax(0)
        hair_mask = torch.zeros([back_mask.shape[1], back_mask.shape[2]]).cuda()
        for valid_id in face_part_ids:
            valid_index = torch.where(back_mask==valid_id)
            hair_mask[valid_index] = 1.0

        if hair_mask.sum() >= 1000:


            mask_pred                = hair_mask.unsqueeze_(0).unsqueeze_(0)
            soft_face_mask_tensor, _ = self.smooth_mask(mask_pred)
            soft_face_mask_tensor    = torch.clip(soft_face_mask_tensor, 0.0, 1.0).to(foreground.device)
            foreground               = foreground * (1 - soft_face_mask_tensor)
            backgroud                = background * soft_face_mask_tensor
            # print("foreground after shape:",foreground.shape)
            results                  = foreground + backgroud
            return results
        else:
            return foreground