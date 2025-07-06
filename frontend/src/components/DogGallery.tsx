import React, { useState, useEffect } from 'react';
import './DogGallery.css';

interface DogImage {
  number: number;
  filename: string;
  url: string;
  size: number;
  original_filename?: string;
  original_size?: number;
  watermark_removed?: boolean;
}

interface IndexData {
  total_images: number;
  images: DogImage[];
  created_at: string;
  description?: string;
  source?: string;
}

const DogGallery: React.FC = () => {
  const [images, setImages] = useState<DogImage[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [indexData, setIndexData] = useState<IndexData | null>(null);

  useEffect(() => {
    const loadImages = async () => {
      try {
        // 优先加载清洗后的图片索引文件
        const response = await fetch(
          process.env.NODE_ENV === 'development' 
            ? '/data/precise_cleaned/index.json'
            : `${process.env.PUBLIC_URL}/cleaned_index.json`
        );
        if (!response.ok) {
          throw new Error('无法加载清洗后的图片索引文件');
        }
        const data: IndexData = await response.json();
        setIndexData(data);
        setImages(data.images);
        setLoading(false);
      } catch (err) {
        console.error('加载清洗后图片索引失败:', err);
        
        // 回退到原始图片索引
        try {
          const fallbackResponse = await fetch(
            process.env.NODE_ENV === 'development' 
              ? '/data/dogs/index.json'
              : `${process.env.PUBLIC_URL}/index.json`
          );
          if (!fallbackResponse.ok) {
            throw new Error('无法加载原始图片索引文件');
          }
          const fallbackData: IndexData = await fallbackResponse.json();
          setIndexData(fallbackData);
          setImages(fallbackData.images);
          setLoading(false);
        } catch (fallbackErr) {
          console.error('加载原始图片索引也失败:', fallbackErr);
          setError('加载图片索引失败，请稍后重试');
          setLoading(false);
        }
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

  const getImageSrc = (image: DogImage) => {
    if (process.env.NODE_ENV === 'development') {
      // 开发环境：如果是清洗后的图片，使用清洗后的路径
      if (image.watermark_removed) {
        return `/data/precise_cleaned/images/${image.filename}`;
      }
      return `/data/dogs/${image.filename}`;
    } else {
      // 生产环境：仍然使用原始URL（因为GitHub Pages不包含图片文件）
      return image.url;
    }
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

  const isCleanedImages = indexData?.description?.includes('清洗') || images.some(img => img.watermark_removed);

  return (
    <div className="dog-gallery">
      <div className="gallery-header">
        <h2>
          {isCleanedImages ? '🎯 无水印狗狗图片展示' : '狗狗图片展示'}
        </h2>
        <p>
          共找到 {images.length} 张可爱的狗狗图片
          {isCleanedImages && <span className="watermark-badge">✨ 已精确清洗蓝色水印</span>}
        </p>
        {indexData?.description && (
          <p className="gallery-description">{indexData.description}</p>
        )}
      </div>
      
      <div className="masonry-container">
        {images.map((image) => (
          <div key={image.number} className="masonry-item">
            <img
              src={getImageSrc(image)}
              alt={`狗狗 ${image.number}${image.watermark_removed ? ' (无水印)' : ''}`}
              className="dog-image"
              onLoad={handleImageLoad}
              onError={handleImageError}
            />
            <div className="image-info">
              <span className="image-number">#{image.number}</span>
              <span className="image-size">{Math.round(image.size / 1024)}KB</span>
              {image.watermark_removed && (
                <span className="watermark-removed-badge">🎯 无水印</span>
              )}
            </div>
          </div>
        ))}
      </div>
      
      {isCleanedImages && (
        <div className="gallery-footer">
          <p className="tech-info">
            🔧 使用精确HSV颜色检测算法，专门清洗蓝色"Meet The dogs of Amazon"文字水印
          </p>
          <p className="tech-info">
            🛡️ 完全保护狗狗身体，其他区域零修改
          </p>
        </div>
      )}
    </div>
  );
};

export default DogGallery;