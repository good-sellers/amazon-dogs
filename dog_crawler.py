#!/usr/bin/env python3
"""
Amazon Dogs Image Crawler
从亚马逊抓取狗狗图片的爬虫程序
"""

import os
import json
import requests
from time import sleep
from urllib.parse import urlparse
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DogImageCrawler:
    def __init__(self, base_url="https://images-na.ssl-images-amazon.com/images/G/01/error/", 
                 output_dir="data/dogs", max_number=1000, max_consecutive_404=100):
        self.base_url = base_url
        self.output_dir = output_dir
        self.max_number = max_number
        self.max_consecutive_404 = max_consecutive_404
        self.downloaded_images = []
        self.consecutive_404_count = 0
        
        # 确保输出目录存在
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置请求headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    def download_image(self, number):
        """下载单个图片"""
        url = f"{self.base_url}{number}._TTD_.jpg"
        filename = f"dog_{number}.jpg"
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            logger.info(f"正在尝试下载图片 {number}: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                # 检查是否真的是图片内容
                if response.headers.get('content-type', '').startswith('image/'):
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    image_info = {
                        'number': number,
                        'filename': filename,
                        'url': url,
                        'size': len(response.content)
                    }
                    self.downloaded_images.append(image_info)
                    self.consecutive_404_count = 0  # 重置404计数
                    logger.info(f"成功下载图片 {number}, 文件大小: {len(response.content)} bytes")
                    return True
                else:
                    logger.warning(f"图片 {number} 不是有效的图片格式")
                    self.consecutive_404_count += 1
                    return False
            else:
                logger.warning(f"图片 {number} 下载失败, 状态码: {response.status_code}")
                self.consecutive_404_count += 1
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"下载图片 {number} 时发生错误: {e}")
            self.consecutive_404_count += 1
            return False
    
    def create_index(self):
        """创建索引文件"""
        index_path = os.path.join(self.output_dir, 'index.json')
        index_data = {
            'total_images': len(self.downloaded_images),
            'images': self.downloaded_images,
            'created_at': str(pd.Timestamp.now()) if 'pd' in globals() else str(datetime.now())
        }
        
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
            logger.info(f"索引文件已创建: {index_path}")
        except Exception as e:
            logger.error(f"创建索引文件时发生错误: {e}")
    
    def crawl(self):
        """开始爬取"""
        logger.info("开始爬取亚马逊狗狗图片...")
        logger.info(f"爬取范围: 1-{self.max_number}")
        logger.info(f"最大连续404次数: {self.max_consecutive_404}")
        
        for number in range(1, self.max_number + 1):
            # 检查是否达到最大连续404次数
            if self.consecutive_404_count >= self.max_consecutive_404:
                logger.info(f"达到最大连续404次数({self.max_consecutive_404})，停止爬取")
                break
            
            # 下载图片
            self.download_image(number)
            
            # 添加延时，避免请求过于频繁
            sleep(3)
            
            # 每下载10张图片显示进度
            if number % 10 == 0:
                logger.info(f"进度: {number}/{self.max_number}, 已下载: {len(self.downloaded_images)} 张图片")
        
        logger.info(f"爬取完成！总共下载了 {len(self.downloaded_images)} 张图片")
        
        # 创建索引文件
        self.create_index()
        
        return len(self.downloaded_images)

def main():
    """主函数"""
    crawler = DogImageCrawler()
    downloaded_count = crawler.crawl()
    
    print(f"\n爬取完成！")
    print(f"总共下载了 {downloaded_count} 张狗狗图片")
    print(f"图片保存在: {crawler.output_dir}")
    print(f"索引文件: {os.path.join(crawler.output_dir, 'index.json')}")

if __name__ == "__main__":
    main() 