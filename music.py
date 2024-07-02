from moviepy.editor import AudioFileClip

def trim_mp3(input_file, output_file, start_time, end_time):
    """
    Trims an MP3 file from start_time to end_time and saves it as output_file.

    :param input_file: Path to the input MP3 file
    :param output_file: Path to save the trimmed MP3 file
    :param start_time: Start time in seconds
    :param end_time: End time in seconds
    """
    audio = AudioFileClip(input_file)
    trimmed_audio = audio.subclip(start_time, end_time)
    trimmed_audio.write_audiofile(output_file)

if __name__ == "__main__":
    input_file = "yt5s.io - THE CALL CENTRE _ Omeleto (128 kbps).mp3"  # Path to the input MP3 file
    output_file = "Call Center.mp3"  # Path to save the trimmed MP3 file
    start_time = 15 * 60 + 58  # Start time in seconds (15:58 minutes)
    end_time = 16 * 60 + 48  # End time in seconds (16:48 minutes)

    trim_mp3(input_file, output_file, start_time, end_time)
    print(f"The file has been successfully saved as {output_file}")
