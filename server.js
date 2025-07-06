const express = require('express');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// 提供静态文件服务
app.use('/data', express.static(path.join(__dirname, 'data')));

// 提供前端构建文件
app.use(express.static(path.join(__dirname, 'frontend/build')));

// API路由 - 获取图片列表
app.get('/api/images', (req, res) => {
  const indexPath = path.join(__dirname, 'data/dogs/index.json');
  
  fs.readFile(indexPath, 'utf8', (err, data) => {
    if (err) {
      console.error('读取index.json失败:', err);
      return res.status(500).json({ error: '无法读取图片索引' });
    }
    
    try {
      const indexData = JSON.parse(data);
      res.json(indexData);
    } catch (parseErr) {
      console.error('解析index.json失败:', parseErr);
      res.status(500).json({ error: '无法解析图片索引' });
    }
  });
});

// 所有其他请求都返回React应用
app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'frontend/build/index.html'));
});

// 启动服务器
app.listen(PORT, () => {
  console.log(`服务器运行在 http://localhost:${PORT}`);
  console.log(`图片文件可访问: http://localhost:${PORT}/data/dogs/`);
});

// 优雅关闭
process.on('SIGINT', () => {
  console.log('\n正在关闭服务器...');
  process.exit(0);
}); 