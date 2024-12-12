# 도매꾹 웹 스크래퍼

도매꾹 상품 정보를 스크래핑하고 이미지를 다운로드할 수 있는 웹 애플리케이션입니다.

## 시작하기 전에

### 필수 요구사항

- Python 3.8 이상
- Node.js 16.0 이상
- npm 또는 yarn
- 도매꾹 API 키

## 백엔드 설정

1. 가상환경 생성 및 활성화
   cd backend
   python -m venv venv

# Windows

venv\Scripts\activate

# macOS/Linux

source venv/bin/activate

2. 의존성 설치
   pip install -r requirements.txt

3. 환경변수 설정

- backend 디렉토리에 `.env` 파일 생성

HOST=localhost
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
DATA_DIR=scraped_data
API_KEY=your_domeggook_api_key_here

4. 백엔드 서버 실행
   uvicorn app.main:app --reload

## 프론트엔드 설정

1. 의존성 설치
   cd frontend
   npm install

2. 개발 서버 실행
   npm start

## 애플리케이션 접속

- 백엔드 API: http://localhost:8000
- 프론트엔드: http://localhost:3000

## 디렉토리 구조

project-root/
├── backend/
│ ├── app/
│ │ ├── **init**.py
│ │ ├── main.py
│ �� └── scraper.py
│ ├── scraped_data/
│ ├── requirements.txt
│ └── .env
│
├── frontend/
│ ├── public/
│ ├── src/
│ │ ├── components/
│ │ │ ├── ProductInfo.js
│ │ │ ├── ResultView.js
│ │ │ └── ScrapingForm.js
│ │ ├── App.js
│ │ └── index.js
│ ├── package.json
│ └── .gitignore
│
└── README.md

## API 엔드포인트

### 백엔드 API

1. 상품 정보 조회

- URL: POST /api/scrape/ggook
- Request Body:
  {
  "productNo": "상품번호"
  }

- Response:
  {
  "status": "success",
  "data": {
  // 도매꾹 API 응답 데이터
  },
  "message": "도매꾹 상품 정보 조회 성공"
  }

2. 스크래핑 히스토리 조회

- URL: GET /api/history
- Response: 스크래핑된 데이터 목록

## 개발 환경 설정

### VSCode 추천 확장 프로그램

- Python
- Pylance
- ESLint
- Prettier
- React Developer Tools

### 디버깅 설정

1. 백엔드 디버깅 (VSCode launch.json)
   {
   "version": "0.2.0",
   "configurations": [
   {
   "name": "Python: FastAPI",
   "type": "python",
   "request": "launch",
   "module": "uvicorn",
   "args": [
   "app.main:app",
   "--reload"
   ],
   "jinja": true,
   "justMyCode": true
   }
   ]
   }

2. 프론트엔드 디버깅

- Chrome DevTools 사용
- React Developer Tools 브라우저 확장 프로그램 설치

## 배포 준비

1. 백엔드 배포 준비

# 프로덕션 의존성만 설치

pip install -r requirements.txt --no-dev

# 프로덕션 서버 실행

uvicorn app.main:app --host 0.0.0.0 --port 8000

2. 프론트엔드 배포 준비

# 프로덕션 빌드

npm run build

# 정적 파일 서빙 (예: nginx 설정)

server {
listen 80;
server_name your-domain.com;
root /path/to/frontend/build;
index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

}

## 환경별 설정

### 개발 환경

- 백엔드: localhost:8000
- 프론트엔드: localhost:3000
- 디버그 모드 활성화
- CORS 허용

### 프로덕션 환경

- 환경변수 설정 필요
- CORS 설정 업데이트
- 에러 로깅 강화
- 보안 설정 적용

## 유지보수

1. 로그 관리

- 백엔드 로그는 scraped_data 디렉토리에 저장
- 주기적인 로그 정리 필요

2. 데이터 백업

- scraped_data 디렉토리 주기적 백업
- 데이터베이스 도입 고려

## ��제해결

### 일반적인 문제

1. CORS 오류 발생 시

- .env 파일의 ALLOWED_ORIGINS에 프론트엔드 주소가 정확히 설정되어 있는지 확인

2. 모듈을 찾을 수 없는 경우

- 가상환경이 활성화되어 있는지 확인
- requirements.txt 설치가 정상적으로 완료되었는지 확인

3. API 키 관련 오류

- .env 파일에 유효한 도매꾹 API 키가 설정되어 있는지 확인

### 권한 관련 문제

Windows에서 실행 권한 오류 발생 시:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

Linux/macOS에서 실행 권한 오류 발생 시:
chmod +x venv/bin/activate

## 라이선스

- MIT License

## 기여하기

1. Fork the Project
2. Create your Feature Branch
3. Commit your Changes
4. Push to the Branch
5. Open a Pull Request

## 문의사항

- Issue 등록하기
- Pull Request 제출하기

이 프로젝트는 지속적으로 업데이트되며, 새로운 기능과 개선사항이 추가될 예정입니다.
