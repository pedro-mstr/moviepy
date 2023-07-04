import os
import re
import time
import shutil
from moviepy.editor import CompositeVideoClip
from moviepy.editor import TextClip, concatenate_videoclips
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from moviepy.config import change_settings
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})


input_dir = r'C:\Youtube\moviepy\Downloaded_Videos\1'
output_dir = r'C:\Youtube\moviepy\Done\1'
used_dir = r'C:\Youtube\moviepy\Used\1'  # directory to move used files

# input the desired resolution for the final video
final_width = 1080
final_height = 1920

# input the desired minimum and maximum duration of the final video
video_min_lengh = 50
video_max_lengh = 60

def get_next_file_number(output_dir):
    # Get list of existing files in the output directory
    existing_files = os.listdir(output_dir)

    # Extract the numbers from the file names using a regular expression
    numbers = [int(re.search(r'(\d+)', file).group()) for file in existing_files if re.search(r'(\d+)', file)]

    # If no numbered files exist, start from 1, else get max number and add 1
    if not numbers:
        return 1
    else:
        return max(numbers) + 1
    
# Use the function to get the next file number
counter = get_next_file_number(output_dir)
print(f"The next file will be named: {counter}.mp4")
time.sleep(1)

print("Checking if output and used directories exist...")
if not os.path.exists(output_dir):  # Create output_dir if it doesn't exist
    os.makedirs(output_dir)
    print(f"Created output directory: {output_dir}")

if not os.path.exists(used_dir):  # Create used_dir if it doesn't exist
    os.makedirs(used_dir)
    print(f"Created used directory: {used_dir}")

print("Getting list of .mp4 files...")
file_list = [f for f in os.listdir(input_dir) if f.endswith(".mp4")]

# Sorting files for proper sequencing.
print("Sorting files...")
file_list.sort()

# Sort files by duration
#print("Sorting files by duration...")
#file_list.sort(key=lambda x: VideoFileClip(os.path.join(input_dir, x)).duration)

def process_files(file_list):
    print("Processing files...")
    total_duration = 0
    clip_list = []
    used_files = []

    while file_list:
        print(f"Processing file: {file_list[0]}")
        clip = VideoFileClip(os.path.join(input_dir, file_list[0]))

        if total_duration + clip.duration > video_max_lengh:
            print(f"Skipping file: {file_list[0]} as it exceeds the maximum length")
            file_list.pop(0)
            continue

        total_duration += clip.duration
        clip_list.append(clip)
        used_files.append(file_list.pop(0))

        if total_duration >= video_min_lengh:
            break

    print(f"\nFound a Combo with total duration: {total_duration}")

    return clip_list, used_files

def add_numbers_to_clips(clip_list):
    total_clips = len(clip_list)
    for i, clip in enumerate(clip_list):
        # Create a TextClip for the clip number
        txt_clip = TextClip(f"{total_clips - i:03d}", fontsize=100, color='rgb(173, 217, 230)', stroke_color='white', stroke_width=4, font=r'C:\Users\Administrator\Desktop\Bangers-Regular.ttf')
        txt_clip = txt_clip.set_position(('center', 25)).set_duration(clip.duration)

        # Overlay the TextClip on the video clip
        clip_list[i] = CompositeVideoClip([clip, txt_clip])

    return clip_list

while file_list:
    print("Finding clips to merge...")
    clips_to_merge, used_files = process_files(file_list)
    if clips_to_merge:
        print("Clips found. Starting to merge...")

        # Add numbers to the clips
        clips_to_merge = add_numbers_to_clips(clips_to_merge, len(used_files))

        final_clip = concatenate_videoclips([clip.fx(vfx.resize, height=final_height) for clip in clips_to_merge])  # resize maintaining aspect ratio
        final_clip = final_clip.fx(vfx.resize, newsize=(final_width, final_height))  # hard set size
        print("Writing video file...")
        final_clip.write_videofile(
            os.path.join(output_dir, f"{counter}.mp4"),
            codec="libx264",
            audio_codec="aac",
            temp_audiofile='temp-audio-1.m4a', 
            remove_temp=True,
            preset="ultrafast",  # slower encoding
            threads=4
        )
        print(f"Video file written: {counter}.mp4")
        counter += 1

        # Close the clip manually
        for clip in clips_to_merge:
            clip.close()
            time.sleep(1)

        # move used files to the used_dir
        for filename in used_files:
            print(f"Moving used file: {filename} to used directory")
            shutil.move(os.path.join(input_dir, filename), used_dir)
            time.sleep(1)
