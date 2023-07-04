import os
import shutil
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx

input_dir = r'C:\Youtube\moviepy\Downloaded_Videos'
output_dir = r'C:\Youtube\moviepy\Done'
used_dir = r'C:\Youtube\moviepy\Used'  # directory to move used files

# input the desired resolution for the final video
final_width = 1080
final_height = 1920

# input the desired minimum and maximum duration of the final video
video_min_lengh = 55
video_max_lengh = 60

if not os.path.exists(output_dir):  # Create output_dir if it doesn't exist
    os.makedirs(output_dir)

if not os.path.exists(used_dir):  # Create used_dir if it doesn't exist
    os.makedirs(used_dir)

file_list = [f for f in os.listdir(input_dir) if f.endswith(".mp4")]
file_list.sort()  # Sorting files for proper sequencing.

# Sort files by duration
#file_list.sort(key=lambda x: VideoFileClip(os.path.join(input_dir, x)).duration)

counter = 203  # File name counter for files in the output dir.

def process_files(file_list):
    total_duration = 0
    clip_list = []

    while file_list:
        clip = VideoFileClip(os.path.join(input_dir, file_list[0]))

        if total_duration + clip.duration > video_max_lengh:
            file_list.pop(0)
            continue

        total_duration += clip.duration
        clip_list.append(clip)
        file_list.pop(0)

        if total_duration >= video_min_lengh:
            break
    print("\nFound a Combo with",total_duration)

    return clip_list

while file_list:
    clips_to_merge = process_files(file_list)
    if clips_to_merge:
        final_clip = concatenate_videoclips([clip.fx(vfx.resize, height=final_height) for clip in clips_to_merge])  # resize maintaining aspect ratio
        final_clip = final_clip.fx(vfx.resize, newsize=(final_width, final_height))  # hard set size
        final_clip.write_videofile(
            os.path.join(output_dir, f"{counter}.mp4"),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True,
            preset="ultrafast",  # slower encoding
            threads=16
        )
        counter += 1

        # move used files to the used_dir
        for clip in clips_to_merge:
            shutil.move(clip.filename, used_dir)
