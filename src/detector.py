from ultralytics import YOLO

class SafetyDetector:
    def __init__(self, model_path):
        print(f"Loading model from: {model_path} ...")
        self.model = YOLO(model_path)
    
    def detect(self, frame, conf_threshold=0.5):
        """
        Format: list of [x1, y1, x2, y2, class_id]
        """
        results = self.model(frame, verbose=False, conf=conf_threshold)[0]
        detections = []
        
        for box in results.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cls_id = int(box.cls[0])
            detections.append([x1, y1, x2, y2, cls_id])
        return detections
    
    def detect_in_zone(self, frame, zone, padding = 10):
        '''
        Detect in specific zone
        Return list of [x1, y1, x2, y2, class_id]
        '''
        # Add padding
        h_orig, w_orig = frame.shape[:2]
        zx1, zy1, zx2, zy2 = zone
        ezx1 = max(0, zx1 - padding)
        ezy1 = max(0, zy1 - padding)
        ezx2 = min(w_orig, zx2 + padding)
        ezy2 = min(h_orig, zy2 + padding)
        
        # Crop
        cropped_frame = frame[ezy1:ezy2, ezx1:ezx2]
        if cropped_frame.size == 0:
            return []

        dets_in_crop = self.detect(cropped_frame)
        
        # Mapping to original frame
        final_dets = []
        for (cx1, cy1, cx2, cy2, cls) in dets_in_crop:
            real_x1 = cx1 + zx1
            real_y1 = cy1 + zy1
            real_x2 = cx2 + zx1
            real_y2 = cy2 + zy1
            
            final_dets.append([real_x1, real_y1, real_x2, real_y2, cls])
            
        return final_dets