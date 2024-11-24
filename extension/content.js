// content.js - скрипт для извлечения данных с Amazon страницы

class AmazonDataExtractor {
    constructor() {
        this.productData = null;
    }

    // Основной метод извлечения данных
    async extractProductData() {
        if (!this.isProductPage()) {
            throw new Error('Not a product page');
        }

        try {
            this.productData = {
                asin: this.getASIN(),
                title: this.getTitle(),
                price: this.getPrice(),
                rating: this.getRating(),
                totalReviews: this.getReviewsCount(),
                bsr: this.getBestSellersRank(),
                bsrCategory: this.getBSRCategory(),
                features: this.getFeatures(),
                description: this.getDescription(),
                images: this.getImages(),
                dimensions: this.getDimensions(),
                weight: this.getWeight(),
                dateFirstAvailable: this.getDateFirstAvailable(),
                url: window.location.href
            };

            return this.productData;
        } catch (error) {
            console.error('Error extracting product data:', error);
            throw error;
        }
    }

    // Проверка, является ли страница страницей продукта
    isProductPage() {
        return !!document.getElementById('dp') ||
               !!document.getElementById('productTitle');
    }

    // Получение ASIN
    getASIN() {
        const asinElement = document.getElementById('ASIN');
        if (asinElement) {
            return asinElement.value;
        }

        // Альтернативный метод получения ASIN из URL
        const asinMatch = window.location.pathname.match(/\/([A-Z0-9]{10})(\/|$|\?)/);
        return asinMatch ? asinMatch[1] : null;
    }

    // Получение заголовка продукта
    getTitle() {
        const titleElement = document.getElementById('productTitle');
        return titleElement ? titleElement.textContent.trim() : null;
    }

    // Получение цены
    getPrice() {
        const priceElements = [
            document.getElementById('priceblock_ourprice'),
            document.getElementById('priceblock_saleprice'),
            document.querySelector('.a-price .a-offscreen')
        ];

        for (const element of priceElements) {
            if (element) {
                const price = element.textContent.trim().replace(/[^0-9.]/g, '');
                return parseFloat(price);
            }
        }

        return null;
    }

    // Получение рейтинга
    getRating() {
        const ratingElement = document.getElementById('acrPopover');
        if (ratingElement) {
            const ratingText = ratingElement.title;
            const rating = parseFloat(ratingText.replace(/[^0-9.]/g, ''));
            return !isNaN(rating) ? rating : null;
        }
        return null;
    }

    // Получение количества отзывов
    getReviewsCount() {
        const reviewsElement = document.getElementById('acrCustomerReviewText');
        if (reviewsElement) {
            const count = reviewsElement.textContent.replace(/[^0-9]/g, '');
            return parseInt(count) || 0;
        }
        return 0;
    }

    // Получение Best Sellers Rank
    getBestSellersRank() {
        const bsrElements = document.querySelectorAll('#productDetails_detailBullets_sections1 th, #detailBullets_feature_div li');
        for (const element of bsrElements) {
            if (element.textContent.includes('Best Sellers Rank')) {
                const bsrMatch = element.textContent.match(/#([0-9,]+)/);
                if (bsrMatch) {
                    return parseInt(bsrMatch[1].replace(/,/g, ''));
                }
            }
        }
        return null;
    }

    // Получение категории BSR
    getBSRCategory() {
        const bsrElements = document.querySelectorAll('#productDetails_detailBullets_sections1 th, #detailBullets_feature_div li');
        for (const element of bsrElements) {
            if (element.textContent.includes('Best Sellers Rank')) {
                const categoryMatch = element.textContent.match(/in\s([^)]+)/);
                return categoryMatch ? categoryMatch[1].trim() : null;
            }
        }
        return null;
    }

    // Получение особенностей продукта
    getFeatures() {
        const features = [];
        const featureElements = document.querySelectorAll('#feature-bullets li');
        featureElements.forEach(element => {
            const text = element.textContent.trim();
            if (text && !text.includes('Secure transaction')) {
                features.push(text);
            }
        });
        return features;
    }

    // Получение описания продукта
    getDescription() {
        const descriptionElement = document.getElementById('productDescription');
        return descriptionElement ? descriptionElement.textContent.trim() : null;
    }

    // Получение изображений продукта
    getImages() {
        const images = [];
        const imageElements = document.querySelectorAll('#altImages img');
        imageElements.forEach(img => {
            const src = img.getAttribute('src');
            if (src && !src.includes('spinner')) {
                // Преобразуем URL миниатюры в URL полноразмерного изображения
                const fullSizeUrl = src.replace(/\._.*_\./, '.');
                images.push(fullSizeUrl);
            }
        });
        return images;
    }

    // Получение размеров продукта
    getDimensions() {
        const dimensionsElements = document.querySelectorAll('#productDetails_detailBullets_sections1 th, #detailBullets_feature_div li');
        for (const element of dimensionsElements) {
            if (element.textContent.includes('Product Dimensions') ||
                element.textContent.includes('Package Dimensions')) {
                const dimensions = element.textContent.match(/(\d+(\.\d+)?)\s*x\s*(\d+(\.\d+)?)\s*x\s*(\d+(\.\d+)?)/);
                if (dimensions) {
                    return {
                        length: parseFloat(dimensions[1]),
                        width: parseFloat(dimensions[3]),
                        height: parseFloat(dimensions[5])
                    };
                }
            }
        }
        return null;
    }

    // Получение веса продукта
    getWeight() {
        const weightElements = document.querySelectorAll('#productDetails_detailBullets_sections1 th, #detailBullets_feature_div li');
        for (const element of weightElements) {
            if (element.textContent.includes('Item Weight')) {
                const weightMatch = element.textContent.match(/(\d+(\.\d+)?)\s*(ounces|pounds|oz|lbs)/i);
                if (weightMatch) {
                    let weight = parseFloat(weightMatch[1]);
                    // Конвертируем все в фунты
                    if (weightMatch[3].toLowerCase().includes('ounce') ||
                        weightMatch[3].toLowerCase().includes('oz')) {
                        weight /= 16;
                    }
                    return weight;
                }
            }
        }
        return null;
    }

    // Получение даты первого появления в продаже
    getDateFirstAvailable() {
        const dateElements = document.querySelectorAll('#productDetails_detailBullets_sections1 th, #detailBullets_feature_div li');
        for (const element of dateElements) {
            if (element.textContent.includes('Date First Available')) {
                const dateMatch = element.textContent.match(/:\s*(.+)/);
                return dateMatch ? dateMatch[1].trim() : null;
            }
        }
        return null;
    }
}

// Слушатель сообщений от popup.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extractProductData') {
        const extractor = new AmazonDataExtractor();
        extractor.extractProductData()
            .then(data => sendResponse({ success: true, data }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Важно для асинхронного ответа
    }
});