import cv2
import numpy as np
from datetime import datetime
import os

class VideoProcess:

    def __init__(self,video_fps,save_path):
        self.video_fps = video_fps
        self.save_path = save_path
        self.kernel = np.ones((7, 7), np.uint8)
        self.event_window = []
        self.buffered_frames = []
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(detectShadows=False)
        # self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        
        self.threshold = 15
        self.num_frames_post_event = 0
        self.in_motion_event = False
        
        # size of start condition
        self.min_event_len = 15
        # size of end condition
        self.post_event_len = 70
        # size of buffer
        self.pre_event_len = 15
        

    def new_frame(self,frame):
        frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame_mask = self.bg_subtractor.apply(frame_gray)
        frame_filt = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, self.kernel)
        frame_score = np.sum(frame_filt) / float(frame_filt.shape[0] * frame_filt.shape[1])

        self.event_window.append(frame_score)
        self.event_window = self.event_window[-self.min_event_len:]

        if self.in_motion_event:
            # in event or post event, write all queued frames to file,
            # and write current frame to file.
            # if the current frame doesn't meet the threshold, increment
            # the current scene's post-event counter.
            
            self.video_writer.write(frame)
            if frame_score >= self.threshold:
                # 继续录制
                self.num_frames_post_event = 0
            else:
                self.num_frames_post_event += 1
                # 结束录制
                if self.num_frames_post_event >= self.post_event_len:
                    self.finish()
        else:
            self.buffered_frames.append(frame)
            self.buffered_frames = self.buffered_frames[-self.pre_event_len:]
            if len(self.event_window) >= self.min_event_len and all(
                    score >= self.threshold for score in self.event_window):
                self.in_motion_event = True
                self.event_window = []
                self.num_frames_post_event = 0
                # Open new VideoWriter if needed, write buffered_frames to file.
                
                cur_dt = datetime.now()
                self.video_name = cur_dt.strftime('%Y%m%d-%H%M%S') + '.mp4'
                self.compress_name = cur_dt.strftime('%Y%m%d-%H%M%S') + '_comp.mp4'
                # self.output_path = '%s/%s' % (self.save_path,self.video_name)
                self.video_path = os.path.join(self.save_path,self.video_name)
                self.compress_path = os.path.join(self.save_path,self.compress_name)
                print('start to record %s...' % self.video_name)
                self.video_writer = cv2.VideoWriter(
                    self.video_path, self.fourcc, self.video_fps,
                    (1920,1080))
                for frame in self.buffered_frames:
                    self.video_writer.write(frame)
                self.buffered_frames = []

    def finish(self):
        if not self.in_motion_event:
            return
        self.in_motion_event = False
        self.video_writer.release()
        print('end recording %s.' % self.video_name)
        print('----------')


if __name__ == "__main__":
    # test split a video file
    import time
    video_process = VideoProcess(5,'test_split')
    cap = cv2.VideoCapture('videos\\20191114-154605.avi')
    start = time.time()
    while(cap.isOpened()):
        ret, frame = cap.read()
        if not ret:
            break
        video_process.new_frame(frame)

    cap.release()
    cv2.destroyAllWindows()
    print('time cost:%d' % (time.time() - start))