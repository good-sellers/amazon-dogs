#!/usr/bin/env python3
"""
为精确清洗后的图片生成索引文件
"""

import json
import os
from pathlib import Path
from datetime import datetime

def generate_cleaned_index():
    """生成清洗后图片的索引文件"""
    # 读取原始索引文件
    original_index_path = Path("data/dogs/index.json")
    cleaned_images_dir = Path("data/precise_cleaned/images")
    cleaned_index_path = Path("data/precise_cleaned/index.json")
    
    if not original_index_path.exists():
        print(f"原始索引文件不存在: {original_index_path}")
        return
    
    if not cleaned_images_dir.exists():
        print(f"清洗后图片目录不存在: {cleaned_images_dir}")
        return
    
    # 读取原始索引
    with open(original_index_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    # 创建新的索引数据
    cleaned_data = {
        "total_images": 0,
        "images": [],
        "created_at": datetime.now().isoformat(),
        "description": "精确清洗后的狗狗图片 - 已去除蓝色水印",
        "source": "Amazon Dogs Images - Watermark Cleaned"
    }
    
    # 遍历原始图片信息
    for original_image in original_data["images"]:
        # 构建清洗后图片的文件路径
        cleaned_filename = f"precise_{original_image['filename']}"
        cleaned_file_path = cleaned_images_dir / cleaned_filename
        
        # 检查清洗后的图片是否存在
        if cleaned_file_path.exists():
            # 获取文件大小
            file_size = cleaned_file_path.stat().st_size
            
            # 创建新的图片信息
            cleaned_image = {
                "number": original_image["number"],
                "filename": cleaned_filename,
                "url": original_image["url"],  # 保留原始URL作为备用
                "size": file_size,
                "original_filename": original_image["filename"],
                "original_size": original_image["size"],
                "watermark_removed": True
            }
            
            cleaned_data["images"].append(cleaned_image)
            cleaned_data["total_images"] += 1
            
            print(f"✅ 处理图片 {original_image['number']}: {cleaned_filename} ({file_size} bytes)")
        else:
            print(f"❌ 清洗后图片不存在: {cleaned_filename}")
    
    # 保存新的索引文件
    cleaned_index_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(cleaned_index_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n📁 清洗后索引文件已保存: {cleaned_index_path}")
    print(f"📊 总计处理图片: {cleaned_data['total_images']} 张")
    
    # 创建前端 public 目录的索引副本
    frontend_public_path = Path("frontend/public/cleaned_index.json")
    frontend_public_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(frontend_public_path, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, indent=2, ensure_ascii=False)
    
    print(f"📄 前端索引文件已保存: {frontend_public_path}")

if __name__ == "__main__":
    generate_cleaned_index() 