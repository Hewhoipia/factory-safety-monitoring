# Factory Safety Monitoring System

Dự án AI giám sát an toàn lao động tại nhà máy sử dụng 3 Camera với các chức năng chuyên biệt:
1. **Cam 1:** Giám sát xâm nhập Vùng nguy hiểm & Kiểm tra nón bảo hộ.
2. **Cam 2:** Giám sát xâm nhập Vùng nguy hiểm.
3. **Cam 3:** Kiểm tra tuân thủ đội nón bảo hộ.

Khi phát hiện vi phạm/nguy hiểm:
- Lưu lịch sử
- Kích hoạt cảnh báo (hiển thị, âm thanh, v.v.).
- Trong trường hợp xâm nhập khu vực nguy hiểm, cần giả lập hành động gửi tín hiệu điều khiển ra phần cứng

## 1. Cài đặt

Yêu cầu Python 3.8+

```bash
# Thư viện
pip install -r requirements.txt
```
Chuẩn bị model best.pt trong folder models/, videos để giả lập cameras trong folder data/videos/

Project này sử dụng:
- Model từ https://github.com/snehilsanyal/Construction-Site-Safety-PPE-Detection
- Python 3.12.2 và các phiên bản thư viện mới nhất

## 2. Thực thi
```bash
# Command used for MacOS
cd ./.../factory-safety-monitoring
python ./main.py
```

## 3. Giải thích
### src/
1. **[detector.py](src/detector.py)** với class SafetyDetector, lấy model thông qua YOLO, với 2 functions detect và detect_in_zone
2. **[utils.py](src/utils.py)** cài đặt màu sắc và class id tuỳ theo model; ghi lại dữ liệu bằng class Logger; giả lập phần cứng bằng class HardwareSimulator; và 1 hàm dùng để in văn bản cho vật được phát hiện.
3. **[zones.py](src/zones.py)** với class ZoneManager sử dụng để vẽ và kiểm tra vật thể xâm nhập vùng nguy hiểm

### main.py
Xem diagram bên dưới hoặc [hình ảnh](results/explain.png)
```mermaid
flowchart TD
    Start([Start Program]) --> Init[Initialize: Detector, Loggers, Hardware, Video Sources]
    Init --> DefineZones[Define Safety Zones for Cam 1 & 2]
    DefineZones --> While[While True Loop]
    
    subgraph Main_Loop [While True Loop]
        Read[Read Frames from 3 Cameras] --> Frame_Check{No signal?}
        Frame_Check -- Yes --> End
        Frame_Check -- No --> Resize[Resize/Crop Frames]
        
        %% Branching for 3 Cameras
        Resize --> Cam1_Flow
        Resize --> Cam2_Flow
        Resize --> Cam3_Flow
        
        %% CAM 1 LOGIC
        subgraph Cam1_Flow [Cam 1: Intrusion & PPE]
            C1_Draw[Draw zone] --> C1_Det[Detect 'Persons' in frame]
            C1_Det --> C1_Check{'Person' in zone?}
            C1_Check -- No --> C1_Safe[Mark Safe]
            C1_Check -- Yes --> C1_Intruder[Warning: Intrusion]
            C1_Intruder --> C1_Crop[Crop 'Person' frame]
            C1_Crop --> C1_Det2[Detect 'NO-Hardhat' in Crop]
            C1_Det2 --> C1_HatCheck{No Hat?}
            C1_HatCheck -- Yes --> C1_Crit[<b>ALARM: CRITICAL</b><br>Intrusion + No Hat]
            C1_HatCheck -- No --> C1_Warn[<b>ALARM: WARNING</b><br>Intrusion Only]
        end

        %% CAM 2 LOGIC
        subgraph Cam2_Flow [Cam 2: Intrusion Only]
            C2_Draw[Draw Zone] --> C2_Det[Detect 'Persons']
            C2_Det --> C2_Check{Person in Zone?}
            C2_Check -- No --> C2_Safe[Mark Safe]
            C2_Check -- Yes --> C2_Warn[<b>ALARM: WARNING</b><br>Intrusion]
        end

        %% CAM 3 LOGIC
        subgraph Cam3_Flow [Cam 3: PPE Only]
            C3_Det[Detect class 'NO-Hardhat']
            C3_Det --> C3_Check{No hat?}
            C3_Check -- Hardhat --> C3_Safe[Mark Safe]
            C3_Check -- No-Hardhat --> C3_Warn[<b>ALARM: WARNING</b><br>No PPE]
        end

        %% Logging & Display
        C1_Warn & C1_Crit & C2_Warn & C3_Warn --> Log[Log to CSV & Trigger Hardware]
        C1_Safe & C1_Warn & C1_Crit & C2_Safe & C2_Warn & C3_Safe & C3_Warn --> Display[cv2.imshow]
    end
    
    Display --> Q_Check{Key 'q' pressed?}
    Q_Check -- No --> Read
    Q_Check -- Yes --> End([End Program])
```
