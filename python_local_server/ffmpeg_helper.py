import os
import ffmpeg


def trim_video(in_file, out_file, start, end):
    if os.path.exists(out_file):
        os.remove(out_file)

    # probe_result = ffmpeg.probe(in_file)
    # duration = probe_result.get("format", {}).get("duration", None)

    input_stream = ffmpeg.input(in_file)
    # pts = "PTS-STARTPTS"
    video = input_stream.trim(start=start, end=end)
    output = ffmpeg.output(video, out_file)
    output.run()


trim_video("my_file.webm", "out.webm", 0, 60)