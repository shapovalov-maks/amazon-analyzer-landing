// popup.js - скрипт для управления popup окном расширения

class PopupManager {
    constructor() {
        this.elements = {
            analyzeButton: document.getElementById('analyzeButton'),
            loadingSpinner: document.getElementById('loadingSpinner'),
            resultsContainer: document.getElementById('resultsContainer'),
            errorMessage: document.getElementById('errorMessage'),
            connectionStatus: document.getElementById('connectionStatus'),
            settingsButton: document.getElementById('settingsButton'),

            // Элементы результатов анализа
            competitionScore: document.getElementById('competitionScore'),
            competitionProgress: document.getElementById('competitionProgress'),
            marketSaturation: document.getElementById('marketSaturation'),
            saturationProgress: document.getElementById('saturationProgress'),
            profitPotential: document.getElementById('profitPotential'),
            monthlySales: document.getElementById('monthlySales'),
            aiSummary: document.getElementById('aiSummary'),
            aiOpportunities: document.getElementById('aiOpportunities'),
            aiRecommendations: document.getElementById('aiRecommendations')
        };

        this.state = {
            isAnalyzing: false,
            isConnected: false,
            currentTab: null
        };

        this.initialize();
    }

    async initialize() {
        this.attachEventListeners();
        await this.checkApiConnection();
        await this.getCurrentTab();
    }

    attachEventListeners() {
        this.elements.analyzeButton.addEventListener('click', () => this.handleAnalyzeClick());
        this.elements.settingsButton.addEventListener('click', () => this.openSettings());
    }

    async getCurrentTab() {
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
        this.state.currentTab = tab;
        this.updateUI();
    }

    async checkApiConnection() {
        try {
            const response = await chrome.runtime.sendMessage({ action: 'getApiStatus' });
            this.state.isConnected = response.isConnected;
            this.updateConnectionStatus();
        } catch (error) {
            this.state.isConnected = false;
            this.updateConnectionStatus();
        }
    }

    updateConnectionStatus() {
        const statusElement = this.elements.connectionStatus;
        if (this.state.isConnected) {
            statusElement.classList.add('connected');
            statusElement.querySelector('.status-text').textContent = 'Connected';
        } else {
            statusElement.classList.remove('connected');
            statusElement.querySelector('.status-text').textContent = 'Disconnected';
        }
    }

    async handleAnalyzeClick() {
        if (this.state.isAnalyzing) return;

        try {
            this.startAnalysis();

            // Получаем данные о продукте
            const productData = await this.extractProductData();
            if (!productData.success) {
                throw new Error(productData.error || 'Failed to extract product data');
            }

            // Отправляем данные на анализ
            const analysis = await this.analyzeProduct(productData.data);
            if (!analysis.success) {
                throw new Error(analysis.error || 'Failed to analyze product');
            }

            // Отображаем результаты
            this.displayResults(analysis.data);
        } catch (error) {
            this.showError(error.message);
        } finally {
            this.endAnalysis();
        }
    }

    async extractProductData() {
        return await chrome.tabs.sendMessage(
            this.state.currentTab.id,
            { action: 'extractProductData' }
        );
    }

    async analyzeProduct(productData) {
        return await chrome.runtime.sendMessage({
            action: 'analyzeProduct',
            data: productData
        });
    }

    startAnalysis() {
        this.state.isAnalyzing = true;
        this.elements.analyzeButton.disabled = true;
        this.elements.loadingSpinner.style.display = 'block';
        this.elements.resultsContainer.classList.add('hidden');
        this.elements.errorMessage.classList.add('hidden');
    }

    endAnalysis() {
        this.state.isAnalyzing = false;
        this.elements.analyzeButton.disabled = false;
        this.elements.loadingSpinner.style.display = 'none';
    }

    displayResults(analysis) {
        // Отображение оценки конкуренции
        this.elements.competitionScore.textContent =
            `${(analysis.competition_analysis.score * 100).toFixed(0)}%`;
        this.elements.competitionProgress.style.width =
            `${analysis.competition_analysis.score * 100}%`;

        // Отображение насыщенности рынка
        this.elements.marketSaturation.textContent =
            `${(analysis.competition_analysis.market_saturation * 100).toFixed(0)}%`;
        this.elements.saturationProgress.style.width =
            `${analysis.competition_analysis.market_saturation * 100}%`;

        // Отображение потенциала прибыли
        this.elements.profitPotential.textContent =
            `${(analysis.profit_analysis.potential_profit_margin * 100).toFixed(1)}%`;
        this.elements.monthlySales.textContent =
            `$${analysis.profit_analysis.estimated_monthly_revenue.toLocaleString()}`;

        // Отображение AI инсайтов
        if (analysis.ai_insights) {
            this.elements.aiSummary.textContent = analysis.ai_insights.summary;

            // Очищаем и заполняем возможности
            this.elements.aiOpportunities.innerHTML = '';
            analysis.ai_insights.opportunities.forEach(opportunity => {
                const li = document.createElement('li');
                li.textContent = opportunity;
                this.elements.aiOpportunities.appendChild(li);
            });

            // Очищаем и заполняем рекомендации
            this.elements.aiRecommendations.innerHTML = '';
            analysis.ai_insights.recommendations.forEach(recommendation => {
                const li = document.createElement('li');
                li.textContent = recommendation;
                this.elements.aiRecommendations.appendChild(li);
            });
        }

        this.elements.resultsContainer.classList.remove('hidden');
    }

    showError(message) {
        this.elements.errorMessage.classList.remove('hidden');
        this.elements.errorMessage.querySelector('.error-text').textContent = message;
    }

    updateUI() {
        const isAmazonProduct = this.state.currentTab?.url?.includes('amazon.com/');
        this.elements.analyzeButton.disabled = !isAmazonProduct;

        if (!isAmazonProduct) {
            this.showError('Please navigate to an Amazon product page to use this extension.');
        }
    }

    openSettings() {
        // Здесь можно добавить логику открытия страницы настроек
        chrome.runtime.openOptionsPage();
    }

    // Форматирование чисел для отображения
    formatNumber(number, decimals = 0) {
        return number.toLocaleString(undefined, {
            minimumFractionDigits: decimals,
            maximumFractionDigits: decimals
        });
    }

    // Форматирование цены
    formatPrice(price) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(price);
    }

    // Обработка различных статусов анализа
    updateAnalysisStatus(status) {
        const statusClasses = {
            good: 'text-success',
            warning: 'text-warning',
            bad: 'text-error'
        };

        return {
            class: statusClasses[status] || statusClasses.warning,
            icon: status === 'good' ? '✔️' : status === 'bad' ? '❌' : '⚠️'
        };
    }

    // Анимация прогресс-баров
    animateProgressBar(element, value, duration = 1000) {
        const start = parseFloat(element.style.width) || 0;
        const end = value * 100;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const current = start + (end - start) * progress;
            element.style.width = `${current}%`;

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    // Экспорт результатов анализа
    exportAnalysis(analysis) {
        const data = {
            timestamp: new Date().toISOString(),
            product: analysis.product,
            analysis: {
                competition: analysis.competition_analysis,
                profit: analysis.profit_analysis,
                insights: analysis.ai_insights
            }
        };

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = `analysis-${analysis.product.asin}-${Date.now()}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
}

// Инициализация при загрузке popup
document.addEventListener('DOMContentLoaded', () => {
    const popup = new PopupManager();
});

// Обработка сообщений от background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'apiConnectionStatus') {
        document.querySelector('#connectionStatus').classList.toggle('connected', message.status.isConnected);
        document.querySelector('#connectionStatus .status-text').textContent =
            message.status.isConnected ? 'Connected' : 'Disconnected';
    }
});