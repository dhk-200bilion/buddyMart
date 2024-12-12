import aiohttp
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
import csv

class WebScraper:
    def __init__(self):
        self.data_dir = "scraped_data"
        self.login_url = "https://domeggook.com/main/member/login.php"
        self.session_cookies = None
        os.makedirs(self.data_dir, exist_ok=True)

    async def login(self, username: str, password: str):
        """도매꾹 로그인 수행"""
        login_data = {
            'mode': 'login',
            'id': username,
            'pw': password,
            'save_id': 'Y'
        }
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://domeggook.com/'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(self.login_url, data=login_data, headers=headers) as response:
                if response.status == 200:
                    self.session_cookies = response.cookies
                    return True
                return False

    async def scrape_website(self, url: str) -> dict:
        if not self.session_cookies:
            raise Exception("로그인이 필요합니다. login() 메소드를 먼저 호출해주세요.")

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://domeggook.com/'
        }

        async with aiohttp.ClientSession(cookies=self.session_cookies) as session:
            async with session.get(url, headers=headers) as response:
                if response.status != 200:
                    raise Exception("웹사이트에 접근할 수 없습니다")
                
                try:
                    html = await response.text('utf-8')
                except UnicodeDecodeError:
                    try:
                        html = await response.text('cp949')
                    except UnicodeDecodeError:
                        html = await response.text(errors='ignore')

        soup = BeautifulSoup(html, 'html.parser')
        
        return {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'html': str(soup),
            'title': soup.title.string if soup.title else '',
            'forms': self._extract_forms(soup)
        }
    
    def _extract_forms(self, soup):
        forms = soup.find_all('form')
        form_data = []
        for form in forms:
            form_info = {
                'action': form.get('action', ''),
                'method': form.get('method', 'get'),
                'fields': self._extract_form_fields(form)
            }
            form_data.append(form_info)
        return form_data

    def _extract_form_fields(self, form):
        fields = []
        for element in form.find_all(['input', 'select', 'textarea']):
            field_info = {
                'type': element.get('type', 'text'),
                'name': element.get('name', ''),
                'id': element.get('id', ''),
                'value': element.get('value', ''),
                'required': element.get('required') is not None
            }
            fields.append(field_info)
        return fields

    def save_to_file(self, data: dict) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.data_dir}/scraped_{timestamp}.json"
        
        # HTML 내용을 저장하기 전에 복사본 생성
        data_to_save = data.copy()
        data_to_save['html'] = data['html'][:1000] + '...' if len(data['html']) > 1000 else data['html']
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data_to_save, f, ensure_ascii=False, indent=2)
        
        return filename

    def export_to_csv(self, data: dict) -> str:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{self.data_dir}/scraped_{timestamp}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Form', 'Action', 'Method', 'Field Name', 'Field Type', 'Required'])
            
            for i, form in enumerate(data['forms']):
                for field in form['fields']:
                    writer.writerow([
                        f'Form {i+1}',
                        form['action'],
                        form['method'],
                        field['name'] or field['id'],
                        field['type'],
                        'Yes' if field['required'] else 'No'
                    ])
        
        return filename