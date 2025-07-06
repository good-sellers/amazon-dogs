#!/usr/bin/env python3
"""
Amazon Dogs Image Watermark Cleaner
清洗亚马逊狗狗图片中的水印，保留狗狗名字，去掉广告文字
"""

import cv2
import numpy as np
import os
import json
from PIL import Image, ImageDraw, ImageFont
import argparse
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WatermarkCleaner:
    def __init__(self, input_dir="data/dogs", output_dir="data/cleaned_dogs"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建保存清洗后图片的目录
        (self.output_dir / "images").mkdir(exist_ok=True)
        
    def analyze_image(self, image_path):
        """分析图片结构，查找水印位置"""
        img = cv2.imread(str(image_path))
        if img is None:
            logger.error(f"无法读取图片: {image_path}")
            return None
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        height, width = gray.shape
        
        logger.info(f"图片尺寸: {width}x{height}")
        
        # 通常水印在图片底部，分析底部区域
        bottom_region = gray[int(height * 0.7):, :]
        
        # 使用边缘检测找到文字区域
        edges = cv2.Canny(bottom_region, 50, 150)
        
        # 查找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 分析轮廓，找到可能的文字区域
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 10:  # 过滤掉太小的区域
                # 调整y坐标到原图坐标系
                y += int(height * 0.7)
                text_regions.append((x, y, w, h))
        
        return {
            'width': width,
            'height': height,
            'text_regions': text_regions
        }
    
    def detect_watermark_region(self, img):
        """检测水印区域"""
        height, width = img.shape[:2]
        
        # 转换为灰度图
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 重点检查图片底部区域（通常水印在这里）
        bottom_third = gray[int(height * 0.6):, :]
        
        # 使用模板匹配或文字检测
        # 这里我们假设水印是白色文字在深色背景上，或者相反
        
        # 查找文字可能的区域（高对比度区域）
        _, thresh = cv2.threshold(bottom_third, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 形态学操作连接文字
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (10, 3))
        morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(morphed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        watermark_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            # 调整y坐标
            y += int(height * 0.6)
            
            # 过滤条件：足够大的文字区域
            if w > 100 and h > 15 and w < width * 0.8:
                watermark_regions.append((x, y, w, h))
        
        return watermark_regions
    
    def inpaint_watermark(self, img, regions):
        """使用图像修复技术去除水印"""
        # 创建掩码
        mask = np.zeros(img.shape[:2], dtype=np.uint8)
        
        for x, y, w, h in regions:
            # 为每个水印区域创建掩码
            cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)
            
            # 扩展掩码边缘以确保完全覆盖
            cv2.rectangle(mask, (x-2, y-2), (x + w + 2, y + h + 2), 255, -1)
        
        # 使用Telea算法进行图像修复
        result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
        
        return result, mask
    
    def smart_watermark_removal(self, img):
        """智能水印去除"""
        height, width = img.shape[:2]
        
        # 1. 检测图片底部的文字区域
        watermark_regions = self.detect_watermark_region(img)
        
        if not watermark_regions:
            logger.info("未检测到明显的水印区域")
            return img
        
        logger.info(f"检测到 {len(watermark_regions)} 个可能的水印区域")
        
        # 2. 使用图像修复去除水印
        cleaned_img, mask = self.inpaint_watermark(img, watermark_regions)
        
        return cleaned_img
    
    def process_single_image(self, input_path, output_path):
        """处理单张图片"""
        try:
            # 读取图片
            img = cv2.imread(str(input_path))
            if img is None:
                logger.error(f"无法读取图片: {input_path}")
                return False
            
            logger.info(f"处理图片: {input_path.name}")
            
            # 分析图片
            analysis = self.analyze_image(input_path)
            if analysis:
                logger.info(f"图片分析完成，发现 {len(analysis['text_regions'])} 个文字区域")
            
            # 清洗水印
            cleaned_img = self.smart_watermark_removal(img)
            
            # 保存清洗后的图片
            success = cv2.imwrite(str(output_path), cleaned_img)
            
            if success:
                logger.info(f"清洗完成，保存到: {output_path}")
                return True
            else:
                logger.error(f"保存失败: {output_path}")
                return False
                
        except Exception as e:
            logger.error(f"处理图片时发生错误: {e}")
            return False
    
    def process_all_images(self):
        """批量处理所有图片"""
        logger.info("开始批量清洗图片水印...")
        
        # 获取所有jpg图片
        image_files = list(self.input_dir.glob("*.jpg"))
        total_files = len(image_files)
        
        if total_files == 0:
            logger.warning("未找到需要处理的图片文件")
            return
        
        logger.info(f"找到 {total_files} 张图片待处理")
        
        success_count = 0
        for i, img_file in enumerate(image_files, 1):
            output_file = self.output_dir / "images" / f"cleaned_{img_file.name}"
            
            logger.info(f"进度 [{i}/{total_files}] - 处理: {img_file.name}")
            
            if self.process_single_image(img_file, output_file):
                success_count += 1
            
            # 每处理10张图片显示一次进度
            if i % 10 == 0:
                logger.info(f"已处理 {i}/{total_files} 张图片，成功 {success_count} 张")
        
        logger.info(f"批量处理完成！总计: {total_files}，成功: {success_count}")
        
        # 创建清洗后的索引文件
        self.create_cleaned_index(success_count)
    
    def create_cleaned_index(self, count):
        """为清洗后的图片创建索引文件"""
        index_data = {
            "total_images": count,
            "description": "清洗水印后的亚马逊狗狗图片",
            "images": []
        }
        
        # 扫描清洗后的图片目录
        cleaned_images = list((self.output_dir / "images").glob("cleaned_*.jpg"))
        
        for img_file in sorted(cleaned_images):
            # 从文件名提取原始编号
            name_parts = img_file.stem.replace("cleaned_dog_", "").replace("cleaned_", "")
            number = int(name_parts.split('_')[1]) if '_' in name_parts else 0
            
            index_data["images"].append({
                "number": number,
                "filename": img_file.name,
                "original_filename": img_file.name.replace("cleaned_", ""),
                "status": "cleaned"
            })
        
        # 保存索引文件
        index_path = self.output_dir / "cleaned_index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"清洗后的索引文件已创建: {index_path}")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="清洗亚马逊狗狗图片水印")
    parser.add_argument("--input", "-i", default="data/dogs", help="输入图片目录")
    parser.add_argument("--output", "-o", default="data/cleaned_dogs", help="输出目录")
    parser.add_argument("--single", "-s", help="处理单张图片")
    parser.add_argument("--test", "-t", action="store_true", help="测试模式，只处理前5张图片")
    
    args = parser.parse_args()
    
    cleaner = WatermarkCleaner(args.input, args.output)
    
    if args.single:
        # 处理单张图片
        input_path = Path(args.single)
        output_path = Path(args.output) / "images" / f"cleaned_{input_path.name}"
        cleaner.process_single_image(input_path, output_path)
    elif args.test:
        # 测试模式
        logger.info("测试模式：只处理前5张图片")
        image_files = list(Path(args.input).glob("*.jpg"))[:5]
        for img_file in image_files:
            output_file = Path(args.output) / "images" / f"cleaned_{img_file.name}"
            cleaner.process_single_image(img_file, output_file)
    else:
        # 批量处理
        cleaner.process_all_images()

if __name__ == "__main__":
    main() 