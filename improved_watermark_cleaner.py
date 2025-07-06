#!/usr/bin/env python3
"""
改进版亚马逊狗狗图片水印清洗器
专门针对"Meet The dogs of Amazon"等水印的智能清洗
"""

import cv2
import numpy as np
import os
import json
import argparse
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedWatermarkCleaner:
    def __init__(self, input_dir="data/dogs", output_dir="data/cleaned_dogs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        
    def detect_watermark_areas(self, img):
        """智能检测水印区域"""
        height, width = img.shape[:2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 重点检查图片底部30%的区域（水印通常在这里）
        bottom_start = int(height * 0.7)
        bottom_region = gray[bottom_start:, :]
        
        watermark_regions = []
        
        # 方法1: 基于文字特征的检测
        watermark_regions.extend(self._detect_text_regions(bottom_region, bottom_start))
        
        # 方法2: 基于对比度的检测
        watermark_regions.extend(self._detect_contrast_regions(bottom_region, bottom_start))
        
        # 方法3: 基于边缘密度的检测
        watermark_regions.extend(self._detect_edge_dense_regions(bottom_region, bottom_start))
        
        # 去重并合并重叠区域
        watermark_regions = self._merge_overlapping_regions(watermark_regions)
        
        logger.info(f"检测到 {len(watermark_regions)} 个可能的水印区域")
        return watermark_regions
    
    def _detect_text_regions(self, region, y_offset):
        """检测文字区域"""
        height, width = region.shape
        text_regions = []
        
        # 使用多种阈值方法
        thresh_methods = [
            cv2.threshold(region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            cv2.threshold(region, 127, 255, cv2.THRESH_BINARY)[1],
            cv2.adaptiveThreshold(region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2),
        ]
        
        for thresh in thresh_methods:
            # 形态学操作连接文字字符
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 2))
            morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # 查找轮廓
            contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                
                # 文字区域的特征判断
                aspect_ratio = w / h if h > 0 else 0
                density = area / (w * h) if w * h > 0 else 0
                
                # 过滤条件：合理的文字尺寸和比例
                if (30 < w < width * 0.8 and 
                    8 < h < height * 0.3 and
                    1 < aspect_ratio < 15 and
                    density > 0.1 and
                    area > 200):
                    text_regions.append((x, y + y_offset, w, h))
        
        return text_regions
    
    def _detect_contrast_regions(self, region, y_offset):
        """检测高对比度区域（可能是水印）"""
        # 计算局部标准差
        kernel = np.ones((5, 5), np.float32) / 25
        region_float = region.astype(np.float32)
        mean = cv2.filter2D(region_float, -1, kernel)
        sqr_diff = (region_float - mean) ** 2
        std = np.sqrt(cv2.filter2D(sqr_diff, -1, kernel))
        
        # 高标准差区域可能是文字
        high_contrast = (std > 20).astype(np.uint8) * 255
        
        # 形态学操作
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 3))
        morphed = cv2.morphologyEx(high_contrast, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        contrast_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 10 and w < region.shape[1] * 0.8:
                contrast_regions.append((x, y + y_offset, w, h))
        
        return contrast_regions
    
    def _detect_edge_dense_regions(self, region, y_offset):
        """检测边缘密集区域"""
        # Canny边缘检测
        edges = cv2.Canny(region, 50, 150)
        
        # 膨胀操作连接边缘
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        edge_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 40 and h > 8 and w < region.shape[1] * 0.9:
                edge_regions.append((x, y + y_offset, w, h))
        
        return edge_regions
    
    def _merge_overlapping_regions(self, regions):
        """合并重叠的区域"""
        if not regions:
            return []
        
        # 去重
        unique_regions = list(set(regions))
        
        # 简单的重叠合并
        merged = []
        for x, y, w, h in unique_regions:
            overlap_found = False
            for i, (mx, my, mw, mh) in enumerate(merged):
                # 检查重叠
                if (x < mx + mw and x + w > mx and y < my + mh and y + h > my):
                    # 合并区域
                    new_x = min(x, mx)
                    new_y = min(y, my)
                    new_w = max(x + w, mx + mw) - new_x
                    new_h = max(y + h, my + mh) - new_y
                    merged[i] = (new_x, new_y, new_w, new_h)
                    overlap_found = True
                    break
            
            if not overlap_found:
                merged.append((x, y, w, h))
        
        return merged
    
    def smart_inpainting(self, img, regions):
        """智能图像修复"""
        if not regions:
            return img
        
        # 创建掩码
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        
        for x, y, w, h in regions:
            # 为水印区域创建掩码，稍微扩大边界
            padding = 3
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(img.shape[1], x + w + padding)
            y2 = min(img.shape[0], y + h + padding)
            
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
        
        # 使用Navier-Stokes算法进行修复
        try:
            result = cv2.inpaint(img, mask, 3, cv2.INPAINT_NS)
        except:
            # 如果NS算法失败，回退到Telea算法
            result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
        
        return result
    
    def enhanced_watermark_removal(self, img):
        """增强版水印移除"""
        # 1. 检测水印区域
        watermark_regions = self.detect_watermark_areas(img)
        
        if not watermark_regions:
            logger.info("未检测到水印区域")
            return img
        
        # 2. 记录检测到的区域
        for i, (x, y, w, h) in enumerate(watermark_regions):
            logger.info(f"水印区域 {i+1}: 位置({x},{y}) 尺寸{w}x{h}")
        
        # 3. 使用智能修复
        result = self.smart_inpainting(img, watermark_regions)
        
        # 4. 后处理：轻微模糊以平滑修复区域
        kernel = np.ones((3, 3), np.float32) / 9
        for x, y, w, h in watermark_regions:
            roi = result[y:y+h, x:x+w]
            blurred_roi = cv2.filter2D(roi, -1, kernel)
            result[y:y+h, x:x+w] = blurred_roi
        
        return result
    
    def process_single_image(self, input_path, output_path):
        """处理单张图片"""
        try:
            img = cv2.imread(str(input_path))
            if img is None:
                logger.error(f"无法读取图片: {input_path}")
                return False
            
            logger.info(f"处理图片: {input_path.name}")
            
            # 水印清洗
            cleaned_img = self.enhanced_watermark_removal(img)
            
            # 保存结果
            success = cv2.imwrite(str(output_path), cleaned_img)
            
            if success:
                logger.info(f"处理完成: {output_path}")
                return True
            else:
                logger.error(f"保存失败: {output_path}")
                return False
                
        except Exception as e:
            logger.error(f"处理图片时发生错误: {e}")
            return False
    
    def process_all_images(self):
        """批量处理所有图片"""
        logger.info("开始智能水印清洗...")
        
        image_files = list(self.input_dir.glob("*.jpg"))
        total_files = len(image_files)
        
        if total_files == 0:
            logger.warning("未找到图片文件")
            return
        
        logger.info(f"找到 {total_files} 张图片待处理")
        
        success_count = 0
        for i, img_file in enumerate(image_files, 1):
            output_file = self.output_dir / "images" / f"cleaned_{img_file.name}"
            
            logger.info(f"进度 [{i}/{total_files}]")
            
            if self.process_single_image(img_file, output_file):
                success_count += 1
            
            if i % 20 == 0:
                logger.info(f"已处理 {i}/{total_files} 张图片，成功 {success_count} 张")
        
        logger.info(f"批量处理完成！总计: {total_files}，成功: {success_count}")
        
        # 创建索引
        self.create_cleaned_index()
    
    def create_cleaned_index(self):
        """创建清洗后的索引文件"""
        cleaned_images = list((self.output_dir / "images").glob("cleaned_*.jpg"))
        
        index_data = {
            "total_images": len(cleaned_images),
            "description": "水印清洗后的亚马逊狗狗图片",
            "process_date": str(pd.Timestamp.now()) if 'pd' in globals() else "N/A",
            "images": []
        }
        
        for img_file in sorted(cleaned_images):
            # 提取编号
            original_name = img_file.name.replace("cleaned_", "")
            number_str = original_name.replace("dog_", "").replace(".jpg", "")
            try:
                number = int(number_str)
            except:
                number = 0
            
            index_data["images"].append({
                "number": number,
                "filename": img_file.name,
                "original_filename": original_name,
                "status": "watermark_removed"
            })
        
        index_path = self.output_dir / "cleaned_index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"清洗索引已创建: {index_path}")

def main():
    parser = argparse.ArgumentParser(description="智能水印清洗工具")
    parser.add_argument("--input", "-i", default="data/dogs", help="输入目录")
    parser.add_argument("--output", "-o", default="data/cleaned_dogs", help="输出目录")
    parser.add_argument("--single", "-s", help="处理单张图片")
    parser.add_argument("--test", "-t", action="store_true", help="测试模式（5张图片）")
    
    args = parser.parse_args()
    
    cleaner = ImprovedWatermarkCleaner(args.input, args.output)
    
    if args.single:
        input_path = Path(args.single)
        output_path = Path(args.output) / "images" / f"cleaned_{input_path.name}"
        cleaner.process_single_image(input_path, output_path)
    elif args.test:
        logger.info("测试模式：处理前5张图片")
        image_files = list(Path(args.input).glob("*.jpg"))[:5]
        for img_file in image_files:
            output_file = Path(args.output) / "images" / f"cleaned_{img_file.name}"
            cleaner.process_single_image(img_file, output_file)
    else:
        cleaner.process_all_images()

if __name__ == "__main__":
    main() 