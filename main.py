import cv2
import numpy as np
import time
from src.detector import SafetyDetector
from src.zones import ZoneManager
from src.utils import Logger, HardwareSimulator, CLASS_ID_MAP, COLOR_DANGER, COLOR_SAFE, draw_warning

# Config
#MODEL_PATH = "models/yolov8n.pt" # yolov8n.pt for test
MODEL_PATH = "models/best.pt"
VIDEO_SOURCES = ["data/videos/cam1.mp4", "data/videos/cam2.mp4", "data/videos/cam1.mp4"] # use 1 video to simulate 3 cams
#VIDEO_SOURCES = [0, 0 ,0] # test

def resize(frame, target_w=640, target_h=640):
    '''
    Crop or resize frame to target size
    '''
    if frame is None: return None
    h, w = frame.shape[:2]
    if h < target_h or w < target_w:
        # Resize
        return cv2.resize(frame, (target_w, target_h))
    
    # Crop
    start_x = (w - target_w) // 2
    start_y = (h - target_h) // 2
    return frame[start_y:start_y+target_h, start_x:start_x+target_w]

def main():
    detector = SafetyDetector(MODEL_PATH)
    logger1 = Logger(log_file="results/logs1.csv")
    logger2 = Logger(log_file="results/logs2.csv")
    logger3 = Logger(log_file="results/logs3.csv")
    hardware = HardwareSimulator()
    
    caps = [cv2.VideoCapture(src) for src in VIDEO_SOURCES]
    
    # Định nghĩa Vùng nguy hiểm (Polygon) cho Cam 1 và Cam 2
    # top left, down left, down right, top right
    z1_tl, z1_dl, z1_dr, z1_tr = [250, 0], [250, 400], [639, 400], [639, 0] # zone 1
    z2_tl, z2_dl, z2_dr, z2_tr =[300, 0], [100, 400], [500, 400], [639, 0] # zone 2
    zone_1 = np.array([z1_tl, z1_dl, z1_dr, z1_tr], np.int32)
    zone_2 = np.array([z2_tl, z2_dl, z2_dr, z2_tr], np.int32)

    print(">>> Hệ thống bắt đầu giám sát. Nhấn 'q' để thoát.")
    
    def cam1(frame):
        ZoneManager.draw_zone(frame, zone_1)
        dets1 = np.array(detector.detect(frame))
        
        if dets1.size > 0: # check if there is no detected obj
            coords = dets1[:, :-1] # coordinates
            cls = dets1[:, -1] # class id
            has_person = [clsid == CLASS_ID_MAP['Person'] for clsid in cls] # return list of detected person in bool
            for coord in coords[has_person]: # loop all detected obj
                x1, y1, x2, y2 = coord.tolist()
                center_point = ((x1 + x2) // 2, y2)
                if ZoneManager.check_intrusion(center_point, zone_1):
                    violation_msg = "Intrusion"
                    alarm = "ALARM WARNING"
                    hw = "WARNING"
                    
                    # check hat when join the warning zone
                    dets1_in_zone = np.array(detector.detect_in_zone(frame, (x1, y1, x2, y2))) # detect only in the 'Person' frame
                    if dets1_in_zone.size > 0:
                        coords = dets1_in_zone[:, :-1]
                        cls = dets1_in_zone[:, -1]
                        no_hat_in_zone = [clsid == CLASS_ID_MAP['NO-Hardhat'] for clsid in cls]
                        if any(i for i in no_hat_in_zone):
                            violation_msg = "Intrusion & no hat"
                            alarm = "ALARM CRITICAL"
                            hw = "CRITICAL"  
                        has_hat_in_zone = [clsid == CLASS_ID_MAP['Hardhat'] for clsid in cls]
                        for coord in coords[has_hat_in_zone]:
                            x1, y1, x2, y2 = coord.tolist()
                            cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_SAFE, 2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_DANGER, 2)
                    draw_warning(frame, violation_msg, x1, y1)
                    logger1.log(1, violation_msg, alarm)
                    hardware.trigger(hw)
                    
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_SAFE, 2)
    
    def cam2(frame):
        ZoneManager.draw_zone(frame, zone_2)
        dets2 = np.array(detector.detect(frame))
        
        if dets2.size > 0:
            coords = dets2[:, :-1]
            cls = dets2[:, -1]
            has_person = [clsid == CLASS_ID_MAP['Person'] for clsid in cls]
            for coord in coords[has_person]:
                x1, y1, x2, y2 = coord.tolist()
                center_point = ((x1 + x2) // 2, y2)
                if ZoneManager.check_intrusion(center_point, zone_2):
                    cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_DANGER, 2)
                    draw_warning(frame, "Intrusion", x1, y1)
                    logger2.log(2, "Intrusion", "ALARM WARNING")
                    hardware.trigger("WARNING")
                else:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_SAFE, 2)
    
    def cam3(frame):
        dets3 = np.array(detector.detect(frame))
        
        if dets3.size > 0:
            coords = dets3[:, :-1]
            cls = dets3[:, -1]
            no_hat = [clsid == CLASS_ID_MAP['NO-Hardhat'] for clsid in cls]
            has_hat = [clsid == CLASS_ID_MAP['Hardhat'] for clsid in cls]
            for coord in coords[no_hat]:
                x1, y1, x2, y2 = coord.tolist()
                cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_DANGER, 2)
                draw_warning(frame, "No hat", x1, y1)
                logger3.log(3, "No PPE", "ALARM WARNING")
                hardware.trigger("WARNING")
            for coord in coords[has_hat]:
                x1, y1, x2, y2 = coord.tolist()
                cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_SAFE, 2)

    while True:
        frames = []
        for cap in caps:
            ret, frame = cap.read()
            if not ret:
                frames.append(None)
            else:
                frames.append(resize(frame)) # Resize
        
        # Stop if no signal
        if any(f is None for f in frames):
            print("Kết thúc video.")
            break

        # CAM 1: Intrusion + PPE
        frame1 = frames[0]
        cam1(frame1)

        # CAM 2: Intrusion Only
        frame2 = frames[1]
        cam2(frame2)

        # CAM 3: PPE Only
        frame3 = frames[2]
        cam3(frame3)

        # Display
        cv2.imshow("CAM 1: Intrusion & PPE", frame1)
        cv2.imshow("CAM 2: Intrusion", frame2)
        cv2.imshow("CAM 3: PPE Check", frame3)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Clean up
    for cap in caps: cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()