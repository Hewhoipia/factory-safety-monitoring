import cv2
import csv
import os
from datetime import datetime

# COLOR & CLASS
COLOR_SAFE = (0, 255, 0)      # Green
COLOR_DANGER = (0, 0, 255)    # Red
COLOR_WARNING = (0, 255, 255) # Yellow

# Update class ID with model PPE
CLASS_ID_MAP = {
    'Hardhat': 0,
    'Mask': 1,
    'NO-Hardhat': 2,
    'NO-Mask': 3,
    'NO-Safety Vest': 4,
    'Person': 5,
    'Safety Cone': 6,
    'Safety Vest': 7,
    'machinery': 8,
    'vehicle': 9,
}

class Logger:
    '''
    Log history in folder results/
    '''
    def __init__(self, log_file="data/logs.csv"):
        self.log_file = log_file
        # create file if not exist
        if not os.path.exists(self.log_file):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
            with open(self.log_file, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Camera_ID", "Violation_Type", "Action"])

    def log(self, cam_id, violation, action):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"⚠️ [CAM {cam_id}] {violation} -> {action}")
        
        with open(self.log_file, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, cam_id, violation, action])

class HardwareSimulator:
    '''
    Simulate hardward with 2 level
    '''
    @staticmethod
    def trigger(level):
        if level == "CRITICAL":
            print(">>> [HARDWARE] 🔴 KÍCH HOẠT CÒI HÚ + NGẮT RELAY!")
        elif level == "WARNING":
            print(">>> [HARDWARE] 🟡 BẬT ĐÈN CẢNH BÁO.")

def draw_warning(frame, message, x1, y1):
    '''Draw text for each detected obj'''
    cv2.putText(frame, f"{message}", (x1, y1 - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLOR_DANGER, 2)