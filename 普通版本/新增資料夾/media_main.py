from text_preprocessing import *
from make_media import *
from math import ceil, floor

narration_lang = "zh-tw"

# video_size = (854,480)
# video_size = (1280,720)
video_size = (1920,1080)
shuffle = False
random_timeframe = False
random_split_videos_into = 4

subtitles_font_size = 72
subtitles_font = 'DFKai-SB'
# subtitles_font = 'HanWangYenHeavy'
subtitles_bar_thickness = 2
words_per_line = 23

subtitles_bar_size = (2000,ceil(subtitles_font_size*4/3)*subtitles_bar_thickness)
# subtitles_bar_size = None
logo_size = (200,200)
logo_opacity = 0.3

is_bgm = True
bgm_vol = 0.25
bgm_file = 'bgm.mp3'

if __name__ == '__main__':
    sentences = get_subtitles_from_textfile('text.txt', lang=narration_lang, words_per_line=words_per_line)
    subtitles = generate_audio_files(sentences, lang=narration_lang)
    narration = AudioFileClip(os.path.join(output_dir,'text.mp3'))
    duration = narration.duration
    input_clip = make_clip_from_directory(media_source_dir, output_dir,duration,size=video_size,subtitles_bar_size=subtitles_bar_size, shuffle=shuffle, random_timeframe=random_timeframe, random_split_videos_into=random_split_videos_into, logo_size=logo_size, logo_opacity=logo_opacity)
    insert_audio_and_subtitles(input_clip,'output.mp4','text.mp3',subtitles,fontsize=subtitles_font_size,
    font=subtitles_font, is_bgm=is_bgm, bgm_vol=bgm_vol, bgm_file=bgm_file)

