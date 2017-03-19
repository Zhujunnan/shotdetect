#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 10 20:55:07 2017

@author: zhujunnan
"""

import shotdetect
import os

All_video_path = "/Users/zhujunnan/Desktop/en/"




video_file_path = [All_video_path + file for file in os.listdir(All_video_path) if 'topic' in file]
#print video_file_path
#for video_path in video_file_path:
#    mp4_path = filter(lambda x : x.endswith('mp4'), os.listdir(video_path))
#    for i, mp4_file in enumerate(mp4_path):
#        os.rename(video_path + '/' + mp4_file, video_path + '/' + 'video{0}.mp4'.format(i + 1)) 


                   
for video_file in video_file_path:
    for video in os.listdir(video_file):
        if video.endswith('.mp4'):
            video_id = video[:-4]
            print "video_id is {0}".format(video_id)
            video_id_path = video_file + '/' + video
            print "video_id_path is {0}".format(video_id_path)
            video_output_dir = video_file + '/imageset'  
            print "video_output_dir is {0}".format(video_output_dir)
            detect = shotdetect.shotDetector(video_id_path)
            detect.run()
            detect.pick_frame(video_output_dir, video_id)
            