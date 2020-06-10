# Video Movement Splitter
> a video split util
> used for videos or live stream

### usage
```python
from VideoProcess import VideoProcess
# 5 is the fps of the video
# test_split is the dir of videos to be saved
video_process = VideoProcess(5,'test_split')
for frame in frames:
    video_process.new_frame(frame)
video_process.finish()
```

the frames could be frames read from a video, also could be from a live stream. 
This util is frame-based. 