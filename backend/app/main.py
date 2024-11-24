from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from .models import (
    ProductCreate,
    AnalysisRequest,
    AnalysisResponse,
    CompetitionAnalysis,
    ProfitAnalysis,
    AIInsights
)
from .utils import AmazonAnalyzer, DataValidator, MarketAnalyzer
from .config import settings
from datetime import datetime
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация FastAPI приложения
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="API for Amazon Product Analysis"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Инициализация анализаторов
amazon_analyzer = AmazonAnalyzer()
market_analyzer = MarketAnalyzer()


@app.get("/")
async def read_root():
    """Корневой эндпоинт"""
    return {
        "message": "Welcome to Amazon Product Analyzer API",
        "version": "1.0.0",
        "status": "active"
    }


@app.post("/api/v1/analyze", response_model=AnalysisResponse)
async def analyze_product(request: AnalysisRequest):
    """
    Анализ продукта Amazon
    """
    try:
        logger.info(f"Starting analysis for product: {request.product.asin}")

        # Валидация данных
        product_data = request.product.dict()

        # Анализ конкуренции
        competition_data = await amazon_analyzer.analyze_competition(product_data)
        competition_analysis = CompetitionAnalysis(**competition_data)

        # Анализ прибыльности
        profit_data = await amazon_analyzer.analyze_profit_potential(product_data)
        profit_analysis = ProfitAnalysis(**profit_data)

        # AI анализ (если запрошен)
        ai_insights = None
        if request.include_ai_analysis:
            ai_data = await amazon_analyzer.get_ai_insights(product_data)
            ai_insights = AIInsights(**ai_data)

        # Формируем ответ
        response = AnalysisResponse(
            product_id=hash(request.product.asin),  # Временный ID
            competition_analysis=competition_analysis,
            profit_analysis=profit_analysis,
            ai_insights=ai_insights,
            analysis_date=datetime.utcnow()
        )

        logger.info(f"Analysis completed successfully for product: {request.product.asin}")
        return response

    except Exception as e:
        logger.error(f"Error analyzing product: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing product: {str(e)}"
        )


@app.get("/api/v1/health")
async def health_check():
    """
    Проверка здоровья API
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)