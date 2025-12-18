import cv2
import numpy as np
from src.utils import COLOR_WARNING

class ZoneManager:
    def __init__(self):
        pass

    @staticmethod
    def check_intrusion(point, polygon):
        """
        Kiểm tra điểm (x,y) có nằm trong polygon không.
        Return: True nếu nằm trong hoặc trên cạnh.
        """
        # measureDist=False để chỉ lấy giá trị âm/dương
        result = cv2.pointPolygonTest(polygon, point, False)
        return result >= 0

    @staticmethod
    def draw_zone(frame, polygon):
        """Vẽ vùng nguy hiểm lên hình"""
        cv2.polylines(frame, [polygon], True, COLOR_WARNING, 2)
        # Viết chữ Danger Zone
        start_point = (polygon[0][0], polygon[0][1] - 10)
        cv2.putText(frame, "DANGER ZONE", start_point, 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_WARNING, 2)