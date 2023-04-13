from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5 import uic
import sys
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
import time
import math
import numpy as np

speed_high=0
speed_low=0


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(1048, 868)
        self.label = QtWidgets.QLabel(Form)
        self.label.setGeometry(QtCore.QRect(320, 5, 71, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(Form)
        self.label_2.setGeometry(QtCore.QRect(350, 450, 71, 31))
        self.label_2.setObjectName("label_2")
        self.graphicsView = QtWidgets.QGraphicsView(Form)
        self.graphicsView.setGeometry(QtCore.QRect(62, 32, 681, 401))
        self.graphicsView.setObjectName("graphicsView")
        self.graphicsView_2 = QtWidgets.QGraphicsView(Form)
        self.graphicsView_2.setGeometry(QtCore.QRect(60, 490, 681, 301))
        self.graphicsView_2.setObjectName("graphicsView_2")
        self.lineEdit = QtWidgets.QLineEdit(Form)
        self.lineEdit.setGeometry(QtCore.QRect(780, 320, 231, 31))
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(Form)
        self.lineEdit_2.setGeometry(QtCore.QRect(780, 360, 231, 31))
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(780, 420, 131, 51))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(780, 490, 131, 51))
        self.pushButton_2.setObjectName("pushButton_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "速度监测系统"))
        self.label.setText(_translate("Form", "动态监测"))
        self.label_2.setText(_translate("Form", "二值化视角"))
        self.lineEdit.setPlaceholderText(_translate("Form", "请输入速度上限"))
        self.lineEdit_2.setPlaceholderText(_translate("Form", "请输入速度下限"))
        self.pushButton.setText(_translate("Form", "导入视频"))
        self.pushButton_2.setText(_translate("Form", "开始监测"))
class EuclideanDistTracker:
    def __init__(self):
        self.center_points={}
        self.id_count=0
    def update(self,obj_rect):
        obj_bbx_ids=[]
        for rect in obj_rect:
            x,y,w,h=rect
            cx=(x+x+w)//2
            cy=(y+y+h)//2
            same_obj=False
            for id,pt in self.center_points.items():
                dist=math.hypot(cx-pt[0],cy-pt[1])
                if dist<25:
                    self.center_points[id]=(cx,cy)
                    obj_bbx_ids.append([x,y,w,h,id])
                    same_obj=True
                    break
            if same_obj is False:
                self.center_points[self.id_count]=(cx,cy)
                obj_bbx_ids.append([x,y,w,h,self.id_count])
                self.id_count+=1
        new_cnt_point={}
        for bb_id in obj_bbx_ids:
            _,_,_,_,obj_id=bb_id
            center=self.center_points[obj_id]
            new_cnt_point[obj_id]=center
        self.center_points=new_cnt_point.copy()
        return obj_bbx_ids

class SpeedEstimator:
    def __init__(self, posList, posPast,fps):
        self.x = posList[0]
        self.y = posList[1]
        self.xp=posPast[0]
        self.yp=posPast[1]
        self.fps = fps

    def estimateSpeed(self):
        # Distance / Time -> Speed
        d_pixels = math.sqrt(self.x + self.y)
        d_pixelsx=(self.x-self.xp)
        d_pixelsx2=pow(d_pixelsx,2)
        d_pixelsy=(self.y-self.yp)
        d_pixelsy2=pow(d_pixelsy,2)
        d_pixels = math.sqrt(d_pixelsx2+d_pixelsy2)
        ppm = 40
        d_meters = int(d_pixels * ppm)

        speed = d_meters / self.fps * 3.6
        speedInKM = np.average(speed)
        return int(speedInKM)

class MyWindow(QWidget):
    def __init__(self,name='速度监测系统'):
        super().__init__()
        self.init_ui(name)
 
    def init_ui(self,name):
       self.ui=Ui_Form()
       self.ui.setupUi(self) # 调用Ui_Form中的初始化函数对界面进行初始化
       self.setWindowTitle(name) # 更改界面标题
       self.initConnect() # 将识别与测量按键 与 对应的函数进行链接

    def initConnect(self):
        self.video_btn1 = self.ui.pushButton
        self.video_btn2 = self.ui.pushButton_2
        self.QGraphView = self.ui.graphicsView
        self.QGraphView2 = self.ui.graphicsView_2
 
        # video_btn1 绑定槽函数 loadVideo()
        self.video_btn1.clicked.connect(self.loadVideo)
 
        # video_btn2 绑定槽函数 playVideo()
        self.video_btn2.clicked.connect(self.playVideo)
        self.ui.lineEdit.editingFinished.connect(self.change_high) 
        self.ui.lineEdit_2.editingFinished.connect(self.change_low) 
 
    def loadVideo(self):
        self.video_file = QFileDialog.getOpenFileUrl()[0]
        self.video_path = self.video_file.toString()[8:]
        
    def playVideo(self):
        global speed_high,speed_low
        tracker=EuclideanDistTracker()
        PTime=0
        obj_det=cv2.createBackgroundSubtractorMOG2(history=100,varThreshold=40)

        # Parameters for Lucas-Kanade optical flow
        lk_params = dict(winSize=(40, 40), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        WebcamIsUsing=False
        if WebcamIsUsing: 
            cap=cv2.VideoCapture(0)
        else:
            print(self.video_path)
            cap=cv2.VideoCapture(self.video_path)

        _,previousroi=cap.read()
        
        previousroi=previousroi[40: 300,100: 800]
        previousmask=obj_det.apply(previousroi)
        _,previousmask=cv2.threshold(previousmask,100,255,cv2.THRESH_BINARY)

        while True:
            ret,img=cap.read()
            if not ret:
                break
            # h,w,_,=img.shape
            roi=img[40: 300,100: 800]
            mask=obj_det.apply(roi)
            _,mask=cv2.threshold(mask,100,255,cv2.THRESH_BINARY)
            cont,_=cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
            det=[]
            for cnt in cont:
                area=cv2.contourArea(cnt)
                if area>100:
                    cv2.drawContours(roi,[cnt],-1,(0,255,0),2)
                    x,y,w,h=cv2.boundingRect(cnt)
                    det.append([x,y,w,h])
            
            CTime=time.time()
            # fps=1/(CTime-PTime)
            fps=60
            PTime=CTime
            '''目标检测'''
            boxes_ids=tracker.update(det)

            for box in boxes_ids:
                x,y,w,h,id=box
                cv2.rectangle(roi, (x, y), (x + w, y + h), (255, 255, 0), 3)

                '''计算四个光流点的速度取平均'''
                initialFeatures = np.float32((x +  w / 2, y +  h / 2)).reshape(-1, 1, 2)
                flowForward, status1, err1 = cv2.calcOpticalFlowPyrLK(mask, previousmask, initialFeatures, None,
                                                                    **lk_params)
                for x1, y1 in np.float32(flowForward).reshape(-1, 2):
                    xp = x1
                    yp = y1
                SpeedEstimatorTool=SpeedEstimator([x +  w / 2, y +  h / 2],[xp, yp],fps)
                speed1=SpeedEstimatorTool.estimateSpeed()

                initialFeatures = np.float32((x + w / 4, y + h / 4)).reshape(-1, 1, 2)
                flowForward, status1, err1 = cv2.calcOpticalFlowPyrLK(mask, previousmask, initialFeatures, None,
                                                                    **lk_params)
                for x1, y1 in np.float32(flowForward).reshape(-1, 2):
                    xp = x1
                    yp = y1
                SpeedEstimatorTool = SpeedEstimator([x + w / 4, y + h / 4], [xp, yp], fps)
                speed2 = SpeedEstimatorTool.estimateSpeed()

                initialFeatures = np.float32((x + w / 2, y + h / 4)).reshape(-1, 1, 2)
                flowForward, status1, err1 = cv2.calcOpticalFlowPyrLK(mask, previousmask, initialFeatures, None,
                                                                    **lk_params)
                for x1, y1 in np.float32(flowForward).reshape(-1, 2):
                    xp = x1
                    yp = y1
                SpeedEstimatorTool = SpeedEstimator([x + w / 2, y + h / 4], [xp, yp], fps)
                speed3 = SpeedEstimatorTool.estimateSpeed()

                initialFeatures = np.float32((x + w / 4, y + h / 2)).reshape(-1, 1, 2)
                flowForward, status1, err1 = cv2.calcOpticalFlowPyrLK(mask, previousmask, initialFeatures, None,
                                                                    **lk_params)
                for x1, y1 in np.float32(flowForward).reshape(-1, 2):
                    xp = x1
                    yp = y1
                SpeedEstimatorTool = SpeedEstimator([x + w / 4, y + h / 2], [xp, yp], fps)
                speed4 = SpeedEstimatorTool.estimateSpeed()

                speed=(speed1+speed2+speed3+speed4)/4

                if WebcamIsUsing and speed>=0 and speed <=10:
                    cv2.putText(roi,str(speed)+"Km/h",(x,y-15),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,255),2)
                else:
                    if speed >= 0 and speed <= 50:
                        cv2.putText(roi, str(speed) + "Km/h", (x, y - 15), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
                    '''超过30公里超速标红框'''
                    if speed >= speed_high:
                        cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 255), 2) 
                    if speed <=speed_low:
                        cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 0), 3) 
            
            frame =QImage(img.data, img.shape[1],img.shape[0], img.strides[0], QImage.Format_RGB888)
            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)  # 创建像素图元
            scene = QGraphicsScene()  # 创建场景
            scene.addItem(item)
            self.QGraphView.setScene(scene)  # 将场景添加至视图
            # self.QGraphView.fitInView(item)  # 自适应大小
    


            # image=img
            # resize_rate = 1  # 图像缩小比例，方便展示
            # self.frame_temp = image
            # img_w, img_h, _ = self.frame_temp.shape
            # self.frame_temp = cv2.resize(self.frame_temp, (int(img_h / resize_rate), int(img_w / resize_rate))) # 按比例缩放图像大小，适应ui界面

            # #执行检测操作
            # height, width,_ = self.frame_temp.shape # 获取当前图像的宽高
            # image = QImage(self.frame_temp.data, width, height, width,QImage.Format_Indexed8) #修改图像格式为QImage以便在UI中展示
            # self.ui.label.setPixmap(QPixmap.fromImage(image)) # 在UI界面中进行实时的检测结果展示


            frame = QImage(mask.data, mask.shape[1],mask.shape[0], mask.strides[0], QImage.Format_Indexed8)
            pix = QPixmap.fromImage(frame)
            item = QGraphicsPixmapItem(pix)  # 创建像素图元
            scene = QGraphicsScene()  # 创建场景
            scene.addItem(item)
            self.QGraphView2.setScene(scene)  # 将场景添加至视图
            # self.QGraphView2.fitInView(item)  # 自适应大小
            cv2.waitKey(int(1/fps*1000)&0xff)

            # image1=mask
            # resize_rate = 1  # 图像缩小比例，方便展示
            # self.frame_temp = image1
            # img_w, img_h= self.frame_temp.shape
            # self.frame_temp = cv2.resize(self.frame_temp, (int(img_h / resize_rate), int(img_w / resize_rate))) # 按比例缩放图像大小，适应ui界面

            # #执行检测操作
            # height, width= self.frame_temp.shape # 获取当前图像的宽高
            # image1 = QImage(self.frame_temp.data, width, height, width,QImage.Format_Indexed8) #修改图像格式为QImage以便在UI中展示
            # self.ui.label_2.setPixmap(QPixmap.fromImage(image1)) # 在UI界面中进行实时的检测结果展示
            # cv2.waitKey(int(5))

            # cv2.imshow("mask",mask)
            # cv2.imshow("roi",roi)
            # cv2.imshow("img",img)
            # delay=int(1/fps*1000)
            # print(delay)
            # key=cv2.waitKey(delay)
          
        
 
    def change_high(self):
        global speed_high
        if self.ui.lineEdit=='':
            return
        else:
            speed_high=int(self.ui.lineEdit.text())
    
    def change_low(self):
        global speed_low
        if self.ui.lineEdit_2=='':
            return
        else:
            speed_low=int(self.ui.lineEdit_2.text())


        
if __name__ == '__main__':
 
    app = QApplication(sys.argv)
    w = MyWindow()
    w.show()
    sys.exit(app.exec_())
