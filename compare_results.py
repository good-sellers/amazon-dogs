#!/usr/bin/env python3
"""
比较原图和清洗后图片的效果
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def compare_images(original_path, cleaned_path, output_path):
    """比较原图和清洗后的图片"""
    # 读取图片
    original = cv2.imread(str(original_path))
    cleaned = cv2.imread(str(cleaned_path))
    
    if original is None or cleaned is None:
        print(f"无法读取图片: {original_path} 或 {cleaned_path}")
        return
    
    # 转换颜色空间用于显示
    original_rgb = cv2.cvtColor(original, cv2.COLOR_BGR2RGB)
    cleaned_rgb = cv2.cvtColor(cleaned, cv2.COLOR_BGR2RGB)
    
    # 计算差异
    diff = cv2.absdiff(original, cleaned)
    diff_rgb = cv2.cvtColor(diff, cv2.COLOR_BGR2RGB)
    
    # 创建对比图
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    # 原图
    axes[0, 0].imshow(original_rgb)
    axes[0, 0].set_title(f'原图 - {original_path.name}', fontsize=10)
    axes[0, 0].axis('off')
    
    # 清洗后的图
    axes[0, 1].imshow(cleaned_rgb)
    axes[0, 1].set_title(f'清洗后 - {cleaned_path.name}', fontsize=10)
    axes[0, 1].axis('off')
    
    # 差异图
    axes[1, 0].imshow(diff_rgb)
    axes[1, 0].set_title('差异图（红色区域为修改部分）', fontsize=10)
    axes[1, 0].axis('off')
    
    # 底部区域放大对比
    height = original.shape[0]
    bottom_original = original_rgb[int(height*0.7):, :]
    bottom_cleaned = cleaned_rgb[int(height*0.7):, :]
    
    # 并排显示底部区域
    bottom_comparison = np.hstack([bottom_original, bottom_cleaned])
    axes[1, 1].imshow(bottom_comparison)
    axes[1, 1].set_title('底部区域对比（左：原图，右：清洗后）', fontsize=10)
    axes[1, 1].axis('off')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"对比图已保存: {output_path}")

def main():
    """对比所有测试图片"""
    original_dir = Path("data/dogs")
    cleaned_dir = Path("data/cleaned_dogs/images")
    
    # 获取已清洗的图片
    cleaned_files = list(cleaned_dir.glob("cleaned_*.jpg"))
    
    if not cleaned_files:
        print("未找到清洗后的图片")
        return
    
    print(f"找到 {len(cleaned_files)} 张清洗后的图片")
    
    for cleaned_file in cleaned_files[:5]:  # 只对比前5张
        # 找到对应的原图
        original_name = cleaned_file.name.replace("cleaned_", "")
        original_file = original_dir / original_name
        
        if original_file.exists():
            output_name = f"comparison_{original_name.replace('.jpg', '.png')}"
            compare_images(original_file, cleaned_file, output_name)
        else:
            print(f"未找到原图: {original_file}")

if __name__ == "__main__":
    main() 