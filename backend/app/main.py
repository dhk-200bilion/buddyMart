from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl
from app.scraper import WebScraper
import os
import json
import requests
from datetime import datetime
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

app = FastAPI()
scraper = WebScraper()
logger = logging.getLogger(__name__)

# 환경 변수 사용
HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", 8000))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
DATA_DIR = os.getenv("DATA_DIR", "scraped_data")
API_KEY = os.getenv("API_KEY")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UrlRequest(BaseModel):
    url: HttpUrl

class LoginRequest(BaseModel):
    username: str
    password: str

# 도매꾹 API 요청을 위한 Pydantic 모델
class GgookRequest(BaseModel):
    productNo: str

def extract_image_urls(html_content):
    """HTML 컨텐츠에서 이미지 URL 추출"""
    import re
    pattern = r'src="(https?://[^"]+)"'
    return re.findall(pattern, html_content)

@app.post("/api/scrape")
async def scrape_url(request: UrlRequest):
    try:
        data = await scraper.scrape_website(str(request.url))
        filename = scraper.save_to_file(data)
        return JSONResponse({
            "status": "success",
            "data": {
                "url": data["url"],
                "title": data["title"],
                "html": data["html"],
                "timestamp": data["timestamp"],
                "forms": data["forms"]
            },
            "filename": os.path.basename(filename)
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/download/{filename}")
async def download_file(filename: str):
    file_path = f"scraped_data/{filename}"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    return FileResponse(file_path, filename=filename)

@app.get("/api/history")
async def get_history():
    files = os.listdir("scraped_data")
    history = []
    for file in files:
        with open(f"scraped_data/{file}", "r") as f:
            data = json.load(f)
            history.append({
                "filename": file,
                "url": data["url"],
                "timestamp": data["timestamp"]
            })
    return sorted(history, key=lambda x: x["timestamp"], reverse=True)

@app.get("/")
async def read_root():
    return {"message": "Welcome to Web Scraping API"}

@app.post("/api/login")
async def login(request: LoginRequest):
    """도매꾹 로그인"""
    success = await scraper.login(request.username, request.password)
    if not success:
        raise HTTPException(status_code=401, detail="로그인 실패")
    return {"message": "로그인 성공"}

@app.post("/api/scrape/ggook")
async def scrape_ggook(request: GgookRequest):
    try:
        # API 요청 파라미터 검증
        if not API_KEY or not request.productNo:
            raise HTTPException(
                status_code=400,
                detail="API Key와 상품번호는 필수 입력값입니다."
            )
            
        # API URL 정의
        url = "https://domeggook.com/ssl/api/"
            
        # API 요청 파라미터
        params = {
            "ver": "4.4",
            "mode": "getItemView",
            "aid": API_KEY,
            "no": request.productNo,
            "om": "json"
        }
        
        # 요청 URL과 파라미터 로깅
        logger.info(f"도매꾹 API 요청: URL={url}, Params={params}")
        
        # API 호출
        try:
            response = requests.get(
                url, 
                params=params, 
                timeout=10,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
            )
            
            # 응답 로깅
            logger.info(f"API 응답 상태 코드: {response.status_code}")
            logger.info(f"API 응답 헤더: {dict(response.headers)}")
            logger.info(f"API 응답 내용: {response.text[:200]}...")
            
            # 응답 상태 코드 확인
            response.raise_for_status()
            
        except requests.RequestException as e:
            logger.error(f"API 요청 실패: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"도매꾹 API 요청 실패: {str(e)}"
            )
        
        # 응답 데이터 파싱
        try:
            if 'xml' in response.headers.get('content-type', '').lower():
                import xmltodict
                data = xmltodict.parse(response.text)
            else:
                data = response.json()
                
        except Exception as e:
            logger.error(f"응답 데이터 파싱 실패: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"응답 데이터 파싱 실패: {str(e)}"
            )
            
        # 상품 상세 이미지 URL 추출
        detail_images = []
        if 'desc' in data['domeggook'] and 'contents' in data['domeggook']['desc']:
            item_content = data['domeggook']['desc']['contents'].get('item', '')
            detail_images = extract_image_urls(item_content)
        
        return {
            "status": "success",
            "data": {
                **data,
                "detail_images": detail_images
            },
            "message": "도매꾹 상품 정보 조회 성공"
        }
        
    except Exception as e:
        logger.error(f"처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"처리 중 오류 발생: {str(e)}"
        )
