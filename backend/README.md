## 백엔드 설정 및 실행

### 필수 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)

### 설치 방법

1. 가상환경 생성 및 활성화

```bash
python -m venv venv
source venv/bin/activate
```

2. 패키지 설치

```bash
pip install -r requirements.txt
```

3. 환경변수 설정

- `.env` 파일을 backend 디렉토리에 생성하고 다음 내용을 추가:

```bash
HOST=localhost
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000
DATA_DIR=scraped_data
API_KEY=your_api_key_here
```

4. 서버 실행

```bash
uvicorn app.main:app --reload
```
