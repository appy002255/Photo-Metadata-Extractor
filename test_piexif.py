#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
piexif 診斷工具
piexif Diagnostic Tool
"""

import os
import sys
import piexif

def test_piexif(file_path):
    """測試 piexif 功能"""
    print("=" * 60)
    print("piexif 診斷工具")
    print("=" * 60)
    
    if not os.path.exists(file_path):
        print(f"錯誤：檔案不存在 - {file_path}")
        return
    
    try:
        print(f"檔案：{file_path}")
        print()
        
        # 嘗試載入 EXIF 資料
        print("正在載入 piexif 資料...")
        exif_dict = piexif.load(file_path)
        
        if exif_dict:
            print("✓ piexif 成功載入")
            print(f"區段數量：{len(exif_dict)}")
            print(f"區段：{list(exif_dict.keys())}")
            print()
            
            # 檢查每個區段
            for section, data in exif_dict.items():
                print(f"區段 '{section}':")
                if data:
                    if isinstance(data, dict):
                        print(f"  類型：字典，項目數：{len(data)}")
                        # 顯示前幾個項目
                        count = 0
                        for tag_id, value in data.items():
                            print(f"    {tag_id}: {type(value).__name__} = {value}")
                            count += 1
                            if count >= 5:  # 只顯示前5個
                                print(f"    ... 還有 {len(data) - 5} 個項目")
                                break
                    else:
                        print(f"  類型：{type(data).__name__} = {data}")
                else:
                    print("  空資料")
                print()
        else:
            print("✗ piexif 沒有找到 EXIF 資料")
            
    except Exception as e:
        print(f"✗ piexif 錯誤：{str(e)}")
        print(f"錯誤類型：{type(e).__name__}")
        
        # 嘗試更詳細的錯誤診斷
        try:
            import traceback
            print("\n詳細錯誤資訊：")
            traceback.print_exc()
        except:
            pass

def main():
    if len(sys.argv) != 2:
        print("使用方法：python test_piexif.py <相片檔案路徑>")
        print("範例：python test_piexif.py photo.jpg")
        sys.exit(1)
    
    file_path = sys.argv[1]
    test_piexif(file_path)

if __name__ == "__main__":
    main() 