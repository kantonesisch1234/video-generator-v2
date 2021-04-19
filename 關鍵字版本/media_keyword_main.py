from text_preprocessing import *
from make_media import *
from math import ceil, floor

narration_lang = "zh-tw"

height = None
width = None
video_size = (426, 240)
is_sorted = False
avg_duration = 15
img_duration = 10

time_spread = 5
decay_factor = 0.75
filter_factor = 0.6

subtitles_font_size = 64*video_size[1]/1080
subtitles_font = 'DFKai-SB'
subtitles_bar_thickness = 2
words_per_line = 20

subtitles_bar_size = (1000,ceil(subtitles_font_size*4/3)*subtitles_bar_thickness)
logo_size = (200*video_size[1]/1080, 200*video_size[1]/1080)
logo_opacity = 0.3

is_bgm = True
bgm_vol = 0.15
bgm_file = 'bgm.mp3'

if __name__ == '__main__':
    sentences = get_subtitles_from_textfile('text.txt', lang=narration_lang, words_per_line=words_per_line)
    subtitles = generate_audio_files(sentences, lang=narration_lang)
    narration = AudioFileClip(os.path.join(output_dir,'text.mp3'))
    input_clip = make_clip_by_keyword(subtitles, media_source_dir, output_dir, img_duration=img_duration, steps=2000,
                         time_spread=time_spread, decay_factor=decay_factor, filter_factor=filter_factor, size=video_size, 
                         height=height, width=width,fps=30, is_sorted = is_sorted, avg_duration=avg_duration, 
                         duration_uniformity = 100, gaussian_steps = 10000,  
                         subtitles_bar_size=subtitles_bar_size, logo_size=logo_size, logo_opacity=logo_opacity)
    insert_audio_and_subtitles(input_clip,'output.mp4','text.mp3',subtitles,fontsize=subtitles_font_size,
    font=subtitles_font, is_bgm=is_bgm, bgm_vol=bgm_vol, bgm_file=bgm_file)

