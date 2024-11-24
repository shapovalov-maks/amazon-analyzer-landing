// background.js - фоновый скрипт расширения

// Состояние подключения к API
let apiConnectionState = {
    isConnected: false,
    lastChecked: null
};

// Конфигурация
const config = {
    apiUrl: 'http://localhost:8000',
    connectionCheckInterval: 30000, // 30 секунд
    maxRetries: 3
};

// Проверка соединения с API
async function checkApiConnection() {
    try {
        const response = await fetch(`${config.apiUrl}/api/v1/health`);
        apiConnectionState.isConnected = response.ok;
        apiConnectionState.lastChecked = new Date();

        // Отправляем статус подключения всем активным popup
        chrome.runtime.sendMessage({
            action: 'apiConnectionStatus',
            status: apiConnectionState
        });

        return response.ok;
    } catch (error) {
        apiConnectionState.isConnected = false;
        apiConnectionState.lastChecked = new Date();
        return false;
    }
}

// Периодическая проверка соединения
setInterval(checkApiConnection, config.connectionCheckInterval);

// Инициализация при установке или обновлении расширения
chrome.runtime.onInstalled.addListener(async (details) => {
    if (details.reason === 'install') {
        // Действия при первой установке
        await checkApiConnection();
        // Можно добавить начальные настройки
    } else if (details.reason === 'update') {
        // Действия при обновлении
        await checkApiConnection();
    }
});

// Обработка сообщений от popup и content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getApiStatus') {
        sendResponse(apiConnectionState);
    }
    // Можно добавить другие обработчики сообщений
});

// Обработка запросов к API
async function makeApiRequest(endpoint, method = 'GET', data = null) {
    const retryOperation = async (operation, retries) => {
        try {
            return await operation();
        } catch (error) {
            if (retries > 0) {
                await new Promise(resolve => setTimeout(resolve, 1000));
                return retryOperation(operation, retries - 1);
            }
            throw error;
        }
    };

    const fetchOperation = async () => {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };

        if (data) {
            options.body = JSON.stringify(data);
        }

        const response = await fetch(`${config.apiUrl}${endpoint}`, options);

        if (!response.ok) {
            throw new Error(`API request failed: ${response.statusText}`);
        }

        return await response.json();
    };

    return retryOperation(fetchOperation, config.maxRetries);
}

// Экспорт функций для использования в popup.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'analyzeProduct') {
        makeApiRequest('/api/v1/analyze', 'POST', request.data)
            .then(result => sendResponse({ success: true, data: result }))
            .catch(error => sendResponse({ success: false, error: error.message }));
        return true; // Важно для асинхронного ответа
    }
});