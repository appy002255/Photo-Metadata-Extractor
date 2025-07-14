#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相片 EXIF 資料診斷工具
Photo EXIF Diagnostic Tool
"""

import os
import sys
from PIL import Image
try:
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    TAGS = {}
    GPSTAGS = {}

def test_photo(file_path):
    """測試相片檔案的 EXIF 資料"""
    print("=" * 60)
    print("相片 EXIF 資料診斷")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"錯誤：檔案不存在 - {file_path}")
        return
    
    try:
        # 開啟圖片
        with Image.open(file_path) as img:
            print(f"檔案：{file_path}")
            print(f"格式：{img.format}")
            print(f"模式：{img.mode}")
            print(f"尺寸：{img.width} x {img.height}")
            print()
            
            # 檢查是否有 EXIF 資料
            if hasattr(img, '_getexif'):
                exif_data = img._getexif()
                if exif_data:
                    print("✓ 發現 EXIF 資料")
                    print(f"EXIF 標籤數量：{len(exif_data)}")
                    print()
                    
                    # 顯示前幾個 EXIF 標籤
                    print("EXIF 標籤範例：")
                    count = 0
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, f"Unknown Tag {tag_id}")
                        print(f"  {tag_name} ({tag_id}): {value}")
                        count += 1
                        if count >= 10:  # 只顯示前10個
                            print(f"  ... 還有 {len(exif_data) - 10} 個標籤")
                            break
                    
                    # 檢查 GPS 資料
                    if 34853 in exif_data:
                        print("\n✓ 發現 GPS 資料")
                        gps_data = exif_data[34853]
                        print(f"GPS 標籤數量：{len(gps_data)}")
                        for tag_id, value in gps_data.items():
                            tag_name = GPSTAGS.get(tag_id, f"GPS Tag {tag_id}")
                            print(f"  {tag_name} ({tag_id}): {value}")
                    else:
                        print("\n✗ 沒有 GPS 資料")
                        
                else:
                    print("✗ 沒有 EXIF 資料")
                    print("\n可能的原因：")
                    print("1. 相片是用手機或相機拍攝但沒有啟用 EXIF 記錄")
                    print("2. 相片經過編輯軟體處理，EXIF 資料被移除")
                    print("3. 相片格式不支援 EXIF（如某些 PNG 檔案）")
                    print("4. 相片是截圖或從網頁下載的圖片")
            else:
                print("✗ 此圖片格式不支援 EXIF 資料")
                
    except Exception as e:
        print(f"錯誤：{str(e)}")

def main():
    if len(sys.argv) != 2:
        print("使用方法：python test_photo.py <相片檔案路徑>")
        print("範例：python test_photo.py photo.jpg")
        sys.exit(1)
    
    file_path = sys.argv[1]
    test_photo(file_path)

if __name__ == "__main__":
    main() 