import vlc
import speech_recognition as sr
from urllib.request import urlopen


class SpeechProcessor:
    def __init__(self, audio_socket='http://130.229.143.90:8080/audio.wav'):
        self.audio_socket = audio_socket
        self.r = sr.Recognizer()

    def get_audio(self):
        with sr.WavFile(urlopen(self.audio_socket)) as source:
            print("Say something!")
            # self.r.adjust_for_ambient_noise(source, duration=1)
            audio = self.r.listen(source, phrase_time_limit=1)
        return audio

    # THIS SNIPPET IS FROM HERE: https://github.com/Uberi/speech_recognition/blob/master/examples/microphone_recognition.py
    # recognize speech using Google Speech Recognition
    def recognize(self, audio):
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
            self.recognize(audio)


if __name__ == "__main__":

    sp = SpeechProcessor()
    sp.demo()