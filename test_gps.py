#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GPS 資料提取測試工具
GPS Data Extraction Test Tool
"""

import os
import sys
from PIL import Image
try:
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    TAGS = {}
    GPSTAGS = {}
import piexif

def test_gps_extraction(file_path):
    """測試 GPS 資料提取"""
    print("=" * 60)
    print("GPS 資料提取測試")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"錯誤：檔案不存在 - {file_path}")
        return
    
    try:
        # 方法一：使用 PIL
        print("方法一：PIL EXIF 提取")
        print("-" * 30)
        with Image.open(file_path) as img:
            if hasattr(img, '_getexif'):
                exif_data = img._getexif()
                if exif_data and 34853 in exif_data:
                    gps_data = exif_data[34853]
                    print("✓ PIL 發現 GPS 資料")
                    print(f"GPS 標籤數量：{len(gps_data)}")
                    for tag_id, value in gps_data.items():
                        tag_name = GPSTAGS.get(tag_id, f"GPS Tag {tag_id}")
                        print(f"  {tag_name} ({tag_id}): {value}")
                else:
                    print("✗ PIL 沒有發現 GPS 資料")
            else:
                print("✗ 此格式不支援 EXIF")
        
        print("\n方法二：piexif 提取")
        print("-" * 30)
        try:
            exif_dict = piexif.load(file_path)
            if exif_dict and 'GPS' in exif_dict and exif_dict['GPS']:
                gps_data = exif_dict['GPS']
                print("✓ piexif 發現 GPS 資料")
                print(f"GPS 標籤數量：{len(gps_data)}")
                for tag_id, value in gps_data.items():
                    print(f"  GPS Tag {tag_id}: {value}")
            else:
                print("✗ piexif 沒有發現 GPS 資料")
        except Exception as e:
            print(f"✗ piexif 錯誤：{str(e)}")
            
        print("\n" + "=" * 60)
        print("總結")
        print("=" * 60)
        print("• 如果兩種方法都沒有發現 GPS 資料，表示相片沒有位置資訊")
        print("• 建議拍攝新相片時確保啟用位置服務")
        print("• 某些編輯軟體會移除 GPS 資料以保護隱私")
        
    except Exception as e:
        print(f"錯誤：{str(e)}")

def main():
    if len(sys.argv) != 2:
        print("使用方法：python test_gps.py <相片檔案路徑>")
        print("範例：python test_gps.py photo.jpg")
        sys.exit(1)
    
    file_path = sys.argv[1]
    test_gps_extraction(file_path)

if __name__ == "__main__":
    main() 