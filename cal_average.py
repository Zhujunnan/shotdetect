#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 15:08:17 2017

@author: zhujunnan
"""
import os
import imghdr
import cv2
import numpy as np

__hist_size__ = 128 

class cal_factor(object):
    
    def __init__(self, pick_frame_path = None, origin_frame_path = None):

        assert (os.path.exists(pick_frame_path) and os.path.exists(origin_frame_path)) \
            , "please ensure your input file path"
        self.pick_frame_path = pick_frame_path
        self.origin_frame_path = origin_frame_path
#        self.pick_frame_folder = [file for file in os.listdir(pick_frame_path) if imghdr.what(file)]
#        self.origin_frame_folder = [file for file in os.listdir(origin_frame_path) if imghdr.what(file)]
        self.pick_frame_folder = os.listdir(pick_frame_path)
        self.origin_frame_folder = os.listdir(origin_frame_path)
                                    
    #calculate the average divergence of the hist                                     
    def cal_average_div(self, pick_frame_folder = None, origin_frame_folder = None):
        self.average_origin_result = 0.0
        self.average_pick_result = 0.0
        self.factor = 0.0
        origin_scores = []
        pick_scores = []
        origin_frame_expand = '.png'        
        origin_hist = []
        if pick_frame_folder is not None:
            self.pick_frame_folder = pick_frame_folder
        if origin_frame_folder is not None:
            self.origin_frame_folder =origin_frame_folder
        
        pick_frame_num = sorted([int(picture[5:].split('.')[0]) for picture in self.pick_frame_folder])
        print pick_frame_num
#        origin_frame_expand = origin_frame_folder[0].split('.')[1]

        origin_frame_num = sorted([int(picture[5:].split('.')[0]) for picture in self.origin_frame_folder])
        print len(origin_frame_num)
        for file_num in origin_frame_num:
            frame =cv2.imread(self.origin_frame_path + "frame" +str(file_num).zfill(5) + origin_frame_expand)
            print self.origin_frame_path + str(file_num).zfill(5) + origin_frame_expand
            chists = [cv2.calcHist([frame], [c], None, [__hist_size__], [0,256]) for c in range(3)]   
           # print "hello"
            chists = np.array([chist for chist in chists])
            origin_hist.append(chists.flatten())
            
        origin_scores = [np.ndarray.sum(abs(pair[0] - pair[1])) for pair in zip(origin_hist[1:], origin_hist[:-1])]
                         
        for file_num in pick_frame_num:
            frame =cv2.imread(self.pick_frame_path + "frame" + str(file_num).zfill(5) + origin_frame_expand) 
            print self.pick_frame_path + "frame" + str(file_num).zfill(5) + origin_frame_expand
            chists_1 = [cv2.calcHist([frame], [c], None, [__hist_size__], [0,256]) \
                          for c in range(3)]  
            chists_1 = np.array([chist for chist in chists_1]).flatten()
            frame_previous = cv2.imread(self.origin_frame_path + "frame" + str(file_num - 1).zfill(5) + origin_frame_expand)
            chists_2 = [cv2.calcHist([frame_previous], [c], None, [__hist_size__], [0,256]) \
                          for c in range(3)]  
            chists_2 = np.array([chist for chist in chists_2]).flatten()
            pick_scores.append(np.ndarray.sum(abs(chists_1 - chists_2)))
        print pick_scores    
        self.average_origin_result = sum(origin_scores)/len(origin_scores)
        self.average_pick_result = sum(pick_scores)/len(pick_scores)
        self.factor = self.average_pick_result/self.average_origin_result
        
        
if __name__ == "__main__":
    
    pick_frame_path = "/Users/zhujunnan/Desktop/frame/two_seg/"
    origin_frame_path = "/Users/zhujunnan/Desktop/frame/two_origin/"
    
    detector = cal_factor(pick_frame_path, origin_frame_path)
    
    detector.cal_average_div()
    print detector.factor