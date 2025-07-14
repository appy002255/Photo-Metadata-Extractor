#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化 EXIF 查看器
Simple EXIF Viewer - 只顯示最重要的相機資訊
"""

import os
import sys
from PIL import Image
try:
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    TAGS = {}
    GPSTAGS = {}

def get_important_exif(file_path):
    """提取重要的 EXIF 資訊"""
    important_info = {}
    
    try:
        with Image.open(file_path) as img:
            if hasattr(img, '_getexif'):
                exif_data = img._getexif()
                if exif_data:
                    # 重要標籤對應
                    important_tags = {
                        271: '相機品牌',
                        272: '相機型號', 
                        306: '拍攝時間',
                        36867: '原始拍攝時間',
                        37377: '光圈值',
                        37387: '快門速度',
                        37380: 'ISO 感光度',
                        37396: '焦距',
                        37395: '閃光燈',
                        41987: '白平衡',
                        41990: '場景模式',
                        41992: '對比度',
                        41993: '飽和度',
                        41994: '銳利度',
                        42035: '鏡頭品牌',
                        42036: '鏡頭型號'
                    }
                    
                    for tag_id, value in exif_data.items():
                        if tag_id in important_tags:
                            tag_name = important_tags[tag_id]
                            
                            # 格式化數值
                            if tag_id == 37377:  # 光圈值
                                value = f"f/{value/100}" if value > 0 else str(value)
                            elif tag_id == 37387:  # 快門速度
                                value = f"1/{int(2**value)}s" if value > 0 else str(value)
                            elif tag_id == 37396:  # 焦距
                                value = f"{value}mm"
                            elif tag_id == 37380:  # ISO
                                value = f"ISO {value}"
                            elif tag_id == 37395:  # 閃光燈
                                flash_values = {0: "未使用", 1: "使用", 9: "強制使用", 16: "關閉"}
                                value = flash_values.get(value, str(value))
                            elif tag_id == 41987:  # 白平衡
                                wb_values = {0: "自動", 1: "手動"}
                                value = wb_values.get(value, str(value))
                            elif tag_id == 41990:  # 場景模式
                                scene_values = {0: "標準", 1: "風景", 2: "人像", 3: "夜景"}
                                value = scene_values.get(value, str(value))
                            elif isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='ignore')
                                except:
                                    value = str(value)
                            
                            important_info[tag_name] = value
                    
                    # 檢查 GPS 資料
                    if 34853 in exif_data:
                        gps_data = exif_data[34853]
                        important_info['GPS 資料'] = '有'
                        
                        # 嘗試提取座標
                        try:
                            lat = get_gps_coordinate(gps_data, 'GPSLatitude', 'GPSLatitudeRef')
                            lon = get_gps_coordinate(gps_data, 'GPSLongitude', 'GPSLongitudeRef')
                            if lat and lon:
                                important_info['緯度'] = lat
                                important_info['經度'] = lon
                        except:
                            pass
                    else:
                        important_info['GPS 資料'] = '無'
                        
    except Exception as e:
        important_info['錯誤'] = str(e)
    
    return important_info

def get_gps_coordinate(gps_data, lat_key, ref_key):
    """提取 GPS 座標"""
    try:
        if lat_key in gps_data and ref_key in gps_data:
            lat_data = gps_data[lat_key]
            ref_data = gps_data[ref_key]
            
            if isinstance(lat_data, tuple) and len(lat_data) == 3:
                degrees = float(lat_data[0])
                minutes = float(lat_data[1])
                seconds = float(lat_data[2])
                
                coordinate = degrees + (minutes / 60.0) + (seconds / 3600.0)
                
                if isinstance(ref_data, bytes):
                    ref_data = ref_data.decode('utf-8', errors='ignore')
                
                if ref_data == 'S' or ref_data == 'W':
                    coordinate = -coordinate
                    
                return round(coordinate, 6)
    except:
        return None
    
    return None

def main():
    if len(sys.argv) != 2:
        print("使用方法：python simple_exif_viewer.py <相片檔案路徑>")
        print("範例：python simple_exif_viewer.py photo.jpg")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if not os.path.exists(file_path):
        print(f"錯誤：檔案不存在 - {file_path}")
        return
    
    print("=" * 50)
    print("簡化 EXIF 資訊")
    print("=" * 50)
    
    important_info = get_important_exif(file_path)
    
    if important_info:
        for key, value in important_info.items():
            print(f"{key}: {value}")
    else:
        print("沒有找到 EXIF 資料")
    
    print("\n" + "=" * 50)
    print("提示：")
    print("• 如果沒有 GPS 資料，請確保拍攝時啟用位置服務")
    print("• 某些編輯軟體會移除 EXIF 資料")
    print("• 建議使用原始相機拍攝的相片")

if __name__ == "__main__":
    main() 