# Amazon Dogs - Dog Image Downloader

A simple open-source tool for downloading dog images from Amazon's 404 error pages.

## What is this project?

This project downloads dog images that appear on Amazon's error pages. These images are accessible via predictable URLs like:
- https://images-na.ssl-images-amazon.com/images/G/01/error/1._TTD_.jpg
- https://images-na.ssl-images-amazon.com/images/G/01/error/2._TTD_.jpg
- And so on...

The project includes 200 pre-downloaded dog images ready to use.

## How to use the downloaded images?

### Option 1: Clone the entire repository

```bash
git clone https://github.com/good-sellers/amazon-dogs.git
cd amazon-dogs
```

The downloaded images are located in `data/cleaned_dogs/images/`:
- 200 dog images (cleaned_dog_1.jpg to cleaned_dog_200.jpg)
- Index file: `data/cleaned_dogs/cleaned_index.json`

### Option 2: Download images only

You can download just the images from the repository without cloning the entire codebase.

## How does it work?

The downloader works by:

1. **URL Pattern**: Amazon uses a predictable URL pattern for error page images
   - Base URL: `https://images-na.ssl-images-amazon.com/images/G/01/error/`
   - File format: `{number}._TTD_.jpg` (starting from 1)

2. **Sequential Fetching**: The crawler tries image URLs in sequence (1, 2, 3, 4...)

3. **Smart Stopping**: Stops when:
   - Reaches max number of images (default: 1000)
   - Gets 100 consecutive 404 errors
   - 3-second delay between requests to avoid rate limiting

4. **Image Storage**: Successfully downloaded images are saved to `data/dogs/` with an index file

## Optional: Run the crawler yourself

If you want to download more images:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the crawler
python dog_crawler.py
```

## License

MIT License