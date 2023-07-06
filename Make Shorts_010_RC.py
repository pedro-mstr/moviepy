import os
import re
import time
import shutil
import random
from moviepy.config import change_settings
from moviepy.editor import ImageClip, VideoFileClip, CompositeVideoClip, TextClip, concatenate_videoclips, vfx
change_settings({"IMAGEMAGICK_BINARY": r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"})

# Videos Directories
input_dir = r"C:\Youtube\moviepy\Downloaded_Videos\1"
output_dir = r"C:\Youtube\moviepy\Done\1"
used_dir = r"C:\Youtube\moviepy\Used\1"

subscribe_overlay_dir = r"C:\Youtube\Subscribe_videos\6.mp4"

# input the desired resolution for the final video
final_width = 1080
final_height = 1920

# input the desired minimum and maximum duration of the final video
video_min_lengh = 50
video_max_lengh = 60

# add_numbers_to_clips Settings:
number_font_dir = r"C:\\Youtube\\fonts\\CuteMeow-51Pra.otf"
number_fontsize = 200
number_color = "rgba(173,217,230,0.9)"
number_stroke_color = "white"
number_stroke_width = 2
number_position_x = 60
number_position_y = 50

# add_random_images_to_clips Settings:
emojis_dir = r"C:\Youtube\emojis\300x300"
emojis_start_timer = 0
emojis_lenght = 5

bottom_dir = r"C:\Youtube\Bottom_png\400px"

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

def get_random_image(image_dir):
    images = [f for f in os.listdir(image_dir) if f.endswith(".png")]
    return random.choice(images)


def process_files(file_list):
    print("Processing files...")
    total_duration = 0
    clip_list = []
    used_files = []

    while file_list:
        print(f"Processing file: {file_list[0]}")
        clip = VideoFileClip(os.path.join(input_dir, file_list[0]))

        # Resize the clip before adding it to the list
        clip = clip.fx(vfx.resize, newsize=(final_width, final_height))

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
        txt_clip = TextClip(f"{total_clips - i}", fontsize=number_fontsize, color=number_color, stroke_color=number_stroke_color, stroke_width=number_stroke_width, font=number_font_dir)

        # Position the text clip
        txt_clip = txt_clip.set_position((number_position_x, number_position_y)).set_duration(clip.duration)

        # Add a 1 second fade in and fade out effect
        txt_clip = txt_clip.crossfadein(1).crossfadeout(1)

        # Overlay the TextClip on the resized video clip
        clip_list[i] = CompositeVideoClip([clip, txt_clip])

    return clip_list


def add_random_emojis_to_clips(clip_list, image_dir):
    for i, clip in enumerate(clip_list):
        # Get a random image
        image_path = os.path.join(image_dir, get_random_image(image_dir))
        image = ImageClip(image_path)

        # Set the opacity of the image
        image = image.set_opacity(0.8)  # Adjust as needed

        # Set the start time, duration, and position of the image
        image = image.set_start(emojis_start_timer).set_duration(emojis_lenght)
        
        # Position the image at the center bottom of the video, 40px above the bottom
        image = image.set_position(('center', clip.size[1] - image.size[1] - 500))

        # Add a 1 second fade in and fade out effect
        image = image.crossfadein(1).crossfadeout(1)

        # Overlay the image on the clip
        clip_list[i] = CompositeVideoClip([clip, image])
    return clip_list

def add_random_bottom_to_clips(clip_list, image_dir):
    for i, clip in enumerate(clip_list):
        # Get a random image
        image_path = os.path.join(image_dir, get_random_image(image_dir))
        image = ImageClip(image_path)

        # Set the opacity of the image
        image = image.set_opacity(0.9)  # Adjust as needed

        # Set the start time, duration, and position of the image
        image = image.set_start(0).set_duration(clip.duration)
        
        # Position the image at the center bottom of the video, and the bottom
        image = image.set_position(("center", "bottom"))

        # Overlay the image on the clip
        clip_list[i] = CompositeVideoClip([clip, image])
    return clip_list


def add_overlay_video(clip_list, overlay_video_path, overlay_start):
    # Load the overlay video
    overlay = VideoFileClip(overlay_video_path)

    # Remove black color from the overlay video
    overlay = overlay.fx(vfx.mask_color, color=[0, 0, 0], thr=100, s=10)

    # Set the start time of the overlay video
    overlay = overlay.set_start(overlay_start)

    # Add the overlay video to the last clip
    last_clip = clip_list[-1]
    last_clip = CompositeVideoClip([last_clip, overlay])

    # Replace the last clip with the new composite clip
    clip_list[-1] = last_clip

    return clip_list

while file_list:
    print("Finding clips to merge...")
    clips_to_merge, used_files = process_files(file_list)
    if clips_to_merge:
        print("Clips found. Starting to merge...")

        # Add numbers to the clips
        clips_to_merge = add_numbers_to_clips(clips_to_merge)

        # Add random images to the clips
        clips_to_merge = add_random_emojis_to_clips(clips_to_merge, emojis_dir)

        # Add random bottom to the clips
        clips_to_merge = add_random_bottom_to_clips(clips_to_merge, bottom_dir)

        # Add the subscribe overlay video 4 seconds before the end of the last clip
        clips_to_merge = add_overlay_video(clips_to_merge, subscribe_overlay_dir, clips_to_merge[-1].duration - 4)

        # resize and aspect ratio
        final_clip = concatenate_videoclips([clip.fx(vfx.resize, height=final_height) for clip in clips_to_merge])  
        final_clip = final_clip.fx(vfx.resize, newsize=(final_width, final_height))
        print("Writing video file...")
        final_clip.write_videofile(
            os.path.join(output_dir, f"{counter}.mp4"),
            codec="libx264",
            audio_codec="aac",
            bitrate='8000k',  # Set the bitrate to 4000 kbps
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