from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

class ProductBase(BaseModel):
    asin: str = Field(..., description="Amazon Standard Identification Number")
    title: str = Field(..., description="Product title")
    price: float = Field(..., description="Current product price")
    currency: str = Field(default="USD", description="Price currency")

class ProductCreate(ProductBase):
    url: Optional[str] = Field(None, description="Product URL")
    description: Optional[str] = Field(None, description="Product description")
    features: Optional[List[str]] = Field(default_factory=list, description="Product features")
    rating: Optional[float] = Field(None, ge=0, le=5, description="Product rating")
    total_reviews: Optional[int] = Field(None, ge=0, description="Total number of reviews")
    bsr_rank: Optional[int] = Field(None, description="Best Sellers Rank")
    bsr_category: Optional[str] = Field(None, description="BSR Category")
    dimensions: Optional[Dict[str, float]] = Field(None, description="Product dimensions")
    weight: Optional[float] = Field(None, description="Product weight in pounds")

class ProductInDB(ProductCreate):
    id: int
    created_at: datetime
    updated_at: datetime

class Config:
    from_attributes = True
    json_schema_extra = {...}

class AnalysisRequest(BaseModel):
    product: ProductCreate
    include_ai_analysis: bool = Field(default=True, description="Whether to include AI analysis")

class CompetitionAnalysis(BaseModel):
    score: float = Field(..., ge=0, le=1, description="Competition score")
    level: str = Field(..., description="Competition level (Low/Medium/High)")
    total_competitors: int = Field(..., ge=0, description="Number of competitors")
    market_saturation: float = Field(..., ge=0, le=1, description="Market saturation score")

class ProfitAnalysis(BaseModel):
    potential_profit_margin: float = Field(..., description="Potential profit margin")
    recommended_price: float = Field(..., description="Recommended selling price")
    estimated_monthly_sales: int = Field(..., description="Estimated monthly sales")
    estimated_monthly_revenue: float = Field(..., description="Estimated monthly revenue")

class AIInsights(BaseModel):
    summary: str = Field(..., description="AI generated summary")
    opportunities: List[str] = Field(..., description="List of opportunities")
    risks: List[str] = Field(..., description="List of risks")
    recommendations: List[str] = Field(..., description="List of recommendations")

class AnalysisResponse(BaseModel):
    product_id: int
    competition_analysis: CompetitionAnalysis
    profit_analysis: ProfitAnalysis
    ai_insights: Optional[AIInsights]
    analysis_date: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "product_id": 1,
                "competition_analysis": {
                    "score": 0.7,
                    "level": "Medium",
                    "total_competitors": 15,
                    "market_saturation": 0.65
                },
                "profit_analysis": {
                    "potential_profit_margin": 0.35,
                    "recommended_price": 29.99,
                    "estimated_monthly_sales": 150,
                    "estimated_monthly_revenue": 4498.50
                },
                "ai_insights": {
                    "summary": "This product shows good potential with moderate competition.",
                    "opportunities": [
                        "Growing market segment",
                        "Underserved customer needs"
                    ],
                    "risks": [
                        "Seasonal demand fluctuations",
                        "Increasing competition"
                    ],
                    "recommendations": [
                        "Focus on product differentiation",
                        "Optimize pricing strategy"
                    ]
                }
            }
        }