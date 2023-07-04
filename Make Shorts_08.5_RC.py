import os
import re
import time
import shutil
from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
from multiprocessing import Pool

# input the desired resolution for the final video
final_width = 1080
final_height = 1920

# input the desired minimum and maximum duration of the final video
video_min_lengh = 55
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

def process_directory(input_dir, output_dir, used_dir):
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

while file_list:
    print("Finding clips to merge...")
    clips_to_merge, used_files = process_files(file_list)
    if clips_to_merge:
        print("Clips found. Starting to merge...")
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
        for clip in clips_to_merge:
            print(f"Moving used file: {clip.filename} to used directory")
            shutil.move(clip.filename, used_dir)
            time.sleep(1)

if __name__ == "__main__":
    directories = [
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\1", "C:\\Youtube\\moviepy\\Done\\1", "C:\\Youtube\\moviepy\\Used\\1"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\2", "C:\\Youtube\\moviepy\\Done\\2", "C:\\Youtube\\moviepy\\Used\\2"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\2", "C:\\Youtube\\moviepy\\Done\\2", "C:\\Youtube\\moviepy\\Used\\3"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\2", "C:\\Youtube\\moviepy\\Done\\2", "C:\\Youtube\\moviepy\\Used\\4"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\2", "C:\\Youtube\\moviepy\\Done\\2", "C:\\Youtube\\moviepy\\Used\\5"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\2", "C:\\Youtube\\moviepy\\Done\\2", "C:\\Youtube\\moviepy\\Used\\6"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\2", "C:\\Youtube\\moviepy\\Done\\2", "C:\\Youtube\\moviepy\\Used\\7"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\2", "C:\\Youtube\\moviepy\\Done\\2", "C:\\Youtube\\moviepy\\Used\\8"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\2", "C:\\Youtube\\moviepy\\Done\\2", "C:\\Youtube\\moviepy\\Used\\9"),
        ("C:\\Youtube\\moviepy\\Downloaded_Videos\\10", "C:\\Youtube\\moviepy\\Done\\10", "C:\\Youtube\\moviepy\\Used\\10"),
    ]

    with Pool(10) as p:
        p.starmap(process_directory, directories)
