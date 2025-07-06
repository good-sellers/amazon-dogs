import React, { useState, useEffect } from 'react';
import './DogGallery.css';

interface DogImage {
  number: number;
  filename: string;
  url: string;
  size: number;
}

interface IndexData {
  total_images: number;
  images: DogImage[];
  created_at: string;
}

const DogGallery: React.FC = () => {
  const [images, setImages] = useState<DogImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadImages = async () => {
      try {
        // 尝试从相对路径加载索引文件
        const response = await fetch('/data/dogs/index.json');
        if (!response.ok) {
          throw new Error('无法加载图片索引文件');
        }
        const data: IndexData = await response.json();
        setImages(data.images);
        setLoading(false);
      } catch (err) {
        console.error('加载图片索引失败:', err);
        setError('加载图片索引失败，请确保爬虫已运行并生成了索引文件');
        setLoading(false);
      }
    };

    loadImages();
  }, []);

  const handleImageLoad = (event: React.SyntheticEvent<HTMLImageElement>) => {
    const img = event.currentTarget;
    img.classList.add('loaded');
  };

  const handleImageError = (event: React.SyntheticEvent<HTMLImageElement>) => {
    const img = event.currentTarget;
    img.style.display = 'none';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>正在加载狗狗图片...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <h2>加载失败</h2>
        <p>{error}</p>
        <button onClick={() => window.location.reload()}>重试</button>
      </div>
    );
  }

  if (images.length === 0) {
    return (
      <div className="empty-container">
        <h2>暂无图片</h2>
        <p>请先运行爬虫程序下载图片</p>
      </div>
    );
  }

  return (
    <div className="dog-gallery">
      <div className="gallery-header">
        <h2>狗狗图片展示</h2>
        <p>共找到 {images.length} 张可爱的狗狗图片</p>
      </div>
      
      <div className="masonry-container">
        {images.map((image) => (
          <div key={image.number} className="masonry-item">
            <img
              src={`/data/dogs/${image.filename}`}
              alt={`狗狗 ${image.number}`}
              className="dog-image"
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
            <div className="image-info">
              <span className="image-number">#{image.number}</span>
              <span className="image-size">{Math.round(image.size / 1024)}KB</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DogGallery; 