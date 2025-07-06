#!/usr/bin/env python3
"""
精确水印清洗器 - 基于连通组件分析和OCR识别
专门针对蓝色"Meet The dogs of Amazon"文字
"""

import cv2
import numpy as np
import os
import json
import argparse
import logging
from pathlib import Path
import pytesseract
from PIL import Image
import re

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PreciseWatermarkCleaner:
    def __init__(self, input_dir="data/dogs", output_dir="data/precise_cleaned"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        
    def is_blue_pixel(self, pixel):
        """判断像素是否是蓝色像素"""
        b, g, r = pixel
        # 蓝色判断条件：蓝色分量高，红色和绿色分量低
        return (b > 100 and b > g + 30 and b > r + 30)
    
    def flood_fill_blue_region(self, img, start_x, start_y, visited):
        """从蓝色像素开始，使用洪水填充算法找到连通的蓝色区域"""
        height, width = img.shape[:2]
        region_pixels = []
        stack = [(start_x, start_y)]
        
        # 8个方向
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        
        while stack:
            x, y = stack.pop()
            
            # 检查边界
            if x < 0 or x >= width or y < 0 or y >= height:
                continue
            
            # 检查是否已访问
            if visited[y, x]:
                continue
            
            # 检查是否是蓝色像素
            if not self.is_blue_pixel(img[y, x]):
                continue
            
            # 标记为已访问
            visited[y, x] = True
            region_pixels.append((x, y))
            
            # 向8个方向扩展
            for dx, dy in directions:
                stack.append((x + dx, y + dy))
        
        return region_pixels
    
    def extract_region_for_ocr(self, img, region_pixels):
        """从连通区域提取图像片段用于OCR识别"""
        if not region_pixels:
            return None
        
        # 计算边界框
        xs = [p[0] for p in region_pixels]
        ys = [p[1] for p in region_pixels]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        
        # 添加一些边距
        padding = 5
        min_x = max(0, min_x - padding)
        min_y = max(0, min_y - padding)
        max_x = min(img.shape[1], max_x + padding)
        max_y = min(img.shape[0], max_y + padding)
        
        # 提取区域
        roi = img[min_y:max_y, min_x:max_x]
        
        # 转换为灰度图
        if len(roi.shape) == 3:
            roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            roi_gray = roi
        
        # 二值化，让文字更清晰
        _, roi_binary = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return roi_binary, (min_x, min_y, max_x - min_x, max_y - min_y)
    
    def is_text_region(self, roi_image):
        """使用OCR判断区域是否包含文字"""
        if roi_image is None or roi_image.size == 0:
            return False
        
        try:
            # 放大图像以提高OCR准确性
            scale_factor = 3
            enlarged = cv2.resize(roi_image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_CUBIC)
            
            # 使用PIL Image进行OCR
            pil_image = Image.fromarray(enlarged)
            
            # OCR配置：只识别英文字母
            config = '--oem 3 --psm 8 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
            text = pytesseract.image_to_string(pil_image, config=config).strip()
            
            # 清理文字
            text = re.sub(r'[^a-zA-Z]', '', text)
            
            # 如果识别出至少1个字母，认为是文字区域
            if len(text) >= 1:
                logger.info(f"识别到文字: '{text}'")
                return True
            
            return False
            
        except Exception as e:
            logger.warning(f"OCR识别失败: {e}")
            return False
    
    def fill_region_with_white(self, img, region_pixels):
        """将连通区域填充为白色"""
        for x, y in region_pixels:
            img[y, x] = [255, 255, 255]  # 白色
    
    def smart_watermark_removal(self, img):
        """使用新算法进行水印移除"""
        height, width = img.shape[:2]
        result = img.copy()
        visited = np.zeros((height, width), dtype=bool)
        
        # 只在图片底部区域查找蓝色文字
        start_y = int(height * 0.7)  # 从70%的高度开始
        
        removed_regions = 0
        
        # 遍历每个像素
        for y in range(start_y, height):
            for x in range(width):
                # 跳过已访问的像素
                if visited[y, x]:
                    continue
                
                # 检查是否是蓝色像素
                if not self.is_blue_pixel(img[y, x]):
                    continue
                
                # 找到连通的蓝色区域
                region_pixels = self.flood_fill_blue_region(img, x, y, visited)
                
                # 如果区域太小，跳过
                if len(region_pixels) < 20:
                    continue
                
                # 提取区域进行OCR
                roi_data = self.extract_region_for_ocr(img, region_pixels)
                if roi_data is None:
                    continue
                
                roi_image, bbox = roi_data
                
                # 检查是否是文字区域
                if self.is_text_region(roi_image):
                    # 填充为白色
                    self.fill_region_with_white(result, region_pixels)
                    removed_regions += 1
                    logger.info(f"移除了文字区域 {removed_regions}: 位置({bbox[0]},{bbox[1]}) 尺寸{bbox[2]}x{bbox[3]}")
        
        logger.info(f"总共移除了 {removed_regions} 个文字区域")
        return result
    
    def process_single_image(self, input_path, output_path, save_debug=False):
        """处理单张图片"""
        try:
            img = cv2.imread(str(input_path))
            if img is None:
                logger.error(f"无法读取图片: {input_path}")
                return False
            
            logger.info(f"处理图片: {input_path.name}")
            
            # 使用新算法进行水印清洗
            cleaned_img = self.smart_watermark_removal(img)
            
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
    
    def create_comparison_image(self, original_path, cleaned_path, output_path):
        """创建原图和清洗后的对比图"""
        original = cv2.imread(str(original_path))
        cleaned = cv2.imread(str(cleaned_path))
        
        if original is None or cleaned is None:
            return
        
        # 转换颜色用于显示
        original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
        cleaned_rgb = cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB)
        
        # 计算差异
        diff = cv2.absdiff(original, cleaned)
        diff_rgb = cv2.cvtColor(diff, cv2.COLOR_BGR2RGB)
        
        # 创建对比图
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # 原图
        axes[0].imshow(original_rgb)
        axes[0].set_title('Original Image')
        axes[0].axis('off')
        
        # 清洗后
        axes[1].imshow(cleaned_rgb)
        axes[1].set_title('Cleaned Image')
        axes[1].axis('off')
        
        # 差异图
        axes[2].imshow(diff_rgb)
        axes[2].set_title('Difference (Changes in Red)')
        axes[2].axis('off')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        logger.info(f"对比图已保存: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="精确蓝色水印清洗工具")
    parser.add_argument("--input", "-i", default="data/dogs", help="输入目录")
    parser.add_argument("--output", "-o", default="data/precise_cleaned", help="输出目录")
    parser.add_argument("--single", "-s", help="处理单张图片")
    parser.add_argument("--test", "-t", action="store_true", help="测试模式（3张图片）")
    parser.add_argument("--debug", "-d", action="store_true", help="保存调试信息")
    parser.add_argument("--compare", "-c", action="store_true", help="生成对比图")
    
    args = parser.parse_args()
    
    cleaner = PreciseWatermarkCleaner(args.input, args.output)
    
    if args.single:
        input_path = Path(args.single)
        output_path = Path(args.output) / "images" / f"precise_{input_path.name}"
        cleaner.process_single_image(input_path, output_path, args.debug)
        
        if args.compare:
            compare_path = f"precise_comparison_{input_path.stem}.png"
            cleaner.create_comparison_image(input_path, output_path, compare_path)
            
    elif args.test:
        logger.info("测试模式：处理前3张图片")
        image_files = list(Path(args.input).glob("*.jpg"))[:3]
        for img_file in image_files:
            output_file = Path(args.output) / "images" / f"precise_{img_file.name}"
            cleaner.process_single_image(img_file, output_file, args.debug)
            
            if args.compare:
                compare_path = f"precise_comparison_{img_file.stem}.png"
                cleaner.create_comparison_image(img_file, output_file, compare_path)
    else:
        logger.info("批量处理所有图片")
        image_files = list(Path(args.input).glob("*.jpg"))
        total = len(image_files)
        success = 0
        
        for i, img_file in enumerate(image_files, 1):
            output_file = Path(args.output) / "images" / f"precise_{img_file.name}"
            logger.info(f"进度 [{i}/{total}]")
            
            if cleaner.process_single_image(img_file, output_file, args.debug):
                success += 1
        
        logger.info(f"批量处理完成！成功: {success}/{total}")

if __name__ == "__main__":
    main() 