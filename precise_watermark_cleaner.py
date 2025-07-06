#!/usr/bin/env python3
"""
精确水印清洗器 - 专门针对蓝色"Meet The dogs of Amazon"文字
只清洗蓝色文字水印，其他区域完全不动
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

class PreciseWatermarkCleaner:
    def __init__(self, input_dir="data/dogs", output_dir="data/precise_cleaned"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "images").mkdir(exist_ok=True)
        
    def detect_blue_text_regions(self, img):
        """专门检测蓝色文字区域"""
        height, width = img.shape[:2]
        
        # 转换到HSV颜色空间，更好地检测蓝色
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        
        # 定义蓝色范围 (针对Amazon的蓝色文字)
        # 蓝色的HSV范围
        lower_blue1 = np.array([100, 50, 50])   # 较深的蓝色
        upper_blue1 = np.array([130, 255, 255])
        
        lower_blue2 = np.array([90, 40, 40])    # 较浅的蓝色
        upper_blue2 = np.array([140, 255, 255])
        
        # 创建蓝色掩码
        mask_blue1 = cv2.inRange(hsv, lower_blue1, upper_blue1)
        mask_blue2 = cv2.inRange(hsv, lower_blue2, upper_blue2)
        blue_mask = cv2.bitwise_or(mask_blue1, mask_blue2)
        
        # 只检查图片底部区域（水印位置）
        bottom_start = int(height * 0.75)  # 更保守，只检查底部25%
        blue_mask[:bottom_start, :] = 0  # 清零上面区域
        
        # 形态学操作，连接文字字符
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 1))
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_CLOSE, kernel)
        
        # 去除噪声
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        blue_mask = cv2.morphologyEx(blue_mask, cv2.MORPH_OPEN, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        blue_text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            
            # 非常严格的过滤条件，只保留明显的文字区域
            if (w > 20 and h > 8 and         # 最小尺寸
                w < width * 0.6 and          # 最大宽度限制
                h < height * 0.1 and         # 最大高度限制
                area > 150 and               # 最小面积
                y > bottom_start):           # 必须在底部区域
                
                # 检查区域内蓝色像素密度
                roi_mask = blue_mask[y:y+h, x:x+w]
                blue_ratio = np.sum(roi_mask > 0) / (w * h)
                
                if blue_ratio > 0.3:  # 蓝色像素占比超过30%
                    blue_text_regions.append((x, y, w, h))
        
        logger.info(f"检测到 {len(blue_text_regions)} 个蓝色文字区域")
        for i, (x, y, w, h) in enumerate(blue_text_regions):
            logger.info(f"蓝色区域 {i+1}: 位置({x},{y}) 尺寸{w}x{h}")
        
        return blue_text_regions, blue_mask
    
    def conservative_inpainting(self, img, regions):
        """保守的图像修复，只修复确定的蓝色文字区域"""
        if not regions:
            return img
        
        result = img.copy()
        
        for x, y, w, h in regions:
            # 只修复很小的边界扩展
            padding = 1  # 只扩展1像素
            x1 = max(0, x - padding)
            y1 = max(0, y - padding)
            x2 = min(img.shape[1], x + w + padding)
            y2 = min(img.shape[0], y + h + padding)
            
            # 创建小范围掩码
            mask = np.zeros(img.shape[:2], dtype=np.uint8)
            cv2.rectangle(mask, (x1, y1), (x2, y2), 255, -1)
            
            # 使用Telea算法（更保守）
            result = cv2.inpaint(result, mask, 2, cv2.INPAINT_TELEA)
        
        return result
    
    def precise_watermark_removal(self, img):
        """精确的水印移除，只针对蓝色文字"""
        # 1. 检测蓝色文字区域
        blue_regions, blue_mask = self.detect_blue_text_regions(img)
        
        if not blue_regions:
            logger.info("未检测到蓝色文字水印")
            return img, blue_mask
        
        # 2. 保守的修复
        result = self.conservative_inpainting(img, blue_regions)
        
        return result, blue_mask
    
    def process_single_image(self, input_path, output_path, save_debug=False):
        """处理单张图片"""
        try:
            img = cv2.imread(str(input_path))
            if img is None:
                logger.error(f"无法读取图片: {input_path}")
                return False
            
            logger.info(f"处理图片: {input_path.name}")
            
            # 精确水印清洗
            cleaned_img, debug_mask = self.precise_watermark_removal(img)
            
            # 保存结果
            success = cv2.imwrite(str(output_path), cleaned_img)
            
            # 保存调试信息
            if save_debug:
                debug_path = output_path.parent / f"debug_{output_path.name}"
                cv2.imwrite(str(debug_path.with_suffix('.png')), debug_mask)
                logger.info(f"调试掩码已保存: {debug_path}")
            
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