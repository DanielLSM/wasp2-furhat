from objserv import ObjectProcessor
from recognizer import SpeechProcessor

import cv2
from threading import Thread


class DetectionServer:
    def __init__(self, file_path='launch.json'):
        self.object_processor = ObjectProcessor(file_path=file_path)
        self.speech_processor = SpeechProcessor(file_path=file_path)
        self.obj_broadcast = Thread(
            target=self.object_processor.broadcast_objects)
        self.speech_broadcast = Thread(
            target=self.speech_processor.broadcast_speech)
        # self.update_lang = Thread(target=self.speech_processor.update_language)

    def start_broadcast(self):
        self.object_processor.language = self.speech_processor.language  #passed by reference :)
        self.object_processor.lang_socket = self.speech_processor.outsocket
        self.speech_broadcast.start()
        self.obj_broadcast.start()
        # self.update_lang.start()

    def finish_broadcast(self):
        self.obj_broadcast.join()
        self.speech_broadcast.join()
        # self.update_lang.join()


if __name__ == "__main__":
    server = DetectionServer()
    server.start_broadcast()
    server.finish_broadcast()
    ###############
