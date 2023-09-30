import cv2
import win32api, win32con
import time
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector
# 检测人脸


class FaceDetector:
    def __init__(self, maxFaces=1):
        self.maxFaces = 1
        self.detector = FaceMeshDetector(self.maxFaces)
        # print("aaaaaaaaaa")
        self.start_time = None  # 计时开始时间
        self.elapsed_time = None  # 已用时间

        self.is_focusing = False  # 是否正视

    def detect(self, img, draw_circle=False, draw_face = True):
        # 寻找特征点
        img, faces = self.detector.findFaceMesh(img, draw=draw_face)
        if faces:
            face = faces[0]
            pointLeft = face[145]  # 左眼中心点坐标
            pointRight = face[374]  # 右眼中心点坐标
            self.pointLeft = pointLeft
            # print(face)
            self.pointRight = pointRight
            self.face = face
            self.bottom = face[152]
            self.top = face[151]
            self.noe = face[168]
            for i in [151, 168]:
                cv2.circle(img, face[i], 5, (255, 0, 255), cv2.FILLED)
                cv2.putText(img, str(i), (face[i][0]+10,face[i][1]+10),cv2.FONT_HERSHEY_SIMPLEX, 0.4,color=(244,0,0))
            if self.start_time is None:
                self.start_time = time.time()
            # 绘制人眼中心点并连线
            if draw_circle:
                self.draw(img)
            if abs(self.pointLeft[1] - self.pointRight[1]) < 10 and abs(self.pointLeft[0] - self.pointRight[0]) < 90:
                self.is_focusing = True
                print("眼球正视")
            else:
                self.is_focusing = False
                print("眼球未正视")
                self.start_time = time.time()
            return pointLeft, pointRight

    def draw(self, img):
        cv2.line(img, self.pointLeft, self.pointRight, (0, 200, 0), 3)
        cv2.circle(img, self.pointLeft, 5, (255, 0, 255), cv2.FILLED)
        cv2.circle(img, self.pointRight, 5, (255, 0, 255), cv2.FILLED)


    def find_distance(self, img, W=6.3, f=600, text=True):
        w, _ = self.detector.findDistance(self.pointLeft, self.pointRight)
        # W = 6.3
        # f = 600  # 根据相机标定的结果
        d = (W * f) / w
        # print(d)
        if text:
            cvzone.putTextRect(img, f'Depth:{int(d)}cm', (self.face[10][0] - 100, self.face[10][1] - 50), scale=2)
        if d < 40 or d > 80:
            print("距离不对")
            # win32api.MessageBox(0, "距离不对！距离不对！", "xiaoshenshen", win32con.MB_OK)
        if self.start_time is not None:
            self.elapsed_time = time.time() - self.start_time

        # 显示时间
        if text:
            cvzone.putTextRect(img, f'Time:{int(self.elapsed_time)}s', (img.shape[1]-200, img.shape[0] - 450),
                               scale=2,colorR=(255,255,0), colorT=(0,0,0))

        return d, w


def main():
    cap = cv2.VideoCapture(0)
    detector_face = FaceDetector()
    while True:
        success, img = cap.read()
        detector_face.detect(img, True)
        detector_face.find_distance(img, text=True)
        # img, faces = detector.findFaceMesh(img)
        # if faces:
        #     face = faces[0]
        #     pointLeft = face[145]  # 左眼中心点坐标
        #     pointRight = face[374]  # 右眼中心点坐标
        #     # 绘制人眼中心点并连线
        #     cv2.line(img, pointLeft, pointRight, (0, 200, 0), 3)
        #     cv2.circle(img, pointLeft, 5, (255, 0, 255), cv2.FILLED)
        #     cv2.circle(img, pointRight, 5, (255, 0, 255), cv2.FILLED)
        #     w, _ = detector.findDistance(pointLeft, pointRight)  # 保持人脸到摄像头50cm下测量
        #     W = 6.3  # 真实人脸间距 6.3cm
        #     # Finding the Focal Length
        #     # d= 40 # 保持人脸到摄像头50cm的距离
        #     # f=(w*d)/W
        #     # print(f)
        #
        #     # Finding distance
        #     f = 600  # 根据相机标定的结果
        #     d = (W * f) / w
        #     # print(d)
        #     cvzone.putTextRect(img, f'Depth:{int(d)}cm', (face[10][0] - 100, face[10][1] - 50), scale=2)
        #     if d < 40 or d > 80:
        #         print("距离不对")
        cv2.imshow("Image", img)
        cv2.waitKey(1)



if __name__ == '__main__':
    main()