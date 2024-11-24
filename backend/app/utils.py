from typing import Dict, List, Optional
import openai
from .config import settings
import aiohttp
import json
import re
from datetime import datetime


class AmazonAnalyzer:
    def __init__(self):
        self.openai = openai
        self.openai.api_key = settings.OPENAI_API_KEY

    async def analyze_competition(self, product_data: Dict) -> Dict:
        """Анализ конкуренции на основе данных о продукте"""
        competitors_score = self._calculate_competition_score(product_data)
        market_saturation = self._calculate_market_saturation(product_data)

        return {
            "score": competitors_score,
            "level": self._get_competition_level(competitors_score),
            "total_competitors": self._estimate_competitors(product_data),
            "market_saturation": market_saturation
        }

    async def analyze_profit_potential(self, product_data: Dict) -> Dict:
        """Анализ потенциальной прибыльности"""
        margin = self._calculate_potential_margin(product_data)
        monthly_sales = self._estimate_monthly_sales(product_data)
        recommended_price = self._calculate_recommended_price(product_data)

        return {
            "potential_profit_margin": margin,
            "recommended_price": recommended_price,
            "estimated_monthly_sales": monthly_sales,
            "estimated_monthly_revenue": monthly_sales * recommended_price
        }

    async def get_ai_insights(self, product_data: Dict) -> Dict:
        """Получение аналитических выводов от AI"""
        try:
            prompt = self._create_analysis_prompt(product_data)
            response = await self.openai.ChatCompletion.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": """
                    Ты эксперт по анализу Amazon продуктов и рынка. 
                    Проанализируй данные и предоставь структурированные рекомендации.
                    Фокусируйся на конкретных, действенных советах."""},
                    {"role": "user", "content": prompt}
                ]
            )

            insights = self._parse_ai_response(response.choices[0].message.content)
            return insights
        except Exception as e:
            print(f"Error getting AI insights: {str(e)}")
            return self._get_fallback_insights()

    def _calculate_competition_score(self, data: Dict) -> float:
        """Расчет оценки конкуренции"""
        base_score = 0.5
        factors = {
            'reviews': self._normalize_review_count(data.get('total_reviews', 0)),
            'rating': self._normalize_rating(data.get('rating', 0)),
            'bsr': self._normalize_bsr(data.get('bsr_rank', 0))
        }

        weighted_score = (
                factors['reviews'] * 0.4 +
                factors['rating'] * 0.3 +
                factors['bsr'] * 0.3
        )

        return round(min(max(weighted_score, 0), 1), 2)

    def _normalize_review_count(self, reviews: int) -> float:
        """Нормализация количества отзывов"""
        if reviews == 0:
            return 0
        return min(1, reviews / 1000)

    def _normalize_rating(self, rating: float) -> float:
        """Нормализация рейтинга"""
        return rating / 5 if rating else 0

    def _normalize_bsr(self, bsr: int) -> float:
        """Нормализация Best Seller Rank"""
        if bsr == 0:
            return 0
        return 1 - min(1, bsr / 100000)

    def _get_competition_level(self, score: float) -> str:
        """Определение уровня конкуренции"""
        if score < 0.3:
            return "Low"
        elif score < 0.7:
            return "Medium"
        return "High"

    def _estimate_competitors(self, data: Dict) -> int:
        """Оценка количества конкурентов"""
        base_competitors = 10
        if data.get('bsr_rank'):
            base_competitors += min(50, data['bsr_rank'] // 1000)
        if data.get('total_reviews'):
            base_competitors += min(30, data['total_reviews'] // 100)
        return base_competitors

    def _calculate_market_saturation(self, data: Dict) -> float:
        """Расчет насыщенности рынка"""
        saturation_score = 0.5
        if data.get('bsr_rank'):
            saturation_score += 0.3 * (1 - min(1, data['bsr_rank'] / 100000))
        if data.get('total_reviews'):
            saturation_score += 0.2 * min(1, data['total_reviews'] / 1000)
        return round(min(max(saturation_score, 0), 1), 2)

    def _create_analysis_prompt(self, data: Dict) -> str:
        """Создание промпта для AI анализа"""
        return f"""
        Проанализируй следующий Amazon продукт:

        Название: {data.get('title')}
        Цена: ${data.get('price')}
        Рейтинг: {data.get('rating')}⭐ ({data.get('total_reviews', 0)} отзывов)
        BSR: {data.get('bsr_rank', 'N/A')} в {data.get('bsr_category', 'категории')}

        Особенности продукта:
        {self._format_features(data.get('features', []))}

        Предоставь структурированный анализ, включающий:
        1. Краткое резюме потенциала продукта
        2. Основные возможности на рынке
        3. Потенциальные риски
        4. Конкретные рекомендации по улучшению позиции на рынке
        """

    def _format_features(self, features: List[str]) -> str:
        """Форматирование особенностей продукта"""
        if not features:
            return "Информация о характеристиках отсутствует"
        return "\n".join(f"- {feature}" for feature in features)

    def _get_fallback_insights(self) -> Dict:
        """Запасные инсайты в случае ошибки AI"""
        return {
            "summary": "Базовый анализ продукта на основе доступных данных.",
            "opportunities": [
                "Изучите возможности улучшения листинга",
                "Рассмотрите оптимизацию ценообразования"
            ],
            "risks": [
                "Проведите дополнительное исследование конкурентов",
                "Оцените сезонность спроса"
            ],
            "recommendations": [
                "Соберите больше данных о рынке",
                "Проанализируйте отзывы конкурентов"
            ]
        }

    def _parse_ai_response(self, response: str) -> Dict:
        """Парсинг ответа AI в структурированный формат"""
        sections = {
            "summary": "",
            "opportunities": [],
            "risks": [],
            "recommendations": []
        }

        current_section = "summary"
        lines = response.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if "возможности" in line.lower():
                current_section = "opportunities"
                continue
            elif "риски" in line.lower():
                current_section = "risks"
                continue
            elif "рекомендации" in line.lower():
                current_section = "recommendations"
                continue

            if current_section == "summary":
                sections["summary"] += line + " "
            elif line.startswith("-") or line.startswith("*"):
                sections[current_section].append(line.lstrip("- *"))

        return sections


class DataValidator:
    """Класс для валидации и очистки данных"""

    @staticmethod
    def clean_price(price_str: str) -> Optional[float]:
        """Очистка и валидация цены"""
        if not price_str:
            return None
        try:
            # Удаляем все символы кроме цифр и точки
            clean_price = re.sub(r'[^\d.]', '', price_str)
            return float(clean_price)
        except ValueError:
            return None

    @staticmethod
    def clean_rating(rating_str: str) -> Optional[float]:
        """Очистка и валидация рейтинга"""
        if not rating_str:
            return None
        try:
            # Извлекаем число из строки (например, "4.5 out of 5")
            rating_match = re.search(r'(\d+\.?\d*)', rating_str)
            if rating_match:
                rating = float(rating_match.group(1))
                # Продолжение класса DataValidator в utils.py
                if 0 <= rating <= 5:
                    return rating
            return None
        except ValueError:
            return None

    @staticmethod
    def clean_reviews_count(reviews_str: str) -> Optional[int]:
        """Очистка и валидация количества отзывов"""
        if not reviews_str:
            return None
        try:
            # Удаляем запятые и извлекаем число
            clean_count = re.sub(r'[^\d]', '', reviews_str)
            return int(clean_count) if clean_count else None
        except ValueError:
            return None

    @staticmethod
    def clean_bsr(bsr_str: str) -> Optional[int]:
        """Очистка и валидация BSR (Best Sellers Rank)"""
        if not bsr_str:
            return None
        try:
            # Извлекаем первое число из строки BSR
            bsr_match = re.search(r'#?([\d,]+)', bsr_str)
            if bsr_match:
                bsr = int(bsr_match.group(1).replace(',', ''))
                return bsr
            return None
        except ValueError:
            return None

    @staticmethod
    def extract_dimensions(dimension_str: str) -> Optional[Dict[str, float]]:
        """Извлечение размеров продукта"""
        if not dimension_str:
            return None
        try:
            # Ищем числа с единицами измерения
            dims = re.findall(r'([\d.]+)\s*(inches|in|cm|mm)', dimension_str.lower())
            if len(dims) >= 3:
                return {
                    'length': float(dims[0][0]),
                    'width': float(dims[1][0]),
                    'height': float(dims[2][0]),
                    'unit': dims[0][1]
                }
            return None
        except ValueError:
            return None


class MarketAnalyzer:
    """Класс для анализа рыночных данных"""

    @staticmethod
    def calculate_market_size(bsr: int, category: str) -> Dict[str, any]:
        """Расчет размера рынка на основе BSR и категории"""
        # Базовые коэффициенты для разных категорий
        category_coefficients = {
            'Electronics': 0.8,
            'Home & Kitchen': 0.7,
            'Sports & Outdoors': 0.6,
            'Beauty & Personal Care': 0.75,
            'Toys & Games': 0.65,
            'default': 0.5
        }

        coef = category_coefficients.get(category, category_coefficients['default'])

        # Расчет примерного объема продаж
        if bsr < 1000:
            daily_sales = 100 * coef
        elif bsr < 5000:
            daily_sales = 50 * coef
        elif bsr < 10000:
            daily_sales = 20 * coef
        else:
            daily_sales = max(5, 1000000 / bsr) * coef

        monthly_sales = daily_sales * 30

        return {
            'daily_sales': round(daily_sales, 2),
            'monthly_sales': round(monthly_sales, 2),
            'market_strength': 'High' if bsr < 1000 else 'Medium' if bsr < 10000 else 'Low'
        }

    @staticmethod
    def analyze_price_point(price: float, category: str) -> Dict[str, any]:
        """Анализ ценовой точки"""
        # Оптимальные ценовые диапазоны по категориям
        price_ranges = {
            'Electronics': {'low': 20, 'medium': 50, 'high': 100},
            'Home & Kitchen': {'low': 15, 'medium': 35, 'high': 70},
            'Sports & Outdoors': {'low': 15, 'medium': 40, 'high': 80},
            'Beauty & Personal Care': {'low': 10, 'medium': 25, 'high': 50},
            'Toys & Games': {'low': 10, 'medium': 30, 'high': 60},
            'default': {'low': 15, 'medium': 35, 'high': 70}
        }

        ranges = price_ranges.get(category, price_ranges['default'])

        if price <= ranges['low']:
            price_position = 'low'
            recommendation = 'Consider increasing price if quality permits'
        elif price <= ranges['medium']:
            price_position = 'medium'
            recommendation = 'Price point is optimal'
        elif price <= ranges['high']:
            price_position = 'high'
            recommendation = 'Consider value-added features to justify price'
        else:
            price_position = 'premium'
            recommendation = 'Ensure premium positioning is well-justified'

        return {
            'price_position': price_position,
            'recommendation': recommendation,
            'optimal_range': {
                'min': ranges['low'],
                'max': ranges['high']
            }
        }

    @staticmethod
    def calculate_seasonal_trend(historical_data: List[Dict]) -> Dict[str, any]:
        """Расчет сезонности на основе исторических данных"""
        if not historical_data:
            return {
                'seasonality': 'Unknown',
                'peak_months': [],
                'low_months': []
            }

        # Группировка данных по месяцам
        monthly_sales = {}
        for data in historical_data:
            month = data['date'].month
            sales = data.get('sales', 0)
            monthly_sales[month] = monthly_sales.get(month, []) + [sales]

        # Расчет средних продаж по месяцам
        avg_monthly_sales = {
            month: sum(sales) / len(sales)
            for month, sales in monthly_sales.items()
        }

        # Определение пиковых и низких месяцев
        avg_sales = sum(avg_monthly_sales.values()) / len(avg_monthly_sales)
        peak_months = [
            month for month, sales in avg_monthly_sales.items()
            if sales > avg_sales * 1.2
        ]
        low_months = [
            month for month, sales in avg_monthly_sales.items()
            if sales < avg_sales * 0.8
        ]

        # Определение уровня сезонности
        if len(peak_months) >= 3 or len(low_months) >= 3:
            seasonality = 'High'
        elif len(peak_months) >= 1 or len(low_months) >= 1:
            seasonality = 'Medium'
        else:
            seasonality = 'Low'

        return {
            'seasonality': seasonality,
            'peak_months': peak_months,
            'low_months': low_months,
            'monthly_trends': avg_monthly_sales
        }