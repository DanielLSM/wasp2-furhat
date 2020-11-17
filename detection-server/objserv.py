import zmq
import numpy as np
import cv2
import time
import json

from recognizer import TranslatorProcessor, AVAILABLE_LANGUAGES, LANGUAGES_DICT, TRANSLATOR_DICT


class ObjectProcessor:
    def __init__(self, file_path='launch.json'):
        self.file_path = file_path
        self.config = self._load_config()
        #Load YOLO
        self.net, self.classes, self.layer_names, self.outputlayers, self.colors = self._load_net_properties(
        )

        self.capturer, self.outsocket = self._load_network_properties()

        # Detecting objects is resource intensive, so we try to avoid detecting objects in every frame
        self.detection_period = self.config["detection_period"]
        # Detection threshold takes a double between 0.0 and 1.0
        self.detection_threshold = self.config[
            "detection_confidence_threshold"]

        self.language = {'language': 'english'}
        self.translator = TranslatorProcessor()
        self.lang_socket = None

    def _load_network_properties(self):
        # Setup the sockets
        context = zmq.Context()

        ################## video socket
        video_socket = 'http://' + self.config["Furhat_IP"] + ':8080/video'
        capturer = cv2.VideoCapture(video_socket)

        # Output results using a PUB socket
        context2 = zmq.Context()
        outsocket = context2.socket(zmq.PUB)
        outsocket.bind("tcp://" + self.config["Dev_IP"] + ":" +
                       self.config["detection_exposure_port"])
        return capturer, outsocket

    def _load_net_properties(self):
        net = cv2.dnn.readNet("yolov3.weights", "yolov3.cfg")
        classes = []
        with open("coco.names", "r") as f:
            classes = [line.strip() for line in f.readlines()]

        layer_names = net.getLayerNames()
        outputlayers = [
            layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()
        ]

        colors = np.random.uniform(0, 255, size=(len(classes), 3))
        return net, classes, layer_names, outputlayers, colors

    def _load_config(self):
        # Load configuration
        with open(self.file_path) as f:
            config = json.load(f)
        print(config)
        return config

    def broadcast_objects(self):
        print('connected, entering broadcast')
        prevset = {}
        iterations = 0
        x = True
        while x:
            ret, img = self.capturer.read()

            if (iterations % self.detection_period == 0):
                # print("Detecting objects!")
                ret, img = self.capturer.read()
                height, width, channels = img.shape

                res = self.detect(img, height, width, channels,
                                  self.detection_threshold)
                img2 = self.draw(img, res)

                currset = self.getObjectSet(
                    self.objectList(res, height, width, channels))
                objdiff = self.compareSets(prevset, currset)

                if ((len(objdiff) > 1)
                        and ((iterations % self.detection_period * 500) == 0)):
                    print('hello')
                    msg_enter, msg_leave = self.translator.create_furhat_msg(
                        objdiff, dest=self.language['language'])
                    if msg_enter != '...':
                        self.outsocket.send_string(msg_enter.text)
                        self.lang_socket.send_string(msg_enter.dest)
                        print(msg_enter.text)
                        print(msg_enter.dest)

                    if msg_leave != '...':
                        self.outsocket.send_string(msg_leave.text)
                        self.lang_socket.send_string(msg_leave.dest)
                        print(msg_leave.text)
                        print(msg_leave.dest)

                        # print(self.language['language'])
                    # msg = ' '.join(objdiff)

                prevset = currset

                cv2.imshow("yolov3", img2)
            else:
                # print("Showing image!")
                img2 = self.draw(img, res)
                cv2.imshow("yolov3", img)

            iterations = iterations + 1

            k = cv2.waitKey(1)
            if k % 256 == 27:  # When pressing esc the program
                # ESC pressed
                print("Escape hit, closing...")
                break

    def detect(self, img, height, width, channels, confidence_threshold):
        #detecting objects
        blob = cv2.dnn.blobFromImage(img,
                                     0.00392, (416, 416), (0, 0, 0),
                                     True,
                                     crop=False)

        self.net.setInput(blob)
        outs = self.net.forward(self.outputlayers)

        # get confidence score of algorithm in detecting an object in blob
        class_ids = []
        confidences = []
        boxes = []
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > confidence_threshold:
                    #onject detected
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])  #put all rectangle areas
                    confidences.append(
                        float(confidence)
                    )  #how confidence was that object detected and show that percentage
                    class_ids.append(
                        class_id)  #name of the object tha was detected

        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.4, 0.6)
        return {'indexes': indexes, 'boxes': boxes, 'class_ids': class_ids}

    def draw(self, img, res):
        boxes = res['boxes']
        indexes = res['indexes']
        class_ids = res['class_ids']
        font = cv2.FONT_HERSHEY_PLAIN
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                color = self.colors[i]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label, (x, y + 30), font, 3, (255, 255, 0), 2)

        return img

    def formatresult(self, res, width, height):
        boxes = res['boxes']
        indexes = res['indexes']
        class_ids = res['class_ids']
        output = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                x /= width
                w /= width
                y /= height
                h /= height
                output.append({'item': label, 'bbox': [x, y, w, h]})
        return output

    def objectList(self, res, height, width, channels):
        boxes = res['boxes']
        indexes = res['indexes']
        class_ids = res['class_ids']
        output = []
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                x /= width
                w /= width
                y /= height
                h /= height
                output.append(label)
        return output

    def getObjectSet(self, list):
        set = {}
        for item in list:
            set[item] = True
        return set

    def compareSets(self, set1, set2):
        out = []
        for item in set2.keys():
            if not item in set1:
                out.append('enter_' + item)
        for item in set1.keys():
            if not item in set2:
                out.append('leave_' + item)
        return out


if __name__ == "__main__":
    op = ObjectProcessor()
    ###############
    print('connected, entering loop')
    op.broadcast_objects()
