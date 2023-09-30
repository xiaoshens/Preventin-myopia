import cv2
from cvzone.PoseModule import PoseDetector
import time
import math
import dis_a
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import win32api, win32con
import a333
# import mask
def get_img_from_camera_local():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    while True:
        ret, frame = cap.read()
        # 显示文字
        cv2.putText(frame, "Please adjust the standard sitting ", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1,
               (0, 0, 255), 2)
        cv2.putText(frame, "posture and press q. ", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1,
               (0, 0, 255), 2)
        cv2.imshow("capture",  frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.imwrite('image/' + 'biaozhun' + '.jpg', frame)# 存储为图像
            break
    cap.release()
    cv2.destroyAllWindows()


def cv2_chinese_text(img, text, position, textColor=(0, 255, 0), textSize=30):
    if (isinstance(img, np.ndarray)):  # 判断是否OpenCV图片类型
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    # 创建一个可以在给定图像上绘图的对象
    draw = ImageDraw.Draw(img)
    # 字体的格式
    fontStyle = ImageFont.truetype("font/simsun.ttc", textSize, encoding="utf-8")
    # 绘制文本
    draw.text(position, text, textColor, font=fontStyle)
    # 转换回OpenCV格式
    return cv2.cvtColor(np.asarray(img), cv2.COLOR_RGB2BGR)

class poseDetector():

    def __init__(self):
        self.detect = PoseDetector()
        self.degree = 0
        self.real_height = 0

    # 找出点
    def findPose(self, img, draw=True):
        # imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = self.detect.findPose(img)
        self.lmList, bboxInfo = self.detect.findPosition(img, bboxWithHands=False, draw=False)
        # print(self.lmList)
        if bboxInfo:
            center = bboxInfo["center"]
            # cv2.circle(img, center, 5, (255, 0, 255), cv2.FILLED)
        return img

    def draw_angle(self, img, draw=True):
        if draw:
            # cv2.putText(img, f':倾斜了{90-round(self.degree)}度', (100, 100),cv2.FONT_HERSHEY_PLAIN, 3,
            # (255, 0, 0), 3)
            img = cv2_chinese_text(img, f':脖子倾斜了{round(self.degree)}度', (100 + 5, 100 - 30))
        return img

    def angle(self, img, thera, top, nos):
        distance = math.sqrt((top[0] - nos[0]) * (top[0] - nos[0]) + (top[1] - nos[1]) * (top[1] - nos[1]))
        cos = math.fabs(top[1] - nos[1]) / distance
        degree = 0
        if distance != math.fabs(top[1] - nos[1]):
            degree = math.acos(cos)
            degree = math.degrees(degree)
            self.degree = degree
            # print(degree)
        if degree > thera:
            print("头歪了！")

    def shoulder_gd(self, thera, img):
        shoulder_l = [self.lmList[12][1], self.lmList[12][2]]
        shoulder_r = [self.lmList[11][1], self.lmList[11][2]]
        distance = math.sqrt((shoulder_l[0] - shoulder_r[0]) * (shoulder_l[0] - shoulder_r[0]) + (shoulder_l[1] - shoulder_r[1]) * (shoulder_l[1] - shoulder_r[1]))
        cos = math.fabs(shoulder_l[0] - shoulder_r[0]) / distance
        degree = 0
        if distance != math.fabs(shoulder_l[0] - shoulder_r[0]):
            degree = math.acos(cos)
            degree = math.degrees(degree)
            self.degree = degree
            # print(degree)
        img = cv2_chinese_text(img, f':肩膀倾斜了{round(self.degree)}度', (350 + 5, 360), (120,132,21), 20)
        if degree > thera:
            print("斜肩了！")
        return img

    def find_dis_ls(self, img, jaw, d, w, read=True):
        shoulder_l = [self.lmList[12][1], self.lmList[12][2]]
        shoulder_r = [self.lmList[11][1], self.lmList[11][2]]
        mid = [(shoulder_r[i] + shoulder_l[i]) / 2 for i in range(2)]
        distance = math.fabs(jaw[1] - mid[1])
        # print(distance)
        height = 6.3*distance/w
        if not read:self.real_height=height
        if height < self.real_height-1:
            print("驼背了！")
            print(height)
            img = cv2_chinese_text(img, '你驼背了哟！！', (100 , 200), (255, 100, 100), 25)
            # win32api.MessageBox(0, "驼背了！驼背了！", "xiaoshenshen", win32con.MB_OK)
        return img

def main():
    if not os.path.exists('image/biaozhun.jpg'):
        get_img_from_camera_local()
    cap = cv2.VideoCapture(0)
    pTime = 0
    detector = poseDetector()
    my_face = a333.face_emotion()
    detector_face = dis_a.FaceDetector()
    # read_face = mask.real_FaceDetector()
    read = False
    while True:
        if read:success, img = cap.read()
        else:
            img = cv2.imread('image/biaozhun.jpg')
        img = detector.findPose(img)
        img = my_face.learning_face(img)
        # read_face.detect(img, False)
        # read_face.find_distance(img, text=True)
        detector_face.detect(img, False)
        jaw = detector_face.bottom
        d, w = detector_face.find_distance(img, text=True)
        detector.angle(img, 10, detector_face.top, detector_face.noe)
        img = detector.draw_angle(img)

        # if len(lmList) != 0:
        #     # print(lmList[14])
        #     cv2.circle(img, (lmList[14][1], lmList[14][2]), 15, (0, 0, 255), cv2.FILLED)
        # detector.angle(img, 80)
        # cTime = time.time()
        # fps = 1 / (cTime - pTime)
        # pTime = cTime
        img = detector.shoulder_gd(5, img)
        img = detector.find_dis_ls(img, jaw, d, w, read)
        if not read:read = True
            # time.sleep(10)
        # img = detector.draw_angle(img)
        # cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                    # (255, 0, 0), 3)
        cv2.imshow("Image", img)
        cv2.waitKey(1)
    # detector = poseDetector()
    # img = cv2.imread('lhr.jpg')
    # img = detector.findPose(img)
    # lmList = detector.findPosition(img, draw=True)
    # detector.angle(img)
    # print(lmList)
    # cv2.imshow('image', img)
    # cv2.waitKey(0)

if __name__ == "__main__":
    main()