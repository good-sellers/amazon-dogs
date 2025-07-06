#!/usr/bin/env python3
"""
水印分析工具 - 用于查看和分析图片中的水印特征
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def analyze_image_watermark(image_path):
    """详细分析图片中的水印"""
    print(f"分析图片: {image_path}")
    
    # 读取图片
    img = cv2.imread(str(image_path))
    if img is None:
        print("无法读取图片")
        return
    
    height, width = img.shape[:2]
    print(f"图片尺寸: {width} x {height}")
    
    # 转换为灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 分析图片的不同区域
    regions = {
        'top': gray[:height//4, :],
        'middle': gray[height//4:3*height//4, :],
        'bottom': gray[3*height//4:, :],
    }
    
    print("\n各区域文字检测:")
    for region_name, region in regions.items():
        print(f"\n{region_name.upper()} 区域:")
        
        # 使用不同的阈值方法
        methods = [
            ('BINARY', cv2.THRESH_BINARY),
            ('BINARY_INV', cv2.THRESH_BINARY_INV),
            ('OTSU', cv2.THRESH_BINARY + cv2.THRESH_OTSU),
            ('ADAPTIVE_MEAN', None),
            ('ADAPTIVE_GAUSSIAN', None)
        ]
        
        for method_name, thresh_type in methods:
            if 'ADAPTIVE' in method_name:
                if 'MEAN' in method_name:
                    thresh = cv2.adaptiveThreshold(region, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
                else:
                    thresh = cv2.adaptiveThreshold(region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
            else:
                _, thresh = cv2.threshold(region, 0, 255, thresh_type)
            
            # 查找轮廓
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 过滤轮廓
            text_contours = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                area = cv2.contourArea(contour)
                aspect_ratio = w / h if h > 0 else 0
                
                # 文字轮廓的特征
                if (w > 20 and h > 8 and 
                    area > 100 and 
                    0.1 < aspect_ratio < 20):
                    text_contours.append((x, y, w, h, area))
            
            if text_contours:
                print(f"  {method_name}: 发现 {len(text_contours)} 个可能的文字区域")
                for i, (x, y, w, h, area) in enumerate(text_contours[:3]):  # 只显示前3个
                    print(f"    区域{i+1}: ({x},{y}) 尺寸{w}x{h} 面积{area}")

def create_watermark_detection_visualization(image_path, output_path):
    """创建水印检测可视化图片"""
    img = cv2.imread(str(image_path))
    if img is None:
        return
    
    height, width = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 重点分析底部区域
    bottom_region = gray[int(height * 0.6):, :]
    
    # 使用多种方法检测文字
    methods = [
        ('OTSU', cv2.threshold(bottom_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]),
        ('ADAPTIVE', cv2.adaptiveThreshold(bottom_region, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)),
    ]
    
    # 创建可视化图片
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    
    # 原图
    axes[0, 0].imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    axes[0, 0].set_title('原图')
    axes[0, 0].axis('off')
    
    # 灰度图
    axes[0, 1].imshow(gray, cmap='gray')
    axes[0, 1].set_title('灰度图')
    axes[0, 1].axis('off')
    
    # 底部区域
    axes[0, 2].imshow(bottom_region, cmap='gray')
    axes[0, 2].set_title('底部区域 (60%以下)')
    axes[0, 2].axis('off')
    
    # 不同阈值化方法
    for i, (method_name, thresh_img) in enumerate(methods):
        row = 1
        col = i
        axes[row, col].imshow(thresh_img, cmap='gray')
        axes[row, col].set_title(f'{method_name} 阈值化')
        axes[row, col].axis('off')
        
        # 找到轮廓并标记
        contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        result_img = cv2.cvtColor(thresh_img, cv2.COLOR_GRAY2RGB)
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h > 10:  # 可能的文字区域
                cv2.rectangle(result_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        
        if i < 2:  # 避免超出子图范围
            axes[row, col + 1].imshow(result_img)
            axes[row, col + 1].set_title(f'{method_name} 检测结果')
            axes[row, col + 1].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"可视化图片已保存: {output_path}")

def main():
    """主函数"""
    # 分析第一张图片
    image_files = list(Path("data/dogs").glob("*.jpg"))
    if not image_files:
        print("未找到图片文件")
        return
    
    # 分析前3张图片
    for i, img_file in enumerate(image_files[:3]):
        print(f"\n{'='*60}")
        analyze_image_watermark(img_file)
        
        # 创建可视化
        output_path = f"analysis_result_{i+1}.png"
        create_watermark_detection_visualization(img_file, output_path)

if __name__ == "__main__":
    main() 