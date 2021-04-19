from text_preprocessing import get_subtitles_from_textfile
from pydub import AudioSegment, silence
import numpy as np
import math
from moviepy.editor import AudioFileClip

textfile = 'text.txt'
audiofile = 'text.mp3'

silence_thres = 300

words_per_line = 23

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

def get_number_of_silences(textfile):
	sentences = get_subtitles_from_textfile(textfile, lang="zh-tw", words_per_line=words_per_line, max_lines=0)
	short_silences = len(sentences)-1
	long_silences = 0
	for sentence in sentences:
		if sentence == '\n':
			long_silences += 1
			short_silences -= 2
	print(long_silences, short_silences)
	
def get_nonsilent(audiofile, silence_thres):
	myaudio = intro = AudioSegment.from_mp3(audiofile)
	dBFS=myaudio.dBFS
	nonsilent = silence.detect_nonsilent(myaudio, min_silence_len=silence_thres, silence_thresh=dBFS-16, seek_step=5)
	nonsilent = [((start/1000),(stop/1000)) for start,stop in nonsilent] #in sec
	return nonsilent

def combine_tuples(list_of_tuples):
	return (list_of_tuples[0][0], list_of_tuples[-1][1])

def nonsilent_to_subtitles(textfile, audiofile, silence_thres):
	nonsilent = get_nonsilent(audiofile, silence_thres)
	sentences = get_subtitles_from_textfile(textfile, lang="zh-tw", words_per_line=words_per_line, max_lines=0)
	sentences = [sentence for sentence in sentences if sentence != '\n']
	
	new_nonsilent = []
	idx2 = 0
	for sentence in sentences:
		if '、' in sentence:
			old_idx2 = idx2
			idx2 += sentence.count('、')+1
			new_nonsilent.append(combine_tuples(nonsilent[old_idx2:idx2]))
			continue
		else:
			new_nonsilent.append(nonsilent[idx2])
			idx2 += 1

	subtitles = []
	for idx, sentence in enumerate(sentences):
		subtitles.append((list(new_nonsilent[idx]), sentence))
	return subtitles
			
def fill_blanks_to_subtitles(audiofile, subtitles, char = ' '):
	audio_length = AudioFileClip(audiofile).duration
	new_subtitles = [([0.000,subtitles[0][0][0]],char)]
	sub_len = len(subtitles)
	for idx, subtitle in enumerate(subtitles):
		new_subtitles.append(subtitles[idx])
		if idx != sub_len-1:
			new_subtitles.append(([subtitles[idx][0][1],subtitles[idx+1][0][0]], char))
	new_subtitles.append(([subtitles[-1][0][1],audio_length], char))
	return new_subtitles
			
			


subtitles = nonsilent_to_subtitles(textfile, audiofile, silence_thres)
new_subtitles = fill_blanks_to_subtitles(audiofile, subtitles, char=' ')
print(new_subtitles)
subtitles_to_file(new_subtitles, 'a.srt')


