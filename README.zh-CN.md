<div align="right">
  <a href="README.md">English</a>
</div>

# Amazon Dogs - 狗狗图片下载器

一个简单的开源工具，用于从亚马逊404错误页面下载狗狗图片。

## 这个项目是什么？

本项目用于下载亚马逊错误页面上出现的狗狗图片。这些图片可通过可预测的URL访问，例如：
- https://images-na.ssl-images-amazon.com/images/G/01/error/1._TTD_.jpg
- https://images-na.ssl-images-amazon.com/images/G/01/error/2._TTD_.jpg
- 依此类推...

项目包含200张预下载的狗狗图片，可直接使用。

## 如何使用下载的图片？

### 方法1：克隆整个仓库

```bash
git clone https://github.com/good-sellers/amazon-dogs.git
cd amazon-dogs
```

下载的图片位于 `data/cleaned_dogs/images/` 目录：
- 200张狗狗图片（cleaned_dog_1.jpg 到 cleaned_dog_200.jpg）
- 索引文件：`data/cleaned_dogs/cleaned_index.json`

### 方法2：仅下载图片

您可以只下载图片文件，而无需克隆整个代码仓库。

## 工作原理是什么？

下载器的工作原理是：

1. **URL模式**: 亚马逊使用可预测的URL模式来显示错误页面图片
   - 基础URL：`https://images-na.ssl-images-amazon.com/images/G/01/error/`
   - 文件格式：`{数字}._TTD_.jpg`（从1开始）

2. **顺序获取**: 按顺序尝试图片URL（1, 2, 3, 4...）

3. **智能停止**: 当满足以下条件时停止：
   - 达到最大图片数量（默认：1000张）
   - 连续遇到100个404错误
   - 每次请求间隔3秒，避免请求过于频繁

4. **图片存储**: 成功下载的图片保存到 `data/dogs/` 目录，并生成索引文件

## 可选：自己运行爬虫

如果你想下载更多图片：

```bash
# 安装依赖
pip install -r requirements.txt

# 运行爬虫
python dog_crawler.py
```

## 许可证

MIT许可证
