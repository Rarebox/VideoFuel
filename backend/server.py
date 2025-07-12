from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
import httpx
import json
import re

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="VideoFuel AI", description="AI Toolkit for YouTube Creators")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# LLM Model Configuration
SUPPORTED_MODELS = {
    "deephermes2pro": "nousresearch/hermes-2-pro-llama-3-8b",
    "mixtral": "mistralai/mixtral-8x22b-instruct",
    "gpt4o": "openai/gpt-4o"
}

# Pydantic Models
class GenerationRequest(BaseModel):
    topic: str
    language: str = "en"  # "en" or "tr"
    model: str = "deephermes2pro"

class TitleGenerationResponse(BaseModel):
    titles: List[str]
    language: str
    model_used: str

class DescriptionRequest(BaseModel):
    title: str
    language: str = "en"
    model: str = "deephermes2pro"

class DescriptionResponse(BaseModel):
    description: str
    hashtags: List[str]
    language: str
    model_used: str

class ScriptRequest(BaseModel):
    title: str
    language: str = "en"
    video_length_minutes: int = 5
    model: str = "deephermes2pro"

class ScriptResponse(BaseModel):
    hook: str
    sections: List[Dict[str, str]]
    outro: str
    language: str
    model_used: str

class ThumbnailRequest(BaseModel):
    title: str
    language: str = "en"
    model: str = "deephermes2pro"

class ThumbnailResponse(BaseModel):
    thumbnail_texts: List[str]
    language: str
    model_used: str

class SEORequest(BaseModel):
    title: str
    description: str
    hashtags: List[str]
    language: str = "en"

class SEOScores(BaseModel):
    clickbait_score: int
    keyword_relevance_score: int
    length_score: int
    overall_seo_score: int

class SEOResponse(BaseModel):
    scores: SEOScores
    recommendations: List[str]

# OpenRouter API Client
async def query_openrouter(model: str, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 2000):
    """Query OpenRouter API with specified model"""
    headers = {
        "Authorization": f"Bearer {os.environ.get('OPENROUTER_API_KEY')}",
        "HTTP-Referer": "https://videofuel.ai",
        "X-Title": "VideoFuel AI"
    }
    
    payload = {
        "model": SUPPORTED_MODELS[model],
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=500, detail=f"OpenRouter API error: {response.text}")
            
            result = response.json()
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logging.error(f"OpenRouter API error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"LLM generation failed: {str(e)}")

# Helper Functions
def get_language_prompts(language: str):
    """Get language-specific system prompts"""
    if language == "tr":
        return {
            "system": "Sen YouTube içerik üreticileri için uzman bir AI asistanısın. Türkçe içerik üreteceksin.",
            "title_prompt": "YouTube videosu için 5 adet SEO-optimized başlık üret. Her başlık 50-70 karakter arası olmalı, dikkat çekici ve tıklanabilir olmalı.",
            "description_prompt": "Verilen başlık için 2-3 cümlelik açıklayıcı paragraf ve 10-15 adet hashtag üret.",
            "script_prompt": "Verilen başlık için yapılandırılmış video senaryosu üret. Hook (15-30 saniye), ana bölümler ve outro içermeli.",
            "thumbnail_prompt": "Verilen başlık için thumbnail'da kullanılabilecek 3 adet kısa metin önerisi (2-5 kelime) üret."
        }
    else:
        return {
            "system": "You are an expert AI assistant for YouTube content creators. Generate content in English.",
            "title_prompt": "Generate 5 SEO-optimized YouTube video titles. Each title should be 50-70 characters, catchy and clickable.",
            "description_prompt": "Generate a descriptive paragraph (2-3 sentences) and 10-15 hashtags for the given title.",
            "script_prompt": "Generate a structured video script for the given title. Include hook (15-30 seconds), main sections, and outro.",
            "thumbnail_prompt": "Generate 3 short text suggestions (2-5 words) for thumbnail design based on the given title."
        }

def calculate_seo_scores(title: str, description: str, hashtags: List[str], language: str) -> SEOScores:
    """Calculate SEO scores for content"""
    
    # Clickbait Score (0-100)
    clickbait_words = ["amazing", "incredible", "shocking", "ultimate", "secret", "revealed", 
                       "must-see", "unbelievable", "epic", "insane"] if language == "en" else [
                       "inanılmaz", "muhteşem", "şok", "son", "gizli", "açığa çıktı", 
                       "mutlaka izle", "inanılmaz", "epik", "çılgın"]
    
    clickbait_score = min(100, len([word for word in clickbait_words if word.lower() in title.lower()]) * 20 + 40)
    
    # Length Score (0-100)
    title_length = len(title)
    if 50 <= title_length <= 70:
        length_score = 100
    elif 40 <= title_length <= 80:
        length_score = 80
    else:
        length_score = max(0, 100 - abs(60 - title_length) * 3)
    
    # Keyword Relevance Score (based on hashtag relevance)
    title_words = set(title.lower().split())
    hashtag_words = set(" ".join(hashtags).lower().replace("#", "").split())
    common_words = title_words.intersection(hashtag_words)
    keyword_relevance_score = min(100, len(common_words) * 15 + 30)
    
    # Overall SEO Score
    overall_seo_score = int((clickbait_score + length_score + keyword_relevance_score) / 3)
    
    return SEOScores(
        clickbait_score=clickbait_score,
        keyword_relevance_score=keyword_relevance_score,
        length_score=length_score,
        overall_seo_score=overall_seo_score
    )

# API Routes
@api_router.get("/")
async def root():
    return {"message": "VideoFuel AI - YouTube Creator Toolkit", "version": "1.0.0"}

@api_router.get("/models")
async def get_available_models():
    return {"models": list(SUPPORTED_MODELS.keys())}

@api_router.post("/generate-titles", response_model=TitleGenerationResponse)
async def generate_titles(request: GenerationRequest):
    """Generate 5 SEO-optimized YouTube titles"""
    prompts = get_language_prompts(request.language)
    
    messages = [
        {"role": "system", "content": prompts["system"]},
        {"role": "user", "content": f"{prompts['title_prompt']}\n\nKonu: {request.topic}\n\nSadece 5 başlığı liste halinde ver, her satırda bir başlık."}
    ]
    
    try:
        response = await query_openrouter(request.model, messages)
        titles = [line.strip().lstrip('1234567890.-) ') for line in response.split('\n') if line.strip()][:5]
        
        # Store in database
        await db.generations.insert_one({
            "id": str(uuid.uuid4()),
            "type": "titles",
            "topic": request.topic,
            "language": request.language,
            "model": request.model,
            "titles": titles,
            "timestamp": datetime.utcnow()
        })
        
        return TitleGenerationResponse(
            titles=titles,
            language=request.language,
            model_used=SUPPORTED_MODELS[request.model]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate-description", response_model=DescriptionResponse)
async def generate_description(request: DescriptionRequest):
    """Generate description and hashtags for a title"""
    prompts = get_language_prompts(request.language)
    
    messages = [
        {"role": "system", "content": prompts["system"]},
        {"role": "user", "content": f"{prompts['description_prompt']}\n\nBaşlık: {request.title}\n\nÇıktı formatı:\nAÇIKLAMA: [2-3 cümlelik açıklama]\nHASHTAGLAR: #tag1 #tag2 #tag3..."}
    ]
    
    try:
        response = await query_openrouter(request.model, messages, temperature=0.8)
        
        # Parse response
        lines = response.split('\n')
        description = ""
        hashtags = []
        
        for line in lines:
            if line.startswith('AÇIKLAMA:') or line.startswith('DESCRIPTION:'):
                description = line.split(':', 1)[1].strip()
            elif line.startswith('HASHTAG') or '#' in line:
                hashtag_text = line.split(':', 1)[-1].strip()
                hashtags = [tag.strip() for tag in hashtag_text.split() if tag.startswith('#')]
        
        if not description:
            description = response.strip()
        if not hashtags:
            hashtags = re.findall(r'#\w+', response)
        
        # Store in database
        await db.generations.insert_one({
            "id": str(uuid.uuid4()),
            "type": "description",
            "title": request.title,
            "language": request.language,
            "model": request.model,
            "description": description,
            "hashtags": hashtags,
            "timestamp": datetime.utcnow()
        })
        
        return DescriptionResponse(
            description=description,
            hashtags=hashtags,
            language=request.language,
            model_used=SUPPORTED_MODELS[request.model]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate-script", response_model=ScriptResponse)
async def generate_script(request: ScriptRequest):
    """Generate structured video script"""
    prompts = get_language_prompts(request.language)
    
    messages = [
        {"role": "system", "content": prompts["system"]},
        {"role": "user", "content": f"{prompts['script_prompt']}\n\nBaşlık: {request.title}\nVideo Süresi: {request.video_length_minutes} dakika\n\nÇıktı formatı:\nHOOK: [15-30 saniye]\nBÖLÜM1: [başlık] - [içerik]\nBÖLÜM2: [başlık] - [içerik]\nBÖLÜM3: [başlık] - [içerik]\nOUTRO: [call-to-action ile]"}
    ]
    
    try:
        response = await query_openrouter(request.model, messages, temperature=0.7, max_tokens=3000)
        
        # Parse response
        lines = response.split('\n')
        hook = ""
        sections = []
        outro = ""
        
        current_section = None
        for line in lines:
            line = line.strip()
            if line.startswith('HOOK:'):
                hook = line.split(':', 1)[1].strip()
            elif line.startswith('BÖLÜM') or line.startswith('SECTION'):
                if current_section:
                    sections.append(current_section)
                parts = line.split(' - ', 1)
                current_section = {
                    "title": parts[0].split(':', 1)[-1].strip(),
                    "content": parts[1] if len(parts) > 1 else ""
                }
            elif line.startswith('OUTRO:'):
                outro = line.split(':', 1)[1].strip()
            elif current_section and line:
                current_section["content"] += " " + line
        
        if current_section:
            sections.append(current_section)
        
        # Store in database
        await db.generations.insert_one({
            "id": str(uuid.uuid4()),
            "type": "script",
            "title": request.title,
            "language": request.language,
            "model": request.model,
            "video_length_minutes": request.video_length_minutes,
            "hook": hook,
            "sections": sections,
            "outro": outro,
            "timestamp": datetime.utcnow()
        })
        
        return ScriptResponse(
            hook=hook,
            sections=sections,
            outro=outro,
            language=request.language,
            model_used=SUPPORTED_MODELS[request.model]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/generate-thumbnail", response_model=ThumbnailResponse)
async def generate_thumbnail(request: ThumbnailRequest):
    """Generate thumbnail text suggestions"""
    prompts = get_language_prompts(request.language)
    
    messages = [
        {"role": "system", "content": prompts["system"]},
        {"role": "user", "content": f"{prompts['thumbnail_prompt']}\n\nBaşlık: {request.title}\n\nSadece 3 kısa metin önerisi ver, her satırda bir öneri (2-5 kelime)."}
    ]
    
    try:
        response = await query_openrouter(request.model, messages, temperature=0.9)
        thumbnail_texts = [line.strip().lstrip('1234567890.-) ') for line in response.split('\n') if line.strip()][:3]
        
        # Store in database
        await db.generations.insert_one({
            "id": str(uuid.uuid4()),
            "type": "thumbnail",
            "title": request.title,
            "language": request.language,
            "model": request.model,
            "thumbnail_texts": thumbnail_texts,
            "timestamp": datetime.utcnow()
        })
        
        return ThumbnailResponse(
            thumbnail_texts=thumbnail_texts,
            language=request.language,
            model_used=SUPPORTED_MODELS[request.model]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/analyze-seo", response_model=SEOResponse)
async def analyze_seo(request: SEORequest):
    """Analyze SEO scores for content"""
    try:
        scores = calculate_seo_scores(request.title, request.description, request.hashtags, request.language)
        
        # Generate recommendations
        recommendations = []
        if scores.clickbait_score < 60:
            rec = "Başlığınızı daha dikkat çekici hale getirin" if request.language == "tr" else "Make your title more attention-grabbing"
            recommendations.append(rec)
        if scores.length_score < 80:
            rec = "Başlık uzunluğunu 50-70 karakter arasında tutun" if request.language == "tr" else "Keep title length between 50-70 characters"
            recommendations.append(rec)
        if scores.keyword_relevance_score < 70:
            rec = "Hashtag'lerinizin başlıkla daha uyumlu olmasını sağlayın" if request.language == "tr" else "Make hashtags more relevant to your title"
            recommendations.append(rec)
        
        # Store in database
        await db.seo_analyses.insert_one({
            "id": str(uuid.uuid4()),
            "title": request.title,
            "description": request.description,
            "hashtags": request.hashtags,
            "language": request.language,
            "scores": scores.dict(),
            "recommendations": recommendations,
            "timestamp": datetime.utcnow()
        })
        
        return SEOResponse(scores=scores, recommendations=recommendations)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()