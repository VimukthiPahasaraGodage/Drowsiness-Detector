from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import os
import ffmpeg


def trim_video(in_file, out_file, start, end, target_size=2):
    intermediate_file = "intermediate_output.mkv"

    if os.path.exists(out_file):
        os.remove(out_file)

    if os.path.exists(intermediate_file):
        os.remove(intermediate_file)

    ffmpeg_extract_subclip(in_file, start, end, targetname=intermediate_file)
    if os.path.exists(intermediate_file):
        compress_video(intermediate_file, out_file, target_size * 1000)
        os.remove(intermediate_file)


def compress_video(video_full_path, output_file_name, target_size):
    probe = ffmpeg.probe(video_full_path)
    duration = float(probe['format']['duration'])
    target_total_bitrate = (target_size * 1024 * 8) / (1.073741824 * duration)

    video_bitrate = target_total_bitrate

    i = ffmpeg.input(video_full_path)
    ffmpeg.output(i, os.devnull,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 1, 'f': 'mp4'}
                  ).overwrite_output().run()
    ffmpeg.output(i, output_file_name,
                  **{'c:v': 'libx264', 'b:v': video_bitrate, 'pass': 2, 'c:a': 'aac'}
                  ).overwrite_output().run()
