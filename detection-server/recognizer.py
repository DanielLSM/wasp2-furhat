import vlc
import zmq
import time
import json
import numpy as np
import speech_recognition as sr
from urllib.request import urlopen

from googletrans import Translator, constants

AVAILABLE_LANGUAGES = ["en", "fr", "sw", "sp", "it", "po"]
LANGUAGES_DICT = {
    "en": "english",
    "fr": "french",
    "sw": "swedish",
    "it": "italian",
    "sp": "spanish",
    "po": "portuguese"
}
TRANSLATOR_DICT = {
    "en": "en",
    "fr": "fr",
    "sw": "swe",
    "it": "it",
    "sp": "es",
    "po": "pt"
}


class TranslatorProcessor:
    def __init__(self):
        self.translator = Translator()

    def translate_sentence(self, sentence, dest='en'):
        try:
            translation = self.translator.translate(sentence, dest, src='en')
        except:
            translation = "..."
        return translation

    def process_objects(self, objects, transition):
        process_objects = objects
        for _ in range(len(objects)):
            if transition == 'enter':
                process_objects[_] = objects[_].replace("enter_", "")
            else:
                process_objects[_] = objects[_].replace("leave_", "")
        assert len(process_objects) == len(objects)
        return process_objects

    def create_furhat_msg(self, translate_objects, dest='en'):
        transition = 'enter' if translate_objects[0][0:2] == 'en' else 'leave'

        objs = self.process_objects(translate_objects, transition)
        print(objs)

        if transition == 'enter':
            if len(objs) > 1:
                msg = "You showed me multiple objects. "
                for _ in objs:
                    msg = msg + " and " + str(_)
            else:
                msg = "Oh nice, that is a {}".format(objs)
        else:
            if len(objs) > 1:
                msg = "You removed multiple objects. "
                for _ in objs:
                    msg = msg + " and " + str(_)
            else:
                msg = "No, don't remove that, I love the {}".format(objs)

        if dest != 'en':
            translated_msg = self.translate_sentence(msg, dest)

        return translated_msg


class SpeechProcessor:
    def __init__(self, file_path='launch.json'):
        self.file_path = file_path
        self.config = self._load_config()
        #Load YOLO
        self.r, self.outsocket = self._load_network_properties()
        self.language = {'language': 'english'}

    def _load_network_properties(self):
        self.audio_socket = 'http://' + self.config[
            "Audio_IP"] + ':8080/audio.wav'
        recognizer = sr.Recognizer()

        # Output results using a PUB socket
        context = zmq.Context()
        outsocket = context.socket(zmq.PUB)
        outsocket.bind("tcp://" + self.config["Dev_IP"] + ":" +
                       self.config["detection_audio"])

        return recognizer, outsocket

    def _load_config(self):
        # Load configuration
        with open(self.file_path) as f:
            config = json.load(f)
        print(config)
        return config

    def broadcast_speech(self):
        while True:
            audio = self.get_audio()
            recognized_str = str(self.recognize(audio))
            if recognized_str != None and recognized_str[0:2].lower(
            ) in AVAILABLE_LANGUAGES:
                self.language['language'] = LANGUAGES_DICT[
                    recognized_str[0:2].lower()]

    def update_language(self):
        while True:
            self.outsocket.send_string(self.language['language'])

    def get_audio(self):
        with sr.WavFile(urlopen(self.audio_socket)) as source:
            print("Say something!")
            # self.r.adjust_for_ambient_noise(source, duration=1)
            audio = self.r.listen(source, phrase_time_limit=1)
        return audio

    def recognize(self, audio):
        word = None
        try:
            word = self.r.recognize_google(audio)
        except sr.UnknownValueError:
            pass
            # print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}"
                .format(e))
        return word

    # THIS SNIPPET IS FROM HERE: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
    # recognize speech using Google Speech Recognition
    def recognize_debug(self, audio):
        try:
            # for testing purposes, we're just using the default API key
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            # instead of `r.recognize_google(audio)`
            print("Google Speech Recognition thinks you said " +
                  self.r.recognize_google(audio))
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(
                "Could not request results from Google Speech Recognition service; {0}"
                .format(e))

    # THIS SNIPPET IS FROM HERE: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py

    def playback(self):
        p = vlc.MediaPlayer(self.audio_socket)
        print("hello")
        p.play()

    def demo(self):
        while True:
            audio = self.get_audio()
            self.recognize_debug(audio)


if __name__ == "__main__":

    # sp = SpeechProcessor()
    # # sp.demo()
    # sp.broadcast_speech()

    tr = TranslatorProcessor()
    # message = tr.translate_sentence("Hola Mundo")

    objects = ['enter_tvmonitor', 'enter_bottle', 'enter_cup']

    message = tr.create_furhat_msg(objects, dest="es")
    if message != '...':
        print(message.text)