#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相片隱藏資訊提取器 - 命令列版本
Photo Metadata Extractor - Command Line Version

使用方法:
    python photo_metadata_cli.py <相片檔案路徑>
    python photo_metadata_cli.py --help
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from PIL import Image
try:
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    # 如果無法匯入 ExifTags，使用基本字典
    TAGS = {}
    GPSTAGS = {}
import piexif
from typing import Dict, Any, Optional

class PhotoMetadataCLI:
    def __init__(self):
        self.parser = self.setup_argument_parser()
        
    def setup_argument_parser(self):
        """設定命令列參數解析器"""
        parser = argparse.ArgumentParser(
            description='相片隱藏資訊提取器 - 提取相片中的所有隱藏資訊',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
範例:
  python photo_metadata_cli.py photo.jpg
  python photo_metadata_cli.py photo.jpg --output metadata.json
  python photo_metadata_cli.py photo.jpg --gps-only
  python photo_metadata_cli.py photo.jpg --exif-only
            """
        )
        
        parser.add_argument('file_path', help='相片檔案路徑')
        parser.add_argument('-o', '--output', help='輸出 JSON 檔案路徑')
        parser.add_argument('--gps-only', action='store_true', help='只顯示 GPS 資訊')
        parser.add_argument('--exif-only', action='store_true', help='只顯示 EXIF 資訊')
        parser.add_argument('--basic-only', action='store_true', help='只顯示基本資訊')
        parser.add_argument('--raw-only', action='store_true', help='只顯示原始資料')
        parser.add_argument('--no-pretty', action='store_true', help='不使用美化格式輸出')
        parser.add_argument('--map-link', action='store_true', help='顯示 Google Maps 連結')
        
        return parser
        
    def extract_metadata(self, file_path: str) -> Dict[str, Any]:
        """提取相片的所有隱藏資訊"""
        metadata = {
            'basic_info': {},
            'exif_data': {},
            'gps_data': {},
            'raw_data': {}
        }
        
        try:
            # 檢查檔案是否存在
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"檔案不存在: {file_path}")
                
            # 基本檔案資訊
            file_path_obj = Path(file_path)
            stat = file_path_obj.stat()
            
            metadata['basic_info'] = {
                '檔案名稱': file_path_obj.name,
                '檔案路徑': str(file_path_obj.absolute()),
                '檔案大小': f"{stat.st_size:,} bytes ({self.format_size(stat.st_size)})",
                '建立時間': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                '修改時間': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
                '存取時間': datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 使用 PIL 提取 EXIF 資料
            with Image.open(file_path) as img:
                # 基本圖片資訊
                metadata['basic_info'].update({
                    '圖片格式': img.format,
                    '圖片模式': img.mode,
                    '圖片尺寸': f"{img.width} x {img.height}",
                    '圖片大小': f"{img.width * img.height:,} pixels"
                })
                
                # EXIF 資料
                if hasattr(img, '_getexif') and img._getexif():
                    exif_data = img._getexif()
                    metadata['exif_data'] = self.parse_exif_data(exif_data)
                    
                    # GPS 資料
                    if 34853 in exif_data:  # GPSInfo tag
                        gps_data = exif_data[34853]
                        metadata['gps_data'] = self.parse_gps_data(gps_data)
                        
            # 使用 piexif 提取更詳細的 EXIF 資料
            try:
                exif_dict = piexif.load(file_path)
                metadata['raw_data'] = self.parse_piexif_data(exif_dict)
            except:
                pass
                
        except Exception as e:
            metadata['error'] = str(e)
            
        return metadata
        
    def parse_exif_data(self, exif_data: Dict) -> Dict[str, Any]:
        """解析 EXIF 資料"""
        parsed_data = {}
        
        for tag_id, value in exif_data.items():
            tag_name = TAGS.get(tag_id, f"Unknown Tag {tag_id}")
            
            # 處理特殊格式的資料
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except:
                    value = str(value)
            elif isinstance(value, tuple):
                value = str(value)
                
            parsed_data[tag_name] = value
            
        return parsed_data
        
    def parse_gps_data(self, gps_data: Dict) -> Dict[str, Any]:
        """解析 GPS 資料"""
        parsed_gps = {}
        
        for tag_id, value in gps_data.items():
            tag_name = GPSTAGS.get(tag_id, f"GPS Tag {tag_id}")
            
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except:
                    value = str(value)
                    
            parsed_gps[tag_name] = value
            
        # 嘗試計算 GPS 座標
        try:
            lat = self.get_gps_coordinate(gps_data, 'GPSLatitude', 'GPSLatitudeRef')
            lon = self.get_gps_coordinate(gps_data, 'GPSLongitude', 'GPSLongitudeRef')
            
            if lat and lon:
                parsed_gps['緯度 (十進位)'] = lat
                parsed_gps['經度 (十進位)'] = lon
                parsed_gps['Google Maps 連結'] = f"https://www.google.com/maps?q={lat},{lon}"
                
        except Exception as e:
            parsed_gps['座標計算錯誤'] = str(e)
            
        return parsed_gps
        
    def get_gps_coordinate(self, gps_data: Dict, lat_key: str, ref_key: str) -> Optional[float]:
        """從 GPS 資料中提取座標"""
        try:
            if lat_key in gps_data and ref_key in gps_data:
                lat_data = gps_data[lat_key]
                ref_data = gps_data[ref_key]
                
                if isinstance(lat_data, tuple) and len(lat_data) == 3:
                    degrees = float(lat_data[0])
                    minutes = float(lat_data[1])
                    seconds = float(lat_data[2])
                    
                    coordinate = degrees + (minutes / 60.0) + (seconds / 3600.0)
                    
                    if ref_data == b'S' or ref_data == 'S':
                        coordinate = -coordinate
                    elif ref_data == b'W' or ref_data == 'W':
                        coordinate = -coordinate
                        
                    return round(coordinate, 6)
                    
        except Exception as e:
            return None
            
        return None
        
    def parse_piexif_data(self, exif_dict: Dict) -> Dict[str, Any]:
        """解析 piexif 資料"""
        parsed_data = {}
        
        for section, data in exif_dict.items():
            if data:
                parsed_data[section] = {}
                for tag_id, value in data.items():
                    if isinstance(value, bytes):
                        try:
                            value = value.decode('utf-8', errors='ignore')
                        except:
                            value = str(value)
                    parsed_data[section][str(tag_id)] = value
                    
        return parsed_data
        
    def format_size(self, size_bytes: int) -> str:
        """格式化檔案大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
    def print_metadata(self, metadata: Dict[str, Any], args):
        """印出提取的資訊"""
        print("=" * 60)
        print("相片隱藏資訊提取器 - Photo Metadata Extractor")
        print("=" * 60)
        
        # 根據參數決定要顯示哪些資訊
        if args.gps_only:
            self.print_gps_info(metadata.get('gps_data', {}))
        elif args.exif_only:
            self.print_exif_info(metadata.get('exif_data', {}))
        elif args.basic_only:
            self.print_basic_info(metadata.get('basic_info', {}))
        elif args.raw_only:
            self.print_raw_info(metadata.get('raw_data', {}))
        else:
            # 顯示所有資訊
            self.print_basic_info(metadata.get('basic_info', {}))
            print()
            self.print_exif_info(metadata.get('exif_data', {}))
            print()
            self.print_gps_info(metadata.get('gps_data', {}))
            print()
            self.print_raw_info(metadata.get('raw_data', {}))
            
        # 如果有錯誤，顯示錯誤資訊
        if 'error' in metadata:
            print("\n" + "=" * 60)
            print("錯誤資訊:")
            print(f"錯誤: {metadata['error']}")
            
    def print_basic_info(self, basic_info: Dict[str, Any]):
        """印出基本資訊"""
        print("基本檔案資訊:")
        print("-" * 30)
        for key, value in basic_info.items():
            print(f"{key}: {value}")
            
    def print_exif_info(self, exif_data: Dict[str, Any]):
        """印出 EXIF 資訊"""
        print("EXIF 資訊:")
        print("-" * 30)
        if exif_data:
            for key, value in exif_data.items():
                print(f"{key}: {value}")
        else:
            print("沒有 EXIF 資訊")
            
    def print_gps_info(self, gps_data: Dict[str, Any]):
        """印出 GPS 資訊"""
        print("GPS 資訊:")
        print("-" * 30)
        if gps_data:
            for key, value in gps_data.items():
                print(f"{key}: {value}")
        else:
            print("沒有 GPS 資訊")
            
    def print_raw_info(self, raw_data: Dict[str, Any]):
        """印出原始資料"""
        print("原始 EXIF 資料:")
        print("-" * 30)
        if raw_data:
            print(json.dumps(raw_data, indent=2, ensure_ascii=False))
        else:
            print("沒有原始資料")
            
    def save_to_json(self, metadata: Dict[str, Any], output_path: str, pretty: bool = True):
        """儲存為 JSON 檔案"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if pretty:
                    json.dump(metadata, f, indent=2, ensure_ascii=False)
                else:
                    json.dump(metadata, f, ensure_ascii=False)
            print(f"\n資料已儲存至: {output_path}")
        except Exception as e:
            print(f"\n儲存檔案時發生錯誤: {str(e)}")
            
    def run(self):
        """執行程式"""
        args = self.parser.parse_args()
        
        try:
            # 提取資訊
            metadata = self.extract_metadata(args.file_path)
            
            # 顯示資訊
            self.print_metadata(metadata, args)
            
            # 如果指定了輸出檔案，儲存為 JSON
            if args.output:
                self.save_to_json(metadata, args.output, not args.no_pretty)
                
        except Exception as e:
            print(f"錯誤: {str(e)}")
            sys.exit(1)

def main():
    """主程式"""
    cli = PhotoMetadataCLI()
    cli.run()

if __name__ == "__main__":
    main() 