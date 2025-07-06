# Amazon Dogs - 亚马逊狗狗图片爬虫与展示

这是一个完整的项目，包含Python爬虫和React前端，用于抓取并展示亚马逊上的狗狗图片。

## 项目结构

```
amazon-dogs/
├── dog_crawler.py          # Python爬虫主程序
├── requirements.txt        # Python依赖
├── server.js              # Node.js服务器
├── package.json           # Node.js依赖
├── data/
│   └── dogs/              # 存放下载的图片和索引文件
├── frontend/              # React前端项目
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DogGallery.tsx
│   │   │   └── DogGallery.css
│   │   ├── App.tsx
│   │   ├── App.css
│   │   └── index.tsx
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## 功能特色

### Python爬虫
- 🐕 自动抓取亚马逊狗狗图片（从1开始递增）
- 📊 智能停止机制（最大1000张或连续100个404）
- 📱 每个请求间隔3秒，避免请求过于频繁
- 📝 自动生成index.json索引文件
- 📋 详细的日志记录

### 🧽 水印清洗功能
- 🎯 **精确清洗蓝色文字水印** - 只清洗"Meet The dogs of Amazon"文字
- 🛡️ **完全保护狗狗身体** - 零误删，其他区域完全不动
- 🔧 **HSV颜色检测** - 专门针对蓝色文字的精确算法
- 📊 **批量处理** - 200张图片100%成功处理
- 🔍 **效果对比** - 可视化分析和对比工具

### React前端
- 🎨 现代化的瀑布流布局
- 📱 响应式设计，支持各种设备
- 🔄 图片懒加载和加载动画
- 🎭 优雅的错误处理和加载状态
- 💫 流畅的悬停动画效果

## 快速开始

### 1. 安装依赖

```bash
# 安装Python依赖
pip install -r requirements.txt

# 安装Node.js依赖
npm install

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 2. 运行爬虫

```bash
python dog_crawler.py
```

爬虫会：
- 从 `https://images-na.ssl-images-amazon.com/images/G/01/error/1._TTD_.jpg` 开始
- 依次递增数字抓取图片
- 将图片保存到 `data/dogs/` 目录
- 生成 `data/dogs/index.json` 索引文件

### 2.5. 清洗水印（🎯精确版）

```bash
# 精确清洗测试（推荐）
python precise_watermark_cleaner.py --test --compare

# 精确批量清洗所有图片
python precise_watermark_cleaner.py

# 处理单张图片并查看效果
python precise_watermark_cleaner.py --single data/dogs/dog_1.jpg --compare
```

精确水印清洗会：
- **只清洗蓝色"Meet The dogs of Amazon"文字**
- **完全保护狗狗身体，零误删**
- 生成清洗后的图片到 `data/precise_cleaned/` 目录
- 可选生成调试掩码查看检测区域

### 3. 构建前端

```bash
cd frontend
npm run build
cd ..
```

### 4. 启动服务器

```bash
node server.js
```

服务器启动后，访问 `http://localhost:3000` 查看狗狗图片展示页面。

## 使用说明

### 爬虫配置

可以在 `dog_crawler.py` 中修改以下参数：
- `max_number`: 最大图片数量（默认1000）
- `max_consecutive_404`: 最大连续404次数（默认100）
- `output_dir`: 图片保存目录（默认data/dogs）

### 前端特性

- **瀑布流布局**: 自动调整列数（桌面4列，平板3列，手机2列，小屏幕1列）
- **图片信息**: 显示图片编号和文件大小
- **加载状态**: 美观的加载动画
- **错误处理**: 404图片自动隐藏
- **响应式**: 完美适配各种屏幕尺寸

## 开发脚本

```bash
# 运行爬虫
npm run crawler

# 构建前端
npm run build

# 启动开发服务器
npm run dev

# 完整安装
npm run setup
```

## 🧽 水印清洗脚本

```bash
# 水印分析（了解水印特征）
python analyze_watermark.py

# 测试清洗效果
python improved_watermark_cleaner.py --test

# 批量清洗所有图片
python improved_watermark_cleaner.py

# 生成效果对比图
python compare_results.py

# 处理单张图片
python improved_watermark_cleaner.py --single data/dogs/dog_1.jpg
```

## 技术栈

### 后端
- **Python 3.x**: 爬虫核心和图像处理
- **requests**: HTTP请求库
- **OpenCV**: 计算机视觉和图像处理
- **NumPy**: 数值计算和数组操作
- **Matplotlib**: 数据可视化和分析
- **Node.js**: 服务器运行环境
- **Express**: Web框架

### 前端
- **React 18**: 前端框架
- **TypeScript**: 类型安全
- **CSS3**: 现代样式和动画
- **Responsive Design**: 响应式布局

## 注意事项

1. **请求频率**: 爬虫设置了3秒间隔，请不要修改得过于频繁
2. **存储空间**: 图片文件较大，请确保有足够的存储空间
3. **网络连接**: 需要稳定的网络连接来下载图片
4. **浏览器支持**: 建议使用现代浏览器（Chrome、Firefox、Safari、Edge）

### 🧽 水印清洗注意事项

1. **备份重要**: 原始图片保持不变，清洗后图片保存在单独目录
2. **先测试**: 建议先使用`--test`参数测试清洗效果
3. **质量检查**: 使用对比工具检查清洗质量
4. **依赖安装**: 需要安装OpenCV、NumPy等图像处理库
5. **内存使用**: 批量处理时可能需要较多内存

## 许可证

MIT License - 详见 LICENSE 文件

## 贡献

欢迎提交 Issues 和 Pull Requests！

---

🐕 享受这些可爱的狗狗图片吧！ 