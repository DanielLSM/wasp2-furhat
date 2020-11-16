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

    def recognize_debug(self, audio):
        return self.r.recognize_google(audio)

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


import zmq
import numpy as np
import time
import json

# Load configuration
with open('launch.json') as f:
    config = json.load(f)
print(config)

# Setup the sockets
context = zmq.Context()

audio_socket = 'http://' + config["Audio_IP"] + ':8080/audio.wav'
SpeechProcessor(audio_socket=audio_socket)

# Output results using a PUB socket
context2 = zmq.Context()
outsocket = context2.socket(zmq.PUB)
outsocket.bind("tcp://" + config["Dev_IP"] + ":" + config["detection_audio"])

print('connected, entering loop')

x = True
while x:
    # for a in range(2):
    #     string = insocket.recv()
    # print('data:', len(string), 'bytes')
    ret, img = capturer.read()

    if (iterations % detection_period == 0):
        print("Detecting objects!")
        ret, img = capturer.read()
        # shape = array.shape
        # shared_array = np.Array(ctypes.c_uint8,
        #                         shape[0] * shape[1] * shape[2],
        #                         lock=False)
        # buf = np.frombuffer(buf, dtype=np.uint8)

        # print(array.shape)
        # buf = np.frombuffer(array, dtype=np.uint8)
        # print(buf)
        # img = cv2.imdecode(buf, flags=1)

        # height, width, channels = img.shape
        height, width, channels = img.shape

        res = detect(net, img, detection_threshold)
        img2 = draw(img, res)

        currset = getObjectSet(objectList(res))
        objdiff = compareSets(prevset, currset)

        if len(objdiff):
            msg = ' '.join(objdiff)
            outsocket.send_string(msg)

        prevset = currset

        cv2.imshow("yolov3", img2)
    else:
        print("Showing image!")
        # buf = np.frombuffer(string, dtype=np.uint8)
        # img = cv2.imdecode(buf, flags=1)
        img2 = draw(img, res)
        cv2.imshow("yolov3", img)

    iterations = iterations + 1

    k = cv2.waitKey(1)
    if k % 256 == 27:  # When pressing esc the program stops.
        # ESC pressed
        print("Escape hit, closing...")
        break

if __name__ == "__main__":

    sp = SpeechProcessor()
    sp.demo()