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
import hmac
import hashlib
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from pyppeteer import launch

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

# 네이버 쇼핑 API 설정 추가
NAVER_CLIENT_ID = "네이버_클라이언트_ID"
NAVER_CLIENT_SECRET = "네이버_클라이언트_시크릿"

class NaverSearchRequest(BaseModel):
    keyword: str

class CoupangSearchRequest(BaseModel):
    keyword: str

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
                            
                        # Content-Type 정
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

@app.post("/api/search/shopping")
async def search_shopping(request: NaverSearchRequest):
    try:
        headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
        }
        
        encoded_keyword = urllib.parse.quote(request.keyword)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encoded_keyword}&display=10"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return JSONResponse({
                        "status": "success",
                        "data": data
                    })
                else:
                    error_msg = await response.text()
                    logger.error(f"네이버 쇼핑 API 오류: {error_msg}")
                    raise HTTPException(
                        status_code=response.status,
                        detail=f"네이버 쇼핑 API 요청 실패: {error_msg}"
                    )
                    
    except Exception as e:
        logger.error(f"쿠핑 검색 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"쿠핑 검색 처리 중 오류 발생: {str(e)}"
        )

@app.post("/api/search/coupang")
async def search_coupang(request: CoupangSearchRequest):
    try:
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 백그라운드 실행
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-gpu')
        
        # User-Agent 설정
        ua = UserAgent()
        chrome_options.add_argument(f'user-agent={ua.random}')
        
        # 프록시 설정 (선택사항)
        # chrome_options.add_argument('--proxy-server=프록시주소:포트')
        
        # WebDriver 초기화
        service = Service()
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
            # 검색 URL 생성
            encoded_keyword = urllib.parse.quote(request.keyword)
            base_url = "https://www.coupang.com/np/search"
            params = {
                'component': '',
                'q': request.keyword,
                'channel': 'user'
            }
            
            # URL 파라미터 인코딩
            query_string = urllib.parse.urlencode(params)
            search_url = f"{base_url}?{query_string}"
            
            # 페이지 로드
            driver.get(search_url)
            
            # 명시적 대기 설정
            wait = WebDriverWait(driver, 10)
            
            # 상품 목록이 로드될 때까지 대기
            products_selector = "li.search-product"
            products = wait.until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, products_selector))
            )
            
            # 결과 저장
            results = []
            
            # 상위 10개 상품만 처리
            for product in products[:10]:
                try:
                    # 상품 정보 추출
                    title_element = product.find_element(By.CSS_SELECTOR, "div.name")
                    price_element = product.find_element(By.CSS_SELECTOR, "strong.price-value")
                    
                    # 링크 추출 수정
                    link_element = product.find_element(By.CSS_SELECTOR, "a.search-product-link")
                    product_link = link_element.get_attribute("href")
                    
                    # 상품 링크가 상대 경로인 경우 절대 경로로 변환
                    if product_link.startswith("/"):
                        product_link = f"https://www.coupang.com{product_link}"
                    
                    # 이미지 URL 추출
                    try:
                        img_element = product.find_element(By.CSS_SELECTOR, "img.search-product-wrap-img")
                        image_url = img_element.get_attribute("src")
                    except:
                        image_url = ""
                    
                    results.append({
                        "title": title_element.text,
                        "price": price_element.text,
                        "link": product_link,
                        "image": image_url
                    })
                    
                except Exception as e:
                    logger.warning(f"상품 정보 추출 중 오류: {str(e)}")
                    continue
            
            return JSONResponse({
                "status": "success",
                "data": {
                    "products": results
                }
            })
            
        finally:
            driver.quit()
            
    except Exception as e:
        logger.error(f"쿠팡 검색 처리 중 오류 발생: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"쿠팡 검색 처리 중 오류 발생: {str(e)}"
        )
