from google.cloud import translate_v2, speech_v1, texttospeech
import io
from moviepy.editor import *

class Video_Translator:

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

        with open('output.mp3', 'wb') as out:
            out.write(translated_audio)
        #return self.splice_video_and_audio(video, translated_audio)

    def edit_transcript(self, transcript):
        return transcript.replace("&#39;", "'")

    def split_transcript(self, transcript):
        return transcript.split(' ')


    def retrieve_video_and_audio(self, url): #ARUSHI HAS THIS CODE
        return None

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

    def text_to_audio(self, text, lng, speed_factor=1, gender=None): #CRYSTAL IS WORKING ON THIS CODE
        
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
            # Write the response to the output file.
        #    out.write(response.audio_content)
        #    print('Audio content written to file "output.mp3"')


    def splice_video_and_audio(self, video, audio): # I SUPPOSE I(ANTON) WILL WORK ON THIS NOW
        return None

s = input("Specify Filename: ")

videoclip = VideoFileClip(s)
audioclip = videoclip.audio
audioclip.write_audiofile("trying.wav", verbose=True)

s1 = str(input("Input Language: "))
s2 = str(input("Output Language: "))

vt = Video_Translator()
vt.translate_video("trying.wav", s1, s2)
