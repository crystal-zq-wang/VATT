import io
import os
import cv2
import moviepy
import crepe
import numpy
import csv

from google.cloud import translate_v2, speech_v1, texttospeech
from moviepy.editor import *
from scipy.io import wavfile


class VideoTranslator:

    def __init__(self):

        #BEGIN TRANSLATION SETUP
        self.translate_client = translate_v2.Client()
        #END TRANSLATION SETUP

        #BEGIN GENERAL SETUP
        self.languages = {}
        for lng in self.translate_client.get_languages():
            self.languages[lng['name'].lower()] = lng['language']
        #END GENERAL SETUP

        #BEGIN AUDIO-TEXT SETUP
        self.audio_text_client = speech_v1.SpeechClient()
        self.audio_channel_count = 2
        self.enable_separate_recognition_per_channel = True
        #END AUDIO-TEXT SETUP

        #START TEXT-AUDIO SETUP
        self.text_audio_client = texttospeech.TextToSpeechClient()
        #END TEXT-AUDIO SETUP

    def translate(self, text, lng="english"):
        translation = self.translate_client.translate(text,
            target_language=self.languages[lng.lower()])
        return self.edit_transcript(translation['translatedText'])
        
    def get_audio(self, local_file_path):
        with io.open(local_file_path, "rb") as f:
            content = f.read()
        return content


    def translate_video(self, url, native_lng, lng="english"):
        #video, audio = self.retrieve_video_and_audio(url)
        audio = {"content": self.get_audio(url)}
        
        full_transcript = self.split_transcript(self.get_transcript(audio, native_lng))
        translated_transcript = []
        for line in full_transcript:
            translated_transcript.append(self.translate(line, lng))

        translated_audio = None 
        for i in range(len(full_transcript)):
            native_line = full_transcript[i]
            translated_line = translated_transcript[i]
            speed_factor = self.get_speed_factor(native_line, translated_line)
            if not translated_audio:
                translated_audio = self.text_to_audio(translated_line, lng, speed_factor=speed_factor)
            else:
                translated_audio = translated_audio + self.text_to_audio(translated_line, lng, speed_factor=speed_factor)


        with open("output.mp3", "wb") as out:
            out.write(translated_audio)

        audio_background = AudioFileClip("output.mp3")
        final_audio = CompositeAudioClip([audio_background])
        final_clip = videoclip.set_audio(audio_background)
        final_clip.write_videofile("result.mp4")

        # clip = VideoFileClip("result.mp4")
        # clip_resized = clip.resize(h, w)
        # clip_resized.write_videofile("result.mp4")

        # final_final_clip= moviepy.video.fx.all.resize(VideoFileClip("result.mp4"), newsize=(h, w))
        # final_final_clip.write_videofile("result.mp4")
        # final_clip.f1(moviepy.video.fx.all.resize)
        # final_clip.write_videofile("result_final.mp4")

        # new_clip = videoclip.set_audio(AudioFileClip("output.mp3"))
        # videoclip.write_videofile("output.mp4")

        #videoclip.write_videofile("output.mp4", audio="trying.mp3")
        #return self.splice_video_and_audio(video, translated_audio)

    def edit_transcript(self, transcript):
        return transcript.replace("&#39;", "'")

    def split_transcript(self, transcript):
        return transcript.split(' ')

    def get_transcript(self, audio, native_lng): #CRYSTAL HAS THIS CODE
        config = {
            "audio_channel_count": self.audio_channel_count,
            "enable_separate_recognition_per_channel": self.enable_separate_recognition_per_channel,
            "language_code": self.languages[native_lng],
        }
        response = self.audio_text_client.recognize(config, audio)
        for result in response.results:
            alternative = result.alternatives[0]

        return format(alternative.transcript)

    def get_speed_factor(self, native_line, translated_line): #CAN EDIT THIS LATER, FUNCTIONAL FOR NOW
        return len(translated_line)/len(native_line)

    def determine_gender(self, frequency):
        return frequency > 170 and "female" or "male"

    def text_to_audio(self, text, lng, speed_factor=1, gender=None): #CRYSTAL IS WORKING ON THIS CODE
        
         # gender = self.determine_gender(frequency)

        if gender == "female":
            ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE
        elif gender == "male":
            ssml_gender=texttospeech.enums.SsmlVoiceGender.MALE
        else:
            ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL

        synthesis_input = texttospeech.types.SynthesisInput(text=text)
        voice = texttospeech.types.VoiceSelectionParams(language_code=self.languages[lng], ssml_gender=ssml_gender)
        audio_config = texttospeech.types.AudioConfig(audio_encoding=texttospeech.enums.AudioEncoding.MP3)
        response = self.text_audio_client.synthesize_speech(synthesis_input, voice, audio_config)
        return response.audio_content


# Takes in the name of the input file, which is a .mov file
s = input("Specify Filename: ")

# Getting the dimensions of the original video
vid = cv2.VideoCapture(s)
h = int(vid.get(cv2.CAP_PROP_FRAME_HEIGHT))
w = int(vid.get(cv2.CAP_PROP_FRAME_WIDTH))

# Making an audiofile out of the the video file, named "trying.wav"
videoclip = VideoFileClip(s)
audioclip = videoclip.audio
audioclip.write_audiofile("trying.wav", verbose=True)

# taking inputs of native language and changin language
s1 = str(input("Input Language: ")).strip()
s2 = str(input("Output Language: ")).strip()

#finsing average frequency of the input audio

lst = list()
filename = "trying"
os.system("crepe trying.wav --step-size 100")

with open ('trying.f0.csv',newline='') as csvfile:
    data = csv.reader(csvfile, delimiter=',')
    for row in data:
        lst.append(row[1])

lst = lst[1:]
lst = [float(s) for s in lst]

lst.sort()

length = len(lst)

DELTA = 0.1
assert DELTA < 0.5, "not gonna work bro"

lst = lst[int(length*DELTA):-int(length*DELTA)]
frequency = sum(lst) / len(lst)
print(frequency)

"""
if s2=="random":
    vt.languages.random
"""

vt = VideoTranslator()

vt.translate_video("trying.wav", s1, s2)

os.remove("trying.wav")
