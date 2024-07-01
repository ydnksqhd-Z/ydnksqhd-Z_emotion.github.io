from pydub import AudioSegment

# 加载MP3文件
mp3_audio = AudioSegment.from_file("sound_track/asr_example_zh.mp3", format="mp3")

# 设置导出的PCM格式参数：16位采样深度，单声道，44100Hz采样率
pcm_audio = mp3_audio.set_channels(1).set_sample_width(2).set_frame_rate(44100)

# 导出为PCM文件
pcm_audio.export("/workspaces/ydnksqhd-Z_emotion.github.io/sound_track/file.pcm", format="s16le")