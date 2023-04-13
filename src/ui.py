from FunctionLibrary import *
import cv2
import time

tracker=EuclideanDistTracker()
PTime=0
obj_det=cv2.createBackgroundSubtractorMOG2(history=100,varThreshold=40)

# Parameters for Lucas-Kanade optical flow
lk_params = dict(winSize=(40, 40), maxLevel=3, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

path='C:/Users/xiemli/Desktop/Car-Speed-Detection-Python-main/2.mp4'
WebcamIsUsing=False
if WebcamIsUsing: 
    cap=cv2.VideoCapture(0)
else:
    cap=cv2.VideoCapture(path)

_,previousroi=cap.read()
previousroi=previousroi[40: 300,100: 800]
previousmask=obj_det.apply(previousroi)
_,previousmask=cv2.threshold(previousmask,100,255,cv2.THRESH_BINARY)

while True:
    _,img=cap.read()

    h,w,_,=img.shape
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
    fps=1/(CTime-PTime)
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
            if speed >= 30:
                cv2.rectangle(roi, (x, y), (x + w, y + h), (0, 0, 255), 2)
     
    cv2.imshow("mask",mask)
    cv2.imshow("roi",roi)
    cv2.imshow("img",img)

    previousmask=mask

    key=cv2.waitKey(30)
    if key==113: #113=Q
        break
