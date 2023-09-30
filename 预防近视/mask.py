import cv2
import time
import cvzone
from cvzone.FaceMeshModule import FaceMeshDetector


class real_FaceDetector:
    def __init__(self, maxFaces=1):
        self.maxFaces = 1
        self.detector = FaceMeshDetector(self.maxFaces)

        self.start_time = None  # 计时开始时间
        self.elapsed_time = None  # 已用时间

        self.is_focusing = False  # 是否正视

    def detect(self, img, draw_circle=False, draw_face=False):
        # 寻找特征点
        img, faces = self.detector.findFaceMesh(img, draw=draw_face)
        if faces:
            face = faces[0]

            # 开始计时
            if self.start_time is None:
                self.start_time = time.time()

            pointLeft = face[145]  # 左眼中心点坐标
            pointRight = face[374]  # 右眼中心点坐标
            self.pointLeft = pointLeft
            self.pointRight = pointRight
            self.face = face
            self.bottom = face[152]

            # 绘制人眼中心点并连线
            if draw_circle:
                self.draw(img)

            # 判断眼球是否正视
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


        # 计算已用时间
        if self.start_time is not None:
            self.elapsed_time = time.time() - self.start_time

        # 显示时间
        if text:
            cvzone.putTextRect(img, f'Time:{int(self.elapsed_time)}s', (img.shape[1]-200, img.shape[0] - 450),
                               scale=2,colorR=(255,255,0), colorT=(0,0,0))

        return self.is_focusing


def main():
    cap = cv2.VideoCapture(0)
    detector_face = real_FaceDetector()

    while True:
        success, img = cap.read()
        pointLeft, pointRight = detector_face.detect(img, False)
        is_focusing = detector_face.find_distance(img, text=True)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
