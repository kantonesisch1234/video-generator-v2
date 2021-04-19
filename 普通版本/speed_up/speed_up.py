from vid_utils import Video, concatenate_videos

speed_str = input("輸入速度：")
speed = float(speed_str)

videos = [
  Video(speed=speed, path="output.mp4")
]

concatenate_videos(videos=videos, output_file=f"output_sped_up.mp4")


