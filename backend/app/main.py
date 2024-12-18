from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl
from app.scraper import WebScraper
import os
import json
import requests
from datetime import datetime
from urllib.parse import urlparse
import logging
from dotenv import load_dotenv
import aiohttp
import io
from typing import Optional
import asyncio
import ssl

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

@app.get("/api/proxy-image")
async def proxy_image(url: str, timeout: Optional[int] = 60):
    try:
        # URL 디코딩 및 정리
        decoded_url = url.split('?hash=')[0]  # 해시 파라미터 제거
        
        # 타임아웃 설정을 포함한 클라이언트 세션 설정
        timeout_config = aiohttp.ClientTimeout(total=timeout)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://domeggook.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache'
        }
        
        # SSL 검증 비활성화를 위한 커스텀 커넥터 설정
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout_config) as session:
            try:
                async with session.get(decoded_url, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        content = await response.read()
                        
                        # 파일 확장자 추출
                        ext = os.path.splitext(decoded_url)[1]
                        if not ext:
                            ext = '.jpg'  # 기본 확장자
                            
                        # Content-Type 결정
                        content_type = response.headers.get('content-type', '')
                        if not content_type or 'image' not in content_type.lower():
                            content_type = f'image/{ext[1:]}' if ext != '.jpg' else 'image/jpeg'
                        
                        # 파일명 생성
                        filename = os.path.basename(decoded_url).split('?')[0]
                        if not os.path.splitext(filename)[1]:
                            filename += ext
                            
                        return StreamingResponse(
                            io.BytesIO(content), 
                            media_type=content_type,
                            headers={
                                'Cache-Control': 'public, max-age=31536000',
                                'Access-Control-Allow-Origin': '*',
                                'Content-Disposition': f'attachment; filename="{filename}"'
                            }
                        )
                    else:
                        logger.error(f"이미지 다운로드 실패: HTTP {response.status} - URL: {decoded_url}")
                        raise HTTPException(
                            status_code=response.status,
                            detail=f"이미지 다운로드 실패: HTTP {response.status}"
                        )
            except asyncio.TimeoutError:
                logger.error(f"타임아웃 발생: URL: {decoded_url}")
                raise HTTPException(
                    status_code=504,
                    detail="이미지 다운로드 시간이 초과되었습니다"
                )
            except aiohttp.ClientError as e:
                logger.error(f"클라이언트 오류: {str(e)} - URL: {decoded_url}")
                raise HTTPException(
                    status_code=502,
                    detail=f"이미지 서버 연결 오류: {str(e)}"
                )
    except Exception as e:
        logger.error(f"이미지 프록시 오류: {str(e)} - URL: {url}")
        raise HTTPException(
            status_code=500,
            detail=f"이미지 프록시 처리 중 오류 발생: {str(e)}"
        )
