# Amazon Dogs - Image Crawler & Gallery

<div align="right">
  <a href="README.zh-CN.md">中文</a>
</div>

English | [中文](README.zh-CN.md)

A complete open-source project that crawls and displays dog images from Amazon's error pages.

## 🌟 Features

### Python Crawler
- Automatically fetches dog images from Amazon (starting from 1, incrementing)
- Smart stopping mechanism (max 1000 images or 100 consecutive 404s)
- 3-second delay between requests to avoid rate limiting
- Auto-generates index.json index file
- Detailed logging

### React Frontend
- Modern masonry layout
- Responsive design for all devices
- Image lazy loading with loading animations
- Elegant error handling and loading states
- Smooth hover animations

## 🚀 Quick Start

### Quick Start (Recommended)

The project already includes 200 dog images, so you can use it immediately without running the crawler:

```bash
# 1. Install dependencies
pip install -r requirements.txt
npm install

# 2. Build frontend
cd frontend
npm install
cd ..
npm run build

# 3. Start server
node server.js
```

Visit http://localhost:3000 to view the dog images!

### Optional: Run Crawler for New Images

If you want to fetch more dog images, you can run the crawler:

```bash
python dog_crawler.py
```

The crawler will:
- Start from https://images-na.ssl-images-amazon.com/images/G/01/error/1._TTD_.jpg
- Increment numbers to fetch images
- Save images to data/dogs/ directory
- Generate data/dogs/index.json index file

### Build Frontend

```bash
cd frontend
npm run build
cd ..
```

### Start Server

```bash
node server.js
```

After starting the server, visit http://localhost:3000 to view the dog gallery.

## 📖 Usage

### Crawler Configuration

You can modify these parameters in dog_crawler.py:
- max_number: Maximum number of images (default: 1000)
- max_consecutive_404: Maximum consecutive 404s (default: 100)
- output_dir: Image save directory (default: data/dogs)

### Frontend Features

- Masonry Layout: Auto-adjusts columns (4 desktop, 3 tablet, 2 mobile, 1 small screen)
- Image Info: Shows image number and file size
- Loading States: Beautiful loading animations
- Error Handling: 404 images auto-hidden
- Responsive: Perfectly adapts to all screen sizes

## 🛠️ Development Scripts

```bash
# Run crawler
npm run crawler

# Build frontend
npm run build

# Start dev server
npm run dev

# Full setup
npm run setup
```

## 🧰 Tech Stack

### Backend
- Python 3.x: Core crawler
- requests: HTTP request library
- Node.js: Server environment
- Express: Web framework

### Frontend
- React 18: Frontend framework
- TypeScript: Type safety
- CSS3: Modern styling and animations
- Responsive Design: Adaptive layouts

## ⚠️ Important Notes

1. Request Rate: Crawler has 3-second delays, please don't make too frequent
2. Storage: Images are large, ensure enough storage space
3. Network: Stable connection required for downloading
4. Browser: Modern browsers recommended (Chrome, Firefox, Safari, Edge)

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

Issues and Pull Requests welcome!

---

Enjoy these cute dog images!
