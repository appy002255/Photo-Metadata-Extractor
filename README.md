# 相片隱藏資訊提取器

Photo Metadata Extractor - 一個功能完整的相片隱藏資訊提取工具

## 功能特色

這個工具可以提取相片中的所有隱藏資訊，包括：

- **EXIF 資料**：相機設定、拍攝時間、光圈、快門速度等
- **GPS 資訊**：位置座標、海拔高度等
- **基本檔案資訊**：檔案大小、格式、建立時間等
- **原始資料**：完整的 EXIF 原始資料

## 安裝方法

### 1. 安裝 Python 依賴

```bash
pip install -r requirements.txt
```

或者手動安裝：

```bash
pip install Pillow piexif
```

### 2. 下載腳本

將以下檔案下載到你的電腦：
- `photo_metadata_extractor.py` (GUI 版本)
- `photo_metadata_cli.py` (命令列版本)

## 使用方法

### GUI 版本 (推薦)

執行圖形化介面版本：

```bash
python photo_metadata_extractor.py
```

**功能特色：**
- 直觀的圖形化介面
- 相片預覽功能
- 分頁顯示不同類型的資訊
- 一鍵儲存為 JSON 檔案
- 直接在地圖中查看 GPS 位置

**使用步驟：**
1. 點擊「瀏覽檔案」選擇相片
2. 點擊「提取資訊」開始分析
3. 在不同分頁中查看詳細資訊
4. 可選擇儲存為 JSON 檔案或在地圖中查看位置

### 命令列版本

執行命令列版本：

```bash
python photo_metadata_cli.py <相片檔案路徑>
```

**常用參數：**

```bash
# 基本使用
python photo_metadata_cli.py photo.jpg

# 儲存為 JSON 檔案
python photo_metadata_cli.py photo.jpg --output metadata.json

# 只顯示 GPS 資訊
python photo_metadata_cli.py photo.jpg --gps-only

# 只顯示 EXIF 資訊
python photo_metadata_cli.py photo.jpg --exif-only

# 只顯示基本資訊
python photo_metadata_cli.py photo.jpg --basic-only

# 顯示所有參數
python photo_metadata_cli.py --help
```

## 支援的檔案格式

- JPEG (.jpg, .jpeg)
- PNG (.png)
- TIFF (.tiff, .tif)
- BMP (.bmp)
- GIF (.gif)
- WebP (.webp)

## 提取的資訊類型

### 基本檔案資訊
- 檔案名稱和路徑
- 檔案大小
- 建立、修改、存取時間
- 圖片格式和尺寸

### EXIF 資訊
- 相機品牌和型號
- 拍攝時間
- 光圈值 (f-number)
- 快門速度
- ISO 感光度
- 焦距
- 閃光燈設定
- 白平衡
- 曝光模式
- 等等...

### GPS 資訊
- 緯度和經度座標
- GPS 時間戳
- 海拔高度
- 方向資訊
- Google Maps 連結

### 原始資料
- 完整的 EXIF 原始資料
- 所有可用的標籤和數值

## 範例輸出

### 基本資訊範例
```
基本檔案資訊:
------------------------------
檔案名稱: photo.jpg
檔案路徑: C:\Users\User\Desktop\photo.jpg
檔案大小: 2,048,000 bytes (2.0 MB)
建立時間: 2024-01-15 14:30:25
修改時間: 2024-01-15 14:30:25
圖片格式: JPEG
圖片模式: RGB
圖片尺寸: 1920 x 1080
圖片大小: 2,073,600 pixels
```

### EXIF 資訊範例
```
EXIF 資訊:
------------------------------
Make: Canon
Model: Canon EOS 5D Mark IV
DateTime: 2024:01:15 14:30:25
ExposureTime: 1/125
FNumber: 2.8
ISO: 100
FocalLength: 50.0
Flash: 16
WhiteBalance: 0
ExposureMode: 0
```

### GPS 資訊範例
```
GPS 資訊:
------------------------------
GPSLatitude: (25, 2, 30.0)
GPSLatitudeRef: N
GPSLongitude: (121, 30, 15.0)
GPSLongitudeRef: E
緯度 (十進位): 25.041667
經度 (十進位): 121.504167
Google Maps 連結: https://www.google.com/maps?q=25.041667,121.504167
```

## 注意事項

1. **隱私保護**：相片中的 GPS 資訊可能包含精確的位置資料，請注意隱私保護
2. **檔案格式**：並非所有相片都包含完整的 EXIF 資料
3. **GPS 座標**：只有啟用 GPS 功能拍攝的相片才會包含位置資訊
4. **檔案大小**：大型相片檔案可能需要較長的處理時間

## 疑難排解

### 常見問題

**Q: 無法開啟 GUI 版本**
A: 確保已安裝 tkinter（通常 Python 預設已包含）

**Q: 顯示「沒有 EXIF 資訊」**
A: 該相片可能沒有 EXIF 資料，或已被編輯軟體移除

**Q: GPS 座標不正確**
A: 檢查相片是否包含 GPS 資訊，某些編輯軟體會移除位置資料

**Q: 無法安裝依賴套件**
A: 嘗試使用 `pip3` 或更新 pip：`python -m pip install --upgrade pip`

## 技術細節

- **Python 版本**：3.7 或更高版本
- **主要依賴**：Pillow (PIL), piexif
- **GUI 框架**：tkinter (Python 內建)
- **編碼**：UTF-8

## 授權

此專案採用 MIT 授權條款。

## 貢獻

歡迎提交問題報告和功能建議！

---

**版本**：1.0.0  
**更新日期**：2025年7月 
