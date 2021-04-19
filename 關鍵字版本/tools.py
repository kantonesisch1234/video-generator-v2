import re, math, os
from moviepy.editor import *
from text_preprocessing import *
import imghdr
from scipy.stats import uniform, norm, dirichlet, skewnorm
import numpy as np

# ----------------------------------------------------------------------------
# Define default parameters for methods as global variables
default_empty_audio_duration = 3

default_color_clip_fps = 25
default_color_clip_rgb = (0,0,0)
default_color_clip_filename = 'color.mp4'

video_extensions_list = ['.mp4', '.avi', '.flv', '.rmvb']

default_clip_height = None
default_clip_width = None
default_clip_size = (720,480)
default_img_duration = 10

default_time_spread = 5
default_steps = 2000
default_decay_factor = 0.9
default_filter_factor = 1

skewnorm_para = 3.5

#---------------------------------------------------------------------------
# Add margins

def get_suitable_margin(width, height):
    if float(width/height) < 16./9.:
        margin = int((16*height-9*width)/18)
        return {'left': margin, 'right':margin, 'top':0, 'bottom':0}
    elif float(width/height) > 16./9.:
        margin = int((9*width-16*height)/32)
        return {'left': 0, 'right': 0, 'top': margin, 'bottom': margin}
    else:
        return {'left': 0, 'right': 0, 'top': 0, 'bottom': 0}
    
def add_margin_to_clip(clip):
    width, height = clip.size[0], clip.size[1]
    margin_dict = get_suitable_margin(width, height)
    left, right, top, bottom = margin_dict['left'], margin_dict['right'], margin_dict['top'], margin_dict['bottom']
    return clip.margin(left=left, right=right, top=top, bottom=bottom)






#-----------------------------------------------------------------------------
# General methods

def flatten(nested_list):
    return [item for sublist in nested_list for item in sublist]

def combine_to_dict(key_list, value_list):
    the_dict = dict()
    for key in key_list:
        the_dict[key]=[]
    for idx,value in enumerate(value_list):
        the_dict[key_list[idx]].append(value)
    return the_dict

#------------------------------------------------------------------------------
# Subtitles-handling related

def file_to_subtitles(filename):
    """ Converts a srt file into subtitles.

    The returned list is of the form ``[((ta,tb),'some text'),...]``
    and can be fed to SubtitlesClip.

    Only works for '.srt' format for the moment.
    """
    
    def is_string(obj):
        try:
            return isinstance(obj, basestring)
        except NameError:
            return isinstance(obj, str)
    
    def cvsecs(time):
        """ Will convert any time into seconds. 

        If the type of `time` is not valid, 
        it's returned as is. 

        Here are the accepted formats::

        >>> cvsecs(15.4)   # seconds 
        15.4 
        >>> cvsecs((1, 21.5))   # (min,sec) 
        81.5 
        >>> cvsecs((1, 1, 2))   # (hr, min, sec)  
        3662  
        >>> cvsecs('01:01:33.045') 
        3693.045
        >>> cvsecs('01:01:33,5')    # coma works too
        3693.5
        >>> cvsecs('1:33,5')    # only minutes and secs
        99.5
        >>> cvsecs('33.5')      # only secs
        33.5
        """
        factors = (1, 60, 3600)

        if is_string(time):     
            time = [float(f.replace(',', '.')) for f in time.split(':')]

        if not isinstance(time, (tuple, list)):
            return time

        return sum(mult * part for mult, part in zip(factors, reversed(time)))

    times_texts = []
    current_times = None
    current_text = ""
    with open(filename,'r', encoding='utf-8') as f:
        for line in f:
            times = re.findall("([0-9]*:[0-9]*:[0-9]*,[0-9]*)", line)
            if times:
                current_times = [cvsecs(t) for t in times]
            elif line.strip() == '':
                if current_times:
                    times_texts.append((current_times, current_text.strip('\n')))
                current_times, current_text = None, " "
            elif current_times:
                current_text += line

    return times_texts

def subtitles_to_file(subtitles, save_dir):
    """
    The reverse of the function file_to_subtitles. This function will write the subtitles into a srt file.
    """
    def sec_to_time(total_secs):
        hr = math.floor(total_secs/3600)
        min = math.floor(math.floor(total_secs-hr*3600)/60)
        sec = math.floor(total_secs % 60)
        remains = round(total_secs % 1 * 1000)

        if hr < 10:
            hr_str = '0'+str(hr)
        else:
            hr_str = str(hr)
        if min < 10:
            min_str = '0'+str(min)
        else:
            min_str = str(min)
        if sec < 10:
            sec_str = '0'+str(sec)
        else:
            sec_str = str(sec)
        if remains < 10:
            remains_str = '00'+str(remains)
        elif remains < 100:
            remains_str = '0'+str(remains)
        else:
            remains_str = str(remains)

        return hr_str+':'+min_str+':'+sec_str+','+remains_str  
    
    with open(save_dir, 'w', encoding='utf-8') as f:
        for idx, subtitle in enumerate(subtitles):
            f.write(str(idx+1)+'\n')
            f.write(sec_to_time(subtitle[0][0])+' --> '+sec_to_time(subtitle[0][1])+'\n')
            f.write(subtitle[1])
            f.write('\n\n')
# ----------------------------------------------------------------------------------------------
# Audio, video handling related

def make_empty_audio(filename, duration=default_empty_audio_duration):
    make_frame = lambda t: 2*[ 0*t ]
    clip = AudioClip(make_frame, duration=duration, fps=44100)
    clip.write_audiofile(filename)
    
def color_clip(size, duration, fps=default_color_clip_fps, color=default_color_clip_rgb, output=default_color_clip_filename):
    ColorClip(size, color, duration=duration).write_videofile(os.path.join(output_dir,output), fps=fps)
    
def get_img_video_files_list(directory):
    img_files = []
    video_files = []
    video_extensions = ['.mp4', '.avi', '.flv', '.rmvb']
    for file in os.listdir(directory):
        file_path = os.path.join(directory,file)
        if os.path.isfile(file_path):
            if imghdr.what(file_path):
                img_files.append(file_path)
            for ext in video_extensions:
                if file_path.endswith(ext):
                    video_files.append(file_path)
    return img_files, video_files

def is_img(filepath):
    if imghdr.what(filepath):
        return True
    else:
        return False

def is_video(filepath):
    video_extensions = video_extensions_list
    for ext in video_extensions:
        if filepath.endswith(ext):
            return True
    else:
        return False

# -----------------------------------------------------------------------------------------
# Video-editing related
def to_clip(filepath, height=default_clip_height, width=default_clip_width, size=default_clip_size, img_duration=default_img_duration):
    if is_img(filepath):
        image=filepath
        if height:
            return ImageClip(image, duration=img_duration).resize(height=height)
        elif width:
            return ImageClip(image, duration=img_duration).resize(width=width)
        else:
            return ImageClip(image, duration=img_duration).resize(size)
    elif is_video(filepath):
        video=filepath
        if height:
            return VideoFileClip(video).resize(height=height).set_position("center")
        elif width:
            return VideoFileClip(video).resize(width=width).set_position("center")
        else:
            return add_margin_to_clip(VideoFileClip(video)).resize(size).set_position("center")
    else:
        raise Exception("The file is neither video nor image, something is wrong with the code!")
        
def random_split_video(list_of_clips, avg_duration, random_split_videos_into, is_sorted=True):
        video_durations = [clip.duration for clip in list_of_clips]
        if is_sorted:
            random_durations = [tuple(sorted(gaussian_sampling_of_timepoints(random_split_videos_into,duration,avg_duration,10000))) for duration in video_durations]
        else:
            random_durations = [tuple(gaussian_sampling_of_timepoints(random_split_videos_into,duration,avg_duration,10000)) for duration in video_durations]
        video_clips_ = [[clip.subclip(random_duration[i],random_duration[i]+avg_duration) for i in range(random_split_videos_into)] 
                       for clip,random_duration in zip(uncut_video_clips,random_durations)]
        video_clips = [item for sublist in video_clips_ for item in sublist]
        
        return video_clips
    
    
# -----------------------------------------------------------------------------------------
# Keywords-handling related
def is_keyword(keyword, subtitles):
    for subtitle in subtitles:
        sentence_no_new_line = re.sub('\n', '', subtitle[1])
        if re.search(keyword, sentence_no_new_line):
            return True
    return False

def get_non_keywords_paths(keyword_file_dict, media_source_dir):
    img_files, video_files = get_img_video_files_list(media_source_dir)
    media_files = img_files + video_files
    keyword_media_files = [item for sublist in list(keyword_file_dict.values()) for item in sublist]
    media_files_set = set(media_files)
    keyword_media_files_set = set(keyword_media_files)
    return list(media_files_set.difference(keyword_media_files_set))

def get_keywords_to_file_dict(media_source_dir, subtitles):
    def get_file_basename(filepath):
        base = os.path.basename(filepath)
        return os.path.splitext(base)
    
    img_files, video_files = get_img_video_files_list(media_source_dir)
    media_files = img_files + video_files
    media_file_names = [get_file_basename(filepath)[0] for filepath in media_files]
    the_dict = combine_to_dict(media_file_names, media_files)
    not_keywords = []
    for key in the_dict.keys():
        if not is_keyword(key, subtitles):
            not_keywords.append(key)
    for not_keyword in not_keywords:
        del the_dict[not_keyword]
    return the_dict

def keyword_to_clip_dict(keyword_file_dict, img_duration=default_img_duration, height=default_clip_height, width=default_clip_width, size=default_clip_size):
    
    return {key:[to_clip(path,img_duration=img_duration, height=height, width=width, size=size) for path in path_list] for (key,path_list) in keyword_file_dict.items()}

def keyword_timepoints(keyword, subtitles):
    # Returns the time points at which a keyword appears in subtitles
    def keyword_matches_indices(keyword, text):
        keyword_iter = re.finditer(keyword, text)
        indices = [m.start(0) for m in keyword_iter]
        return indices
    matches = []
    for subtitle in subtitles:
        subtitle_match = keyword_matches_indices(keyword, subtitle[1])
        for match in subtitle_match:
            matches.append((subtitle[0],len(subtitle[1]),match))
    time_points = []
    for match in matches:
        start_time, end_time = match[0][0], match[0][1]
        duration = end_time-start_time
        time_points.append(round(start_time+duration*match[2]/match[1],3))
    return time_points

def keyword_prob_dict(keywords_list, subtitles, time_spread=default_time_spread, steps=default_steps, 
                      decay_factor=default_decay_factor, filter_factor=default_filter_factor):
    """
    Return a dictionary of probabilities for each word. steps is the number of time points in the time array (discretization of 
    the video time range). decay_factor is the decay factor for peak of Gaussian function for each time a word appears.
    time_spread is the factor of width of the Gaussian distribution. filter_factor is to filter out the time points at which actually no keywords are being mentioned.
    It is done by adding a uniform distribution in the entire video time range (filter factor * uniform distribution.) 
    """
    def keyword_prob(keyword, subtitles, time_spread=time_spread, steps=steps, decay_factor=decay_factor,
                    filter_factor=filter_factor):
        T = subtitles[-1][0][1]
        t_arr = np.linspace(0,T,steps)
        timepoints = keyword_timepoints(keyword, subtitles)

        keyword_prob = np.zeros(steps)
        for idx,timepoint in enumerate(timepoints):
            keyword_prob += decay_factor**idx*skewnorm.pdf(t_arr,skewnorm_para,timepoint,time_spread)
            # keyword_prob += decay_factor**idx*norm.pdf(t_arr,timepoint,time_spread)

        return keyword_prob

    prob_list = []
    full_keywords_list = keywords_list + ['Random footage']
    
    T = subtitles[-1][0][1]
    t_arr = np.linspace(0,T,steps)
    
    prob_random_footage = filter_factor * uniform.pdf(t_arr,0,T)
    
    for keyword in keywords_list:
        prob_list.append(keyword_prob(keyword, subtitles, time_spread=time_spread, steps=steps, decay_factor=decay_factor))
    prob_list.append(prob_random_footage)
    return dict(zip(full_keywords_list, prob_list))

def prob_dist_at_timepoint(keywords_list, subtitles, t_arr, timepoint, time_spread=default_time_spread,
                          steps=default_steps, decay_factor=default_decay_factor, filter_factor=default_filter_factor):
    prob_dict = keyword_prob_dict(keywords_list, subtitles, time_spread=time_spread, steps=steps, decay_factor=decay_factor, filter_factor=filter_factor)
    T,steps = t_arr[-1],t_arr.size
    idx = max(0,min(round(timepoint/T*steps),steps-1))
    prob_list = []
    full_keywords_list = keywords_list + ["Random footage"]
    for keyword in prob_dict:
        timepoint = t_arr[idx]
        prob_arr = prob_dict[keyword]/sum(prob_dict.values())
        prob = prob_arr[idx]
        prob_list.append(prob)
    return dict(zip(full_keywords_list, prob_list))

def get_clip_times(keywords_list, subtitles, t_arr, time_spread=default_time_spread, steps=default_steps, decay_factor=default_decay_factor, filter_factor=default_filter_factor):
    clip_name_list = []
    first_dict = prob_dist_at_timepoint(keywords_list, subtitles, t_arr, 0, time_spread=time_spread, steps=steps, decay_factor=decay_factor, filter_factor=filter_factor)
    tmp_keyword = max(first_dict, key=first_dict.get)
    t1 = 0
    for t_pt in t_arr:
        test = prob_dist_at_timepoint(keywords_list, subtitles, t_arr, t_pt, time_spread=time_spread, steps=steps, decay_factor=decay_factor, filter_factor=filter_factor)
        keyword = max(test, key=test.get)
        if keyword != tmp_keyword:
            t2 = t_pt
            clip_name_list.append(([t1,t2], tmp_keyword))
            tmp_keyword = keyword
            t1 = t2
    T = subtitles[-1][0][1]
    if "t2" not in locals():
        t2 = t1
    clip_name_list.append(([t2,T], keyword))
    return clip_name_list

#-----------------------------------------------------------------------------------------------------------------------
    
def gaussian_sampling_of_timepoints(clips_number, video_duration, clip_length, steps):
    
    """
    This function is to sample the starting timepoints from the same video for cutting clip in the way that the cut clips overlap as little     as possible
    """

    def gaussian_peak(scale):
        return (2*np.pi*scale**2)**(-0.5)

    def redistribute(dist,t_arr,scale):
        dist = dist/sum(dist)
        loc = np.random.choice(t_arr,p=dist)
        gaussian_mask = norm.pdf(t_arr,loc,scale)
        dist = dist*(1-0.95*gaussian_mask/gaussian_peak(scale))
        return loc,dist

    t_arr = np.linspace(0,video_duration-clip_length,steps)

    dist = uniform.pdf(t_arr,t_arr[0],t_arr[-1])
    dist = dist/sum(dist)

    timepoints_list = []

    for i in range(clips_number):
        timepoint,dist = redistribute(dist,t_arr,clip_length)
        dist[dist<0]=0
        dist = dist/sum(dist)
        timepoints_list.append(timepoint)
    
    return timepoints_list



    
    
    
    
    
