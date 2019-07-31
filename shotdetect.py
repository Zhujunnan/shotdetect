#!/usr/bin/python

import cv2
import numpy as np
import os
import sys
import math
import copy

'''
  A simple yet effective python implementation for video shot detection of abrupt transition
  based on python OpenCV
'''

__hist_size__ = 128             # how many bins for each R,G,B histogram
__min_duration__ = 25           # if a shot has length less than this, merge it with others
__absolute_threshold__ = 1.0   # any transition must be no less than this threshold

class shotDetector(object):
    def __init__(self, video_path = None, min_duration=__min_duration__, output_dir=None):
        self.video_path = video_path
        self.min_duration = min_duration
        self.output_dir = output_dir
        self.factor = 6
        
    def run(self, video_path=None):
        if video_path is not None:
            self.video_path = video_path    
        assert (self.video_path is not None), "you should must the video path!"

        self.shots = []
        self.scores = []
        self.frames = []
        hists = []
        cap = cv2.VideoCapture(self.video_path)
        self.frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        while True:
            success, frame = cap.read()
            if not success:
                break
            self.frames.append(frame)
#            millis = cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
#            print millis
            # compute RGB histogram for each frame
            chists = [cv2.calcHist([frame], [c], None, [__hist_size__], [0,256]) \
                          for c in range(3)]
            chists = np.array([chist for chist in chists])
            hists.append(chists.flatten())
        # compute hist  distances
        self.scores = [np.ndarray.sum(abs(pair[0] - pair[1])) for pair in zip(hists[1:], hists[:-1])]
                      
    def pick_frame(self, obj_path = None, video_split_id = None):
        average_frame_div = sum(self.scores)/len(self.scores)
        self.obj_path = obj_path
        self.frame_index = []
        self.video_split_id = video_split_id
        for idx in range(len(self.scores)):
            if self.scores[idx] > self.factor * average_frame_div:
                self.frame_index.append(idx + 1)
                

        tmp_idx = copy.copy(self.frame_index)
        for i in range(0, len(self.frame_index) - 1):
            if self.frame_index[i + 1] - self.frame_index[i] < __min_duration__:
                del tmp_idx[tmp_idx.index(self.frame_index[i])]
        self.frame_index = tmp_idx
        print("special frames have {0}".format(len(self.frame_index)))
        
        if self.video_split_id and self.obj_path:
            # the real index start from 1 but time 0 and end add to it
            idx_new = copy.copy(self.frame_index)
            idx_new.insert(0, -1)
            if len(self.frames) - 1 - idx_new[-1] < __min_duration__:
                del idx_new[-1]
            idx_new.append(len(self.frames) - 1)
            

            
            idx_new = list(map(lambda x : x + 1.0, idx_new))
            frame_middle_idx = [math.ceil((pair[0] + pair[1])/2) for pair in zip(idx_new[:-1], idx_new[1:])]
            frame_middle_idx = list(map(lambda x : int(x), frame_middle_idx))
            #time_idx = map(lambda x : x / self.fps, idx_new)
            #timestamp_index = [(pair[0], pair[1]) for pair in zip(time_idx[:-1], time_idx[1:])]
            #print idx_new
            #print timestamp_index
            #print frame_middle_idx

            os.system("mkdir -p {0}".format(self.obj_path))
            tmp_idx = copy.copy(frame_middle_idx)
            for i in range(0, len(frame_middle_idx) - 1):
                if frame_middle_idx[i + 1] - frame_middle_idx[i] < __min_duration__:
                    del tmp_idx[tmp_idx.index(frame_middle_idx[i])]   
            frame_middle_idx = tmp_idx
            print(frame_middle_idx)
            print(idx_new)
            time_idx =[0.0]
            #frame_idx_tmp = map(lambda x : x + 1, frame_middle_idx)
            frame_idx_tmp = frame_middle_idx
            for i, element in enumerate(frame_idx_tmp):
                if i < len(frame_idx_tmp) - 1:
                    time_point = list(filter(lambda x : x <= frame_idx_tmp[i + 1], idx_new))[-1]
                    if time_point not in time_idx:
                        time_idx.append(time_point)
                #elif idx_new[-1] - time_idx[-1] < __min_duration__:
                else:
                    #del time_idx[-1]
                    time_idx.append(idx_new[-1])
#            for element in frame_middle_idx:                    
#                time_point = filter(lambda x: x > element, idx_new)[0]
#                time_idx.append(time_point)
            print(time_idx)
            time_idx_float = list(map(lambda x : x / self.fps, time_idx))
            print(time_idx_float)
            timestamp_index = [(pair[0], pair[1]) for pair in zip(time_idx_float[:-1], time_idx_float[1:])]
                               
            for i, idx in enumerate(frame_middle_idx):
                print(i, idx)
                cv2.imwrite("{0}/{1}@@{2:.1f}-{3:.1f}.jpg".format(self.obj_path, self.video_split_id, timestamp_index[i][0], timestamp_index[i][1]), self.frames[idx - 1])
                
                
        else:
            for idx in self.frame_index:
                if self.obj_path is None:
                    print("hello")
                    cv2.imwrite("{0}.jpg".format(idx + 1), self.frames[idx])
                    
                else:
                    os.system("mkdir -p {0}".format(self.obj_path))
                    cv2.imwrite("{0}/frame{1}.jpg".format(self.obj_path, idx + 1), self.frames[idx])
            
            
                    

                
if __name__ == "__main__":
#    if len(sys.argv) < 2 or len(sys.argv) > 3:
#        print "usage: ./shotdetect.py <video-path> [<key-frames-output-dir>]"
#        sys.exit()
    video_path = "test.mp4"
    
    factor = 6
    detector = shotDetector(video_path)
    detector.run()
    detector.pick_frame("/Users/zhujunnan/Desktop/cvTEST/Result", "test_now")
    print(len(detector.scores))
    print("frame_count is {0}".format(detector.frame_count))
    
    average_frame_div = sum(detector.scores)/len(detector.scores)
    print("average divergence = {0}".format(average_frame_div))
    
    #special_frame = [sp_frame for sp_frame in detector.scores if sp_frame > average_frame_div * detector.factor]
    
    #print "special frames have {0}".format(len(special_frame))
    
                      
                      
                      
                      
                      
#        print "max diff:", max(scores), "min diff:", min(scores)
#        # compute automatic threshold
#        mean_score = np.mean(scores)
#        std_score = np.std(scores)
#        threshold = max(__absolute_threshold__, mean_score + 3*std_score)
#
#        # decide shot boundaries
#        prev_i = 0
#        prev_score = scores[0]
#        for i, score in enumerate(scores[1:]):
#            if score>=threshold and abs(score-prev_score)>=threshold/2.0:
#                self.shots.append((prev_i, i+2))
#                prev_i = i + 2
#            prev_score = score
#        video_length = len(hists)
#        self.shots.append((prev_i, video_length))
#        assert video_length>=self.min_duration, "duration error"
#        
#        self.merge_short_shots()
#        
#        # save key frames
#        if self.output_dir is not None:
#            os.system("mkdir -p %s" % self.output_dir)
#            for shot in self.shots:
#                cv2.imwrite("%s/frame-%d.jpg" % (self.output_dir,shot[0]), frames[shot[0]])
#            print "key frames written to %s" % self.output_dir
#
#    def merge_short_shots(self):
#        # merge short shots
#        while True:
#            durations = [shot[1]-shot[0] for shot in self.shots]
#            shortest = min(durations)
#            # no need to merge
#            if shortest >= self.min_duration:
#                break
#            idx = durations.index(shortest)
#            left_half = self.shots[:idx]
#            right_half = self.shots[idx+1:]
#            shot = self.shots[idx]
#
#            # can only merge left
#            if idx == len(self.shots)-1:
#                left = True                
#            # can only merge right
#            elif idx == 0:
#                left = False                
#            else:
#                # otherwise merge the shorter one
#                if durations[idx-1] < durations[idx+1]:
#                    left = True
#                else:
#                    left = False
#            if left:
#                self.shots = left_half[:-1] + [(left_half[-1][0],shot[1])] + right_half
#            else:
#                self.shots = left_half + [(shot[0],right_half[0][1])] + right_half[1:]




