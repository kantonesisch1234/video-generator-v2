import os
from moviepy.editor import *
from tools import *
import gtts
import shutil
import random
import math

tmp_dir = r'.\tmp'
output_dir = r'.\輸出'
media_source_dir = r'.\片源'
bgm_dir = r'.\音樂'
media_dir = r'.\logo'

subtitles_path = os.path.join(output_dir, 'subtitles.srt')
narration_path = os.path.join(output_dir, 'text.mp3')
subtitles_bar_path = os.path.join(media_dir, 'subtitles_bar.jpg')
logo_path = os.path.join(media_dir, 'logo.jpg')

new_para_interval = 1.5

#------------------------------------------------------------------------------------------
# Generating audios

def generate_audio_files(text, new_para_interval=new_para_interval, lang="zh-tw"):
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    if not os.path.isfile(narration_path) or not os.path.isfile(subtitles_path):
        
        processed_sentences = [sentence.strip("\n").strip(" ") for sentence in text]
        subtitles = []
        clips = []
        time_pt = 0

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        audio_filename = os.path.join(output_dir, "text.mp3")

        for idx, sentence in enumerate(processed_sentences):
            if len(sentence)!=0:
                tts=gtts.gTTS(sentence, lang=lang)
                filename=os.path.join(tmp_dir,"audio"+str(idx)+".mp3")
                tts.save(filename)
                audioclip = AudioFileClip(filename)
                clips.append(audioclip)
                duration = audioclip.duration
                time_range = [round(time_pt,3), round(time_pt+duration,3)]
                time_pt += duration
                subtitles.append((time_range, sentence))
            else:
                filename=os.path.join(tmp_dir,"audio"+str(idx)+".mp3")
                make_empty_audio(filename, duration=new_para_interval)
                audioclip = AudioFileClip(filename)
                clips.append(audioclip)
                time_range = [round(time_pt,3), round(time_pt+new_para_interval,3)]
                time_pt += new_para_interval
                subtitles.append((time_range, " "))
            if idx == len(processed_sentences)-1:
                filename=os.path.join(tmp_dir,"audio"+str(idx+1)+".mp3")
                make_empty_audio(filename, duration=new_para_interval)
                audioclip = AudioFileClip(filename)
                clips.append(audioclip)
                time_range = [round(time_pt,3), round(time_pt+new_para_interval,3)]
                time_pt += new_para_interval
                subtitles.append((time_range, " ")) 
                
        concat_clip = concatenate_audioclips(clips)
        concat_clip.write_audiofile(audio_filename)

        audiofile_no = len(processed_sentences)
        shutil.rmtree(tmp_dir)
        subtitles_to_file(subtitles,os.path.join(output_dir,'subtitles.srt'))
        
    else:
        subtitles = file_to_subtitles(os.path.join(output_dir, 'subtitles.srt'))
        print("subtitles.srt found and loaded.")

    return subtitles
    
# ---------------------------------------------------------------------------------
# Generating videos

def make_clip_from_directory(input_directory, output_directory, duration, shuffle=True, random_timeframe=True,
                             random_split_videos_into=0, size=(720,480), fps=30, height=None, width=None, 
                             subtitles_bar_size=None, logo_size=None, logo_opacity=1):
    img_files, video_files = get_img_video_files_list(input_directory)
    img_files_number = len(img_files)
    video_files_number = len(video_files)
    media_files_number = img_files_number + video_files_number
    
    if media_files_number == 0:
        raise Exception("You don't have media files in folder " + media_source_dir + ".")
#     if random_split_videos_into != 0 and not random_timeframe:
#         raise Exception("random_timeframe has to be true if you set random_split_videos_into to be non-zero.")
    
    if not random_split_videos_into:
        avg_duration = duration/media_files_number
    else:
        avg_duration = duration/(video_files_number*random_split_videos_into + img_files_number)
        
    img_clips = [ImageClip(image, duration=avg_duration).resize(size) for image in img_files]
    if height:
        uncut_video_clips = [VideoFileClip(video).resize(height=height).set_position("center") for video in video_files]
    elif width:
        uncut_video_clips = [VideoFileClip(video).resize(width=width).set_position("center") for video in video_files]
    else:
        uncut_video_clips = [VideoFileClip(video).resize(size) for video in video_files]
    if random_timeframe:
        video_durations = [clip.duration for clip in uncut_video_clips]
        if random_split_videos_into:
            random_durations = [tuple(gaussian_sampling_of_timepoints(random_split_videos_into,duration,avg_duration,10000)) for duration in video_durations]
            video_clips_ = [[clip.subclip(random_duration[i],random_duration[i]+avg_duration) for i in range(random_split_videos_into)] 
                           for clip,random_duration in zip(uncut_video_clips,random_durations)]
            video_clips = [item for sublist in video_clips_ for item in sublist]


        else:
            for idx, clip in enumerate(uncut_video_clips):
                if video_durations[idx] < avg_duration:
                    uncut_video_clips[idx] = concatenate_videoclips([uncut_video_clips[idx]] * int(math.ceil(video_durations[idx]/avg_duration)))
            random_durations = [random.uniform(0,duration-avg_duration) for duration in video_durations]
            video_clips = [clip.subclip(random_duration,random_duration+avg_duration) 
                           for clip,random_duration in zip(uncut_video_clips,random_durations)]
    else:
        if random_split_videos_into:
            video_durations = [clip.duration for clip in uncut_video_clips]
            random_durations = [tuple(sorted(gaussian_sampling_of_timepoints(random_split_videos_into,duration,avg_duration,10000))) for duration in video_durations]
            video_clips_ = [[clip.subclip(random_duration[i],random_duration[i]+avg_duration) for i in range(random_split_videos_into)] 
                           for clip,random_duration in zip(uncut_video_clips,random_durations)]
            video_clips = [item for sublist in video_clips_ for item in sublist]
        else:
            video_clips = [clip.subclip(0,avg_duration) for clip in uncut_video_clips]
        
    media_clips = img_clips + video_clips
    
    if shuffle:
        random.shuffle(media_clips)
        
    media_clips = [media_clip.set_start(idx*avg_duration) for idx,media_clip in enumerate(media_clips)]
    
    if subtitles_bar_size:
        subtitles_bar_clip = ImageClip(subtitles_bar_path).resize(subtitles_bar_size).set_pos(('center', 'bottom'))
        media_clips = media_clips + [subtitles_bar_clip]
        
    if logo_size:
        logo_clip = ImageClip(logo_path).resize(logo_size).set_pos(('right', 'top')).set_opacity(logo_opacity)
        media_clips = media_clips + [logo_clip]

    return CompositeVideoClip(media_clips)

# ---------------------------------------------------------------------------------------------------------------
# Insert audio and subtitles

def insert_audio_and_subtitles(input_clip,output_filename,audio_filename,subtitles,txt_color='white', 
                               fontsize=32, font='DFKai-SB', is_bgm=True, bgm_file='bgm.mp3', bgm_vol=1.0):
    def annotate(clip, txt, txt_color=txt_color, fontsize=fontsize, font=font):
        """ Writes a text at the bottom of the clip. """
        txtclip = TextClip(txt, fontsize=fontsize, font=font, color=txt_color)
        cvc = CompositeVideoClip([clip, txtclip.set_pos(('center', 'bottom'))])
        return cvc.set_duration(clip.duration)
    
    video = input_clip
    print("Input video loaded.")
    print("Annotating ...")
    annotated_clips = [annotate(video.subclip(from_t, to_t), txt) for (from_t, to_t), txt in subtitles]
    print("Concatenating videos ... ")
    final_clip = concatenate_videoclips(annotated_clips)
    # final_clip = CompositeVideoClip(
    print("Writing audio ...")
    narration = AudioFileClip(os.path.join(output_dir,audio_filename))
    duration = narration.duration
    if is_bgm:
        bgm = AudioFileClip(os.path.join(bgm_dir,bgm_file))
        if duration >= bgm.duration:
            bgm = concatenate_audioclips([bgm]*int(math.ceil(duration/bgm.duration)))
        bgm = bgm.set_duration(duration).volumex(bgm_vol)
        narration_with_bgm = CompositeAudioClip([narration,bgm])
        final_clip = final_clip.set_audio(narration_with_bgm)
    else:
        final_clip = final_clip.set_audio(narration)
    print("Writing output video ...")
    try:
        final_clip.write_videofile(os.path.join(output_dir,output_filename))
    except Exception as e:
        print("Some error occured!")