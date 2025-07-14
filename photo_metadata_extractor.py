#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
相片隱藏資訊提取器
Photo Metadata Extractor

這個腳本可以提取相片中的所有隱藏資訊，包括：
- EXIF 資料（相機設定、拍攝時間等）
- GPS 資訊（位置座標）
- IPTC 資料（版權、描述等）
- 基本檔案資訊（大小、格式等）
"""

import os
import sys
import json
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
try:
    from PIL.ExifTags import TAGS, GPSTAGS
except ImportError:
    # 如果無法匯入 ExifTags，使用基本字典
    TAGS = {}
    GPSTAGS = {}
import piexif
import webbrowser
from typing import Dict, Any, Optional, List

class PhotoMetadataExtractor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("相片抓包器 - Photo Metadata Extractor")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # 設定樣式
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
        
    def setup_ui(self):
        """設定使用者介面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 賽博風格配色
        cyber_bg = '#0D0D0D'  # 深黑色
        cyber_fg = '#00FFFF'  # 青色
        cyber_entry_bg = '#1A1A1A'
        cyber_entry_fg = '#00FFFF'
        cyber_btn_bg = '#333333'
        cyber_btn_fg = '#00FFFF'
        cyber_tab_bg = '#1A1A1A'
        cyber_tab_fg = '#00FFFF'

        self.root.configure(bg=cyber_bg)
        main_frame.configure(style='Cyber.TFrame')

        # 標題
        title_label = ttk.Label(main_frame, text="相片抓包器-Power by GXTRO", style='Cyber.TLabel', font=('Consolas', 18, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 檔案選擇區域
        file_frame = ttk.LabelFrame(main_frame, text="檔案選擇", padding="10", style='Cyber.TLabelframe')
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.file_path_var = tk.StringVar()
        file_entry = tk.Entry(file_frame, textvariable=self.file_path_var, width=60, bg=cyber_entry_bg, fg=cyber_entry_fg, insertbackground=cyber_fg, font=('Consolas', 11))
        file_entry.grid(row=0, column=0, padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="瀏覽檔案", command=self.browse_file, style='Cyber.TButton')
        browse_btn.grid(row=0, column=1, padx=(0, 10))
        
        extract_btn = ttk.Button(file_frame, text="提取資訊", command=self.extract_metadata, style='Cyber.TButton')
        extract_btn.grid(row=0, column=2)
        
        # 預覽區域
        preview_frame = ttk.LabelFrame(main_frame, text="相片預覽", padding="10", style='Cyber.TLabelframe')
        preview_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        self.preview_label = ttk.Label(preview_frame, text="選擇相片檔案以顯示預覽", style='Cyber.TLabel', font=('Consolas', 11))
        self.preview_label.grid(row=0, column=0)
        
        # 資訊顯示區域
        info_frame = ttk.LabelFrame(main_frame, text="隱藏資訊", padding="10", style='Cyber.TLabelframe')
        info_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 建立 Notebook 用於分頁顯示
        self.notebook = ttk.Notebook(info_frame, style='Cyber.TNotebook')
        self.notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # EXIF 資訊分頁
        self.exif_frame = ttk.Frame(self.notebook, style='Cyber.TFrame')
        self.notebook.add(self.exif_frame, text="EXIF 資訊")
        
        self.exif_text = scrolledtext.ScrolledText(self.exif_frame, width=60, height=20, bg=cyber_bg, fg=cyber_fg, insertbackground=cyber_fg, font=('Consolas', 11))
        self.exif_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # GPS 資訊分頁
        self.gps_frame = ttk.Frame(self.notebook, style='Cyber.TFrame')
        self.notebook.add(self.gps_frame, text="GPS 資訊")
        
        self.gps_text = scrolledtext.ScrolledText(self.gps_frame, width=60, height=20, bg=cyber_bg, fg=cyber_fg, insertbackground=cyber_fg, font=('Consolas', 11))
        self.gps_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 基本資訊分頁
        self.basic_frame = ttk.Frame(self.notebook, style='Cyber.TFrame')
        self.notebook.add(self.basic_frame, text="基本資訊")
        
        self.basic_text = scrolledtext.ScrolledText(self.basic_frame, width=60, height=20, bg=cyber_bg, fg=cyber_fg, insertbackground=cyber_fg, font=('Consolas', 11))
        self.basic_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 原始資料分頁
        self.raw_frame = ttk.Frame(self.notebook, style='Cyber.TFrame')
        self.notebook.add(self.raw_frame, text="原始資料")
        
        self.raw_text = scrolledtext.ScrolledText(self.raw_frame, width=60, height=20, bg=cyber_bg, fg=cyber_fg, insertbackground=cyber_fg, font=('Consolas', 11))
        self.raw_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 診斷資訊分頁
        self.diagnostic_frame = ttk.Frame(self.notebook, style='Cyber.TFrame')
        self.notebook.add(self.diagnostic_frame, text="診斷資訊")
        
        self.diagnostic_text = scrolledtext.ScrolledText(self.diagnostic_frame, width=60, height=20, bg=cyber_bg, fg=cyber_fg, insertbackground=cyber_fg, font=('Consolas', 11))
        self.diagnostic_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 按鈕區域
        button_frame = ttk.Frame(main_frame, style='Cyber.TFrame')
        button_frame.grid(row=3, column=0, columnspan=3, pady=(20, 0))
        
        save_btn = ttk.Button(button_frame, text="儲存為 JSON", command=self.save_to_json, style='Cyber.TButton')
        save_btn.grid(row=0, column=0, padx=(0, 10))
        
        map_btn = ttk.Button(button_frame, text="在地圖中查看", command=self.open_in_map, style='Cyber.TButton')
        map_btn.grid(row=0, column=1, padx=(0, 10))
        
        clear_btn = ttk.Button(button_frame, text="清除", command=self.clear_all, style='Cyber.TButton')
        clear_btn.grid(row=0, column=2)
        
        # 設定網格權重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(2, weight=1)
        info_frame.columnconfigure(0, weight=1)
        info_frame.rowconfigure(0, weight=1)
        self.exif_frame.columnconfigure(0, weight=1)
        self.exif_frame.rowconfigure(0, weight=1)
        self.gps_frame.columnconfigure(0, weight=1)
        self.gps_frame.rowconfigure(0, weight=1)
        self.basic_frame.columnconfigure(0, weight=1)
        self.basic_frame.rowconfigure(0, weight=1)
        self.raw_frame.columnconfigure(0, weight=1)
        self.raw_frame.rowconfigure(0, weight=1)
        self.diagnostic_frame.columnconfigure(0, weight=1)
        self.diagnostic_frame.rowconfigure(0, weight=1)
        
        # 儲存資料
        self.current_metadata = {}
        self.current_file_path = ""
        
    def browse_file(self):
        """瀏覽並選擇相片檔案"""
        file_types = [
            ('圖片檔案', '*.jpg *.jpeg *.png *.bmp *.tiff *.tif *.gif *.webp'),
            ('JPEG 檔案', '*.jpg *.jpeg'),
            ('PNG 檔案', '*.png'),
            ('所有檔案', '*.*')
        ]
        
        filename = filedialog.askopenfilename(
            title="選擇相片檔案",
            filetypes=file_types
        )
        
        if filename:
            self.file_path_var.set(filename)
            self.current_file_path = filename
            self.load_preview()
            
    def load_preview(self):
        """載入相片預覽"""
        try:
            # 載入圖片
            image = Image.open(self.current_file_path)
            
            # 調整大小以適應預覽區域
            max_size = (300, 300)
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # 轉換為 Tkinter 可用的格式
            photo = ImageTk.PhotoImage(image)
            
            # 更新預覽標籤
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo  # 保持參考
            
        except Exception as e:
            self.preview_label.configure(text=f"無法載入預覽: {str(e)}")
            
    def extract_metadata(self):
        """提取相片的隱藏資訊"""
        if not self.current_file_path:
            messagebox.showwarning("警告", "請先選擇相片檔案")
            return
            
        try:
            # 清空之前的資料
            self.clear_text_widgets()
            
            # 提取所有資訊
            self.current_metadata = self.get_all_metadata(self.current_file_path)
            
            # 顯示資訊
            self.display_metadata()
            
        except Exception as e:
            messagebox.showerror("錯誤", f"提取資訊時發生錯誤: {str(e)}")
            
    def get_all_metadata(self, file_path: str) -> Dict[str, Any]:
        """獲取相片的所有隱藏資訊"""
        metadata = {
            'basic_info': {},
            'exif_data': {},
            'gps_data': {},
            'raw_data': {},
            'diagnostic_info': {}
        }
        
        try:
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
            
            # 診斷資訊
            diagnostic_info = {}
            
            # 使用 PIL 提取 EXIF 資料
            with Image.open(file_path) as img:
                # 基本圖片資訊
                metadata['basic_info'].update({
                    '圖片格式': img.format,
                    '圖片模式': img.mode,
                    '圖片尺寸': f"{img.width} x {img.height}",
                    '圖片大小': f"{img.width * img.height:,} pixels"
                })
                
                # 檢查 EXIF 支援
                diagnostic_info['PIL_has_exif_support'] = hasattr(img, '_getexif')
                
                # EXIF 資料
                if hasattr(img, '_getexif'):
                    exif_data = img._getexif()
                    diagnostic_info['exif_data_found'] = exif_data is not None
                    diagnostic_info['exif_tags_count'] = len(exif_data) if exif_data else 0
                    
                    if exif_data:
                        metadata['exif_data'] = self.parse_exif_data(exif_data)
                        
                        # GPS 資料
                        if 34853 in exif_data:  # GPSInfo tag
                            gps_data = exif_data[34853]
                            metadata['gps_data'] = self.parse_gps_data(gps_data)
                            diagnostic_info['gps_data_found'] = True
                        else:
                            diagnostic_info['gps_data_found'] = False
                    else:
                        diagnostic_info['gps_data_found'] = False
                else:
                    diagnostic_info['exif_data_found'] = False
                    diagnostic_info['exif_tags_count'] = 0
                    diagnostic_info['gps_data_found'] = False
                        
            # 使用 piexif 提取更詳細的 EXIF 資料
            try:
                exif_dict = piexif.load(file_path)
                if exif_dict and isinstance(exif_dict, dict):
                    metadata['raw_data'] = self.parse_piexif_data(exif_dict)
                    diagnostic_info['piexif_success'] = True
                    diagnostic_info['piexif_sections'] = list(exif_dict.keys()) if exif_dict else []
                    
                    # 嘗試從 piexif 提取 GPS 資料
                    if 'GPS' in exif_dict and exif_dict['GPS'] and isinstance(exif_dict['GPS'], dict):
                        gps_data = exif_dict['GPS']
                        if not metadata.get('gps_data'):  # 如果 PIL 沒有找到 GPS
                            metadata['gps_data'] = self.parse_piexif_gps_data(gps_data)
                            diagnostic_info['gps_data_found'] = True
                            diagnostic_info['gps_source'] = 'piexif'
                else:
                    diagnostic_info['piexif_success'] = False
                    diagnostic_info['piexif_error'] = 'piexif 返回空資料或非字典格式'
                        
            except Exception as e:
                diagnostic_info['piexif_success'] = False
                diagnostic_info['piexif_error'] = str(e)
                
            # 嘗試其他方法提取資料
            try:
                # 檢查檔案頭部是否有 EXIF 標記
                with open(file_path, 'rb') as f:
                    header = f.read(20)
                    diagnostic_info['file_header'] = header.hex()[:40]
                    
                    # 檢查 JPEG EXIF 標記
                    if b'\xff\xe1' in header:
                        diagnostic_info['jpeg_exif_marker'] = True
                    else:
                        diagnostic_info['jpeg_exif_marker'] = False
            except Exception as e:
                diagnostic_info['header_check_error'] = str(e)
                
            metadata['diagnostic_info'] = diagnostic_info
                
        except Exception as e:
            metadata['error'] = str(e)
            
        return metadata
        
    def parse_exif_data(self, exif_data: Dict) -> Dict[str, Any]:
        """解析 EXIF 資料"""
        parsed_data = {}
        
        # 重要且易讀的標籤對應
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
            42036: '鏡頭型號',
            256: '圖片寬度',
            257: '圖片高度',
            274: '方向',
            296: '解析度單位',
            282: 'X 解析度',
            283: 'Y 解析度',
            531: 'YCbCr 定位',
            34665: 'EXIF 偏移',
            36864: 'EXIF 版本',
            40960: 'FlashPix 版本',
            40961: '色彩空間',
            40962: '像素 X 維度',
            40963: '像素 Y 維度',
            40965: '互通性 IFD 指標',
            36880: '時區偏移',
            36881: '原始時區偏移',
            36868: '數位化時間',
            37378: '曝光程式',
            37379: '光譜敏感度',
            37381: '光電轉換函數',
            37382: 'EXIF 版本',
            37383: '原始日期時間',
            37384: '數位化日期時間',
            37385: '元件配置',
            37386: '壓縮位元數',
            37388: '光圈值',
            37389: '亮度值',
            37390: '曝光偏差值',
            37391: '最大光圈值',
            37392: '主體距離',
            37393: '測光模式',
            37394: '光源',
            37398: '製造商註記',
            37399: '使用者註記',
            37400: '子秒時間',
            37401: '原始子秒時間',
            37402: '數位化子秒時間',
            37500: 'FlashPix 版本',
            37510: '色彩空間',
            37520: '像素 X 維度',
            37521: '像素 Y 維度',
            37522: '相關音訊檔案',
            41483: '閃光燈',
            41484: '閃光燈返回光',
            41485: '閃光燈模式',
            41486: '閃光燈功能',
            41487: '閃光燈紅眼模式',
            41488: '閃光燈曝光補償',
            41492: '閃光燈來源',
            41493: '閃光燈狀態',
            41494: '閃光燈模式',
            41985: '自訂渲染',
            41986: '曝光模式',
            41988: '數位變焦比例',
            41989: '35mm 膠片焦距',
            41991: '增益控制',
            41995: '裝置設定描述',
            41996: '主體距離範圍',
            42016: '影像唯一 ID',
            42032: '相機擁有者名稱',
            42033: '機身序號',
            42034: '鏡頭規格',
            42035: '鏡頭品牌',
            42036: '鏡頭型號',
            42037: '鏡頭序號'
        }
        
        for tag_id, value in exif_data.items():
            if tag_id in important_tags:
                tag_name = important_tags[tag_id]
                
                # 格式化數值
                if tag_id == 37377:  # 光圈值
                    if isinstance(value, tuple) and len(value) == 2:
                        value = f"f/{value[0]/value[1]:.1f}"
                    else:
                        value = f"f/{value/100}" if value > 0 else str(value)
                elif tag_id == 37387:  # 快門速度
                    if isinstance(value, tuple) and len(value) == 2:
                        value = f"1/{int(value[0]/value[1])}s"
                    else:
                        value = f"1/{int(2**value)}s" if value > 0 else str(value)
                elif tag_id == 37396:  # 焦距
                    value = f"{value}mm"
                elif tag_id == 37380:  # ISO
                    if isinstance(value, tuple) and len(value) == 2:
                        value = f"ISO {value[0]}"
                    else:
                        value = f"ISO {value}"
                elif tag_id == 37395:  # 閃光燈
                    flash_values = {
                        0: "未使用", 1: "使用", 9: "強制使用", 16: "關閉",
                        24: "未使用，自動模式", 25: "使用，自動模式",
                        32: "未使用，無閃光燈功能", 65: "使用，紅眼減少",
                        73: "強制使用，紅眼減少", 89: "使用，自動模式，紅眼減少"
                    }
                    value = flash_values.get(value, str(value))
                elif tag_id == 41987:  # 白平衡
                    wb_values = {0: "自動", 1: "手動"}
                    value = wb_values.get(value, str(value))
                elif tag_id == 41990:  # 場景模式
                    scene_values = {0: "標準", 1: "風景", 2: "人像", 3: "夜景"}
                    value = scene_values.get(value, str(value))
                elif tag_id == 41992:  # 對比度
                    contrast_values = {0: "正常", 1: "柔和", 2: "強烈"}
                    value = contrast_values.get(value, str(value))
                elif tag_id == 41993:  # 飽和度
                    saturation_values = {0: "正常", 1: "低飽和度", 2: "高飽和度"}
                    value = saturation_values.get(value, str(value))
                elif tag_id == 41994:  # 銳利度
                    sharpness_values = {0: "正常", 1: "柔和", 2: "強烈"}
                    value = sharpness_values.get(value, str(value))
                elif tag_id == 274:  # 方向
                    orientation_values = {
                        1: "正常", 2: "水平翻轉", 3: "旋轉180度",
                        4: "垂直翻轉", 5: "水平翻轉+順時針90度",
                        6: "順時針90度", 7: "水平翻轉+逆時針90度",
                        8: "逆時針90度"
                    }
                    value = orientation_values.get(value, str(value))
                elif tag_id == 296:  # 解析度單位
                    unit_values = {1: "無", 2: "英寸", 3: "公分"}
                    value = unit_values.get(value, str(value))
                elif isinstance(value, bytes):
                    try:
                        # 嘗試不同的編碼
                        for encoding in ['utf-8', 'latin-1', 'cp1252', 'gbk']:
                            try:
                                decoded_value = value.decode(encoding)
                                if decoded_value and decoded_value.isprintable():
                                    value = decoded_value
                                    break
                            except:
                                continue
                        else:
                            # 如果所有編碼都失敗，跳過這個標籤
                            continue
                    except:
                        continue
                elif isinstance(value, tuple):
                    # 處理座標等特殊格式
                    if len(value) == 3 and all(isinstance(x, (int, float)) for x in value):
                        value = f"({value[0]}, {value[1]}, {value[2]})"
                    elif len(value) == 2 and all(isinstance(x, (int, float)) for x in value):
                        value = f"({value[0]}, {value[1]})"
                    else:
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
            # 強制產生欄位
            parsed_gps['緯度 (十進位)'] = lat
            parsed_gps['經度 (十進位)'] = lon
            if lat is not None and lon is not None:
                parsed_gps['Google Maps 連結'] = f"https://www.google.com/maps?q={lat},{lon}"
        except Exception as e:
            parsed_gps['座標計算錯誤'] = str(e)

        # 額外顯示所有可能的經緯度欄位
        for key in ['GPSLatitude', 'GPSLongitude', 'GPSDestLatitude', 'GPSDestLongitude']:
            if key in gps_data:
                parsed_gps[f'{key} (原始)'] = gps_data[key]

        return parsed_gps
        
    def get_gps_coordinate(self, gps_data: Dict, lat_key: str, ref_key: str) -> Optional[float]:
        try:
            # 支援字串與數字 key
            lat_data = gps_data.get(lat_key)
            if lat_data is None:
                # 嘗試數字 key
                key_map = {
                    'GPSLatitude': 2,
                    'GPSLatitudeRef': 1,
                    'GPSLongitude': 4,
                    'GPSLongitudeRef': 3
                }
                lat_data = gps_data.get(key_map.get(lat_key))
                ref_data = gps_data.get(ref_key) or gps_data.get(key_map.get(ref_key))
            else:
                ref_data = gps_data.get(ref_key)
            if lat_data is None:
                return None
            if ref_data in [None, '', b'']:
                ref_data = 'N' if 'Lat' in lat_key else 'E'
            # 處理 tuple/list of float 或 rational
            if isinstance(lat_data, (tuple, list)) and len(lat_data) == 3:
                # rational 格式
                if all(isinstance(v, (tuple, list)) and len(v) == 2 for v in lat_data):
                    def rational_to_float(x):
                        return float(x[0]) / float(x[1]) if x[1] != 0 else 0
                    degrees = rational_to_float(lat_data[0])
                    minutes = rational_to_float(lat_data[1])
                    seconds = rational_to_float(lat_data[2])
                else:
                    degrees = float(lat_data[0])
                    minutes = float(lat_data[1])
                    seconds = float(lat_data[2])
                coordinate = degrees + (minutes / 60.0) + (seconds / 3600.0)
                if isinstance(ref_data, bytes):
                    ref_data = ref_data.decode('utf-8', errors='ignore')
                if ref_data in ['S', 'W']:
                    coordinate = -coordinate
                return round(coordinate, 8)
            elif isinstance(lat_data, float):
                return lat_data
        except Exception as e:
            print(f"GPS 解析錯誤: {e}")
            return None
        return None
        
    def parse_piexif_data(self, exif_dict: Dict) -> Dict[str, Any]:
        """解析 piexif 資料"""
        parsed_data = {}
        
        if not exif_dict:
            return parsed_data
            
        for section, data in exif_dict.items():
            if data and isinstance(data, dict):
                parsed_data[section] = {}
                for tag_id, value in data.items():
                    if isinstance(value, bytes):
                        try:
                            # 嘗試不同的編碼
                            for encoding in ['utf-8', 'latin-1', 'cp1252', 'gbk']:
                                try:
                                    decoded_value = value.decode(encoding)
                                    if decoded_value and decoded_value.isprintable():
                                        value = decoded_value
                                        break
                                except:
                                    continue
                            else:
                                # 如果所有編碼都失敗，顯示十六進制
                                value = f"[HEX] {value.hex()}"
                        except:
                            value = str(value)
                    elif isinstance(value, tuple):
                        # 處理座標等特殊格式
                        if len(value) == 3 and all(isinstance(x, (int, float)) for x in value):
                            value = f"({value[0]}, {value[1]}, {value[2]})"
                        else:
                            value = str(value)
                    parsed_data[section][str(tag_id)] = value
            elif data:
                # 如果 data 不是字典，直接儲存
                parsed_data[section] = str(data)
                    
        return parsed_data
        
    def parse_piexif_gps_data(self, gps_data: Dict) -> Dict[str, Any]:
        """解析 piexif GPS 資料"""
        parsed_gps = {}
        
        # piexif GPS 標籤對應
        gps_tags = {
            0: 'GPSVersionID',
            1: 'GPSLatitudeRef',
            2: 'GPSLatitude',
            3: 'GPSLongitudeRef',
            4: 'GPSLongitude',
            5: 'GPSAltitudeRef',
            6: 'GPSAltitude',
            7: 'GPSTimeStamp',
            8: 'GPSSatellites',
            9: 'GPSStatus',
            10: 'GPSMeasureMode',
            11: 'GPSDOP',
            12: 'GPSSpeedRef',
            13: 'GPSSpeed',
            14: 'GPSTrackRef',
            15: 'GPSTrack',
            16: 'GPSImgDirectionRef',
            17: 'GPSImgDirection',
            18: 'GPSMapDatum',
            19: 'GPSDestLatitudeRef',
            20: 'GPSDestLatitude',
            21: 'GPSDestLongitudeRef',
            22: 'GPSDestLongitude',
            23: 'GPSDestBearingRef',
            24: 'GPSDestBearing',
            25: 'GPSDestDistanceRef',
            26: 'GPSDestDistance',
            27: 'GPSProcessingMethod',
            28: 'GPSAreaInformation',
            29: 'GPSDateStamp',
            30: 'GPSDifferential'
        }
        
        for tag_id, value in gps_data.items():
            tag_name = gps_tags.get(tag_id, f"GPS Tag {tag_id}")
            
            if isinstance(value, bytes):
                try:
                    value = value.decode('utf-8', errors='ignore')
                except:
                    value = str(value)
                    
            parsed_gps[tag_name] = value
            
        # 嘗試計算 GPS 座標
        try:
            lat = self.get_piexif_gps_coordinate(gps_data, 2, 1)  # GPSLatitude, GPSLatitudeRef
            lon = self.get_piexif_gps_coordinate(gps_data, 4, 3)  # GPSLongitude, GPSLongitudeRef
            
            if lat and lon:
                parsed_gps['緯度 (十進位)'] = lat
                parsed_gps['經度 (十進位)'] = lon
                parsed_gps['Google Maps 連結'] = f"https://www.google.com/maps?q={lat},{lon}"
                
        except Exception as e:
            parsed_gps['座標計算錯誤'] = str(e)
            
        return parsed_gps
        
    def get_piexif_gps_coordinate(self, gps_data: Dict, coord_key: int, ref_key: int) -> Optional[float]:
        """從 piexif GPS 資料中提取座標"""
        try:
            if coord_key in gps_data and ref_key in gps_data:
                coord_data = gps_data[coord_key]
                ref_data = gps_data[ref_key]
                
                if isinstance(coord_data, tuple) and len(coord_data) == 3:
                    degrees = float(coord_data[0])
                    minutes = float(coord_data[1])
                    seconds = float(coord_data[2])
                    
                    coordinate = degrees + (minutes / 60.0) + (seconds / 3600.0)
                    
                    if isinstance(ref_data, bytes):
                        ref_data = ref_data.decode('utf-8', errors='ignore')
                    
                    if ref_data == 'S' or ref_data == 'W':
                        coordinate = -coordinate
                        
                    return round(coordinate, 6)
                    
        except Exception as e:
            return None
            
        return None
        
    def format_size(self, size_bytes: int) -> str:
        """格式化檔案大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
        
    def display_metadata(self):
        """顯示提取的資訊"""
        # 顯示基本資訊
        basic_info = self.current_metadata.get('basic_info', {})
        basic_text = "基本檔案資訊:\n" + "="*50 + "\n"
        for key, value in basic_info.items():
            basic_text += f"{key}: {value}\n"
        self.basic_text.insert(tk.END, basic_text)
        
        # 顯示 EXIF 資訊
        exif_data = self.current_metadata.get('exif_data', {})
        exif_text = "EXIF 資訊:\n" + "="*50 + "\n"
        for key, value in exif_data.items():
            exif_text += f"{key}: {value}\n"
        self.exif_text.insert(tk.END, exif_text)
        
        # 顯示 GPS 資訊
        gps_data = self.current_metadata.get('gps_data', {})
        gps_text = "GPS 資訊:\n" + "="*50 + "\n"
        for key, value in gps_data.items():
            gps_text += f"{key}: {value}\n"
        self.gps_text.insert(tk.END, gps_text)
        
        # 顯示原始資料
        raw_data = self.current_metadata.get('raw_data', {})
        raw_text = "原始 EXIF 資料:\n" + "="*50 + "\n"
        raw_text += json.dumps(raw_data, indent=2, ensure_ascii=False)
        self.raw_text.insert(tk.END, raw_text)
        
        # 顯示診斷資訊
        diagnostic_info = self.current_metadata.get('diagnostic_info', {})
        diagnostic_text = "診斷資訊:\n" + "="*50 + "\n"
        
        # 基本診斷
        diagnostic_text += f"PIL EXIF 支援: {diagnostic_info.get('PIL_has_exif_support', 'Unknown')}\n"
        diagnostic_text += f"發現 EXIF 資料: {diagnostic_info.get('exif_data_found', 'Unknown')}\n"
        diagnostic_text += f"EXIF 標籤數量: {diagnostic_info.get('exif_tags_count', 0)}\n"
        diagnostic_text += f"發現 GPS 資料: {diagnostic_info.get('gps_data_found', 'Unknown')}\n"
        if 'gps_source' in diagnostic_info:
            diagnostic_text += f"GPS 資料來源: {diagnostic_info.get('gps_source', 'Unknown')}\n"
        diagnostic_text += f"piexif 成功: {diagnostic_info.get('piexif_success', 'Unknown')}\n"
        
        # 檔案頭部檢查
        if 'jpeg_exif_marker' in diagnostic_info:
            diagnostic_text += f"JPEG EXIF 標記: {diagnostic_info.get('jpeg_exif_marker', 'Unknown')}\n"
        
        if 'file_header' in diagnostic_info:
            diagnostic_text += f"檔案頭部: {diagnostic_info.get('file_header', 'Unknown')}\n"
        
        # piexif 詳細資訊
        if diagnostic_info.get('piexif_success'):
            sections = diagnostic_info.get('piexif_sections', [])
            diagnostic_text += f"piexif 區段: {sections}\n"
        elif 'piexif_error' in diagnostic_info:
            diagnostic_text += f"piexif 錯誤: {diagnostic_info.get('piexif_error')}\n"
        
        # 建議
        diagnostic_text += "\n" + "="*50 + "\n"
        diagnostic_text += "建議:\n"
        
        if not diagnostic_info.get('exif_data_found'):
            diagnostic_text += "• 此相片可能沒有 EXIF 資料\n"
            diagnostic_text += "• 可能是截圖或從網頁下載的圖片\n"
            diagnostic_text += "• 可能經過編輯軟體處理，EXIF 被移除\n"
            diagnostic_text += "• 建議使用原始相機拍攝的相片\n"
        
        if not diagnostic_info.get('gps_data_found') and diagnostic_info.get('exif_data_found'):
            diagnostic_text += "• 相片有 EXIF 資料但沒有 GPS 資訊\n"
            diagnostic_text += "• 可能拍攝時沒有啟用位置服務\n"
            diagnostic_text += "• 或 GPS 資料被手動移除\n"
        
        if diagnostic_info.get('exif_data_found'):
            diagnostic_text += "• 相片包含 EXIF 資料，可以正常提取\n"
        
        self.diagnostic_text.insert(tk.END, diagnostic_text)
        
    def clear_text_widgets(self):
        """清空所有文字顯示區域"""
        self.exif_text.delete(1.0, tk.END)
        self.gps_text.delete(1.0, tk.END)
        self.basic_text.delete(1.0, tk.END)
        self.raw_text.delete(1.0, tk.END)
        self.diagnostic_text.delete(1.0, tk.END)
        
    def save_to_json(self):
        """將資訊儲存為 JSON 檔案"""
        if not self.current_metadata:
            messagebox.showwarning("警告", "沒有可儲存的資料")
            return
            
        filename = filedialog.asksaveasfilename(
            title="儲存 JSON 檔案",
            defaultextension=".json",
            filetypes=[('JSON 檔案', '*.json'), ('所有檔案', '*.*')]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.current_metadata, f, indent=2, ensure_ascii=False)
                messagebox.showinfo("成功", f"資料已儲存至: {filename}")
            except Exception as e:
                messagebox.showerror("錯誤", f"儲存檔案時發生錯誤: {str(e)}")
                
    def open_in_map(self):
        """在地圖中開啟 GPS 位置"""
        gps_data = self.current_metadata.get('gps_data', {})
        maps_link = gps_data.get('Google Maps 連結')
        lat = gps_data.get('緯度 (十進位)')
        lon = gps_data.get('經度 (十進位)')
        print("DEBUG: maps_link =", maps_link)
        print("DEBUG: lat =", lat, "lon =", lon)
        if not maps_link and lat is not None and lon is not None:
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            print("DEBUG: generated maps_link =", maps_link)
        if maps_link:
            try:
                print("DEBUG: opening browser with", maps_link)
                webbrowser.open(maps_link)
            except Exception as e:
                messagebox.showerror("錯誤", f"無法開啟地圖: {str(e)}")
        else:
            messagebox.showinfo("資訊", f"此相片沒有 GPS 位置資訊\nDEBUG: {lat}, {lon}, {gps_data}")
            
    def clear_all(self):
        """清除所有資料"""
        self.file_path_var.set("")
        self.current_file_path = ""
        self.current_metadata = {}
        self.clear_text_widgets()
        self.preview_label.configure(image="", text="選擇相片檔案以顯示預覽")
        
    def run(self):
        """執行程式"""
        self.root.mainloop()

def main():
    """主程式"""
    try:
        app = PhotoMetadataExtractor()
        app.run()
    except Exception as e:
        print(f"程式執行錯誤: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 