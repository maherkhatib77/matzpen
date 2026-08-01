# -*- coding: utf-8 -*-
"""
מצפן נט - שרת פיתוח מקומי (Python)
מגיש קבצים סטטיים + מטפל ב-POST /api/data-save לכתיבת קבצי JSON.
+ מטפל ב-POST /api/create-page-file ליצירת קבצי HTML בתיקיית pages/
+ מטפל ב-POST /api/save-page ליצירת קבצי HTML (גרסה נוספת)

הפעלה:  python server.py
כתובת:  http://localhost:8000
עצירה:  Ctrl+C
"""

import http.server
import json
import os
import sys
import re
import urllib.parse

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PAGES_DIR = os.path.join(BASE_DIR, 'pages')


class MatspanetHandler(http.server.SimpleHTTPRequestHandler):
    """מטפל גם בקבצים סטטיים וגם ב-API לשמירת JSON ויצירת דפי HTML."""

    def do_OPTIONS(self):
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        if self.path.startswith('/api/'):
            self._handle_api_get()
        else:
            super().do_GET()

    def do_POST(self):
        # הסרת פרמטרים מה-URL (כמו ?XTransformPort=3001)
        path = self.path.split('?')[0]
        
        if path == '/api/data-save':
            self._handle_data_save()
        elif path == '/api/create-page-file' or path == '/api/create-page-file.php':
            self._handle_create_page_file()
        elif path == '/api/save-page':
            self._handle_save_page()
        elif path == '/api/health-check':
            self._handle_health_check()
        else:
            self.send_error(404, 'Not Found - ' + path)

    def _send_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')

    def _handle_api_get(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._send_cors_headers()
        self.end_headers()
        response = {'status': 'ok', 'message': 'Matspanet local server running'}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _handle_data_save(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            if 'filename' not in data or 'data' not in data:
                self._send_error(400, '⚠️ נתונים לא תקינים - חסר filename או data')
                return

            filename = os.path.basename(data['filename'])
            file_data = data['data']

            if not filename.lower().endswith('.json'):
                self._send_error(400, '⚠️ סוג קובץ לא מורשה - חייב להסתיים ב-.json: ' + filename)
                return

            if not isinstance(file_data, (list, dict)):
                self._send_error(400, '⚠️ נתונים לא תקינים - חייב להיות מערך או אובייקט')
                return

            if not os.path.isdir(DATA_DIR):
                os.makedirs(DATA_DIR, exist_ok=True)

            target_path = os.path.join(DATA_DIR, filename)
            with open(target_path, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, ensure_ascii=False, indent=2)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            response = {'success': True, 'filename': filename}
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

            print('✅ OK  Saved ' + filename + ' (' + str(len(json.dumps(file_data))) + ' bytes)')

        except json.JSONDecodeError as e:
            self._send_error(400, '⚠️ JSON לא תקין: ' + str(e))
        except Exception as e:
            self._send_error(500, '❌ שגיאה בשמירה: ' + str(e))

    def _handle_create_page_file(self):
        """טיפול ביצירת קובץ HTML חדש בתיקיית pages/"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            # בדיקה: מה הגיע?
            print('📥 Received data keys:', list(data.keys()))

            # תמיכה בשני הפורמטים האפשריים
            if 'filename' not in data:
                self._send_error(400, '⚠️ חסר filename - הנתונים שהתקבלו: ' + str(list(data.keys())))
                return

            filename = data.get('filename', '')
            title = data.get('title', data.get('titleHe', ''))
            content = data.get('content', '')

            # אם אין תוכן, ננסה לשלוף משדה אחר
            if not content and 'content' in data:
                content = data['content']
            if not content and 'htmlContent' in data:
                content = data['htmlContent']

            if not filename:
                self._send_error(400, '⚠️ שם קובץ ריק')
                return

            if not content or content.strip() == '':
                self._send_error(400, '⚠️ תוכן הדף ריק - אנא הזן תוכן לפני שמירה')
                return

            # הוספת .html אם חסר
            if not filename.lower().endswith('.html'):
                filename = filename + '.html'

            # בדיקת שם קובץ תקין
            if not re.match(r'^[a-zA-Z0-9\-_]+\.html$', filename):
                self._send_error(400, '⚠️ שם קובץ לא תקין - יש להשתמש באותיות באנגלית, מספרים, מקף וקו תחתון בלבד')
                return

            # יצירת תיקיית pages אם אינה קיימת
            if not os.path.isdir(PAGES_DIR):
                os.makedirs(PAGES_DIR, exist_ok=True)
                print('📁 Created pages directory: ' + PAGES_DIR)

            # קריאת הגדרות אתר
            site_name_ar, site_name_he, site_logo, footer_text_ar = self._get_site_settings()
            html_content = self._build_html_page(filename, title, content, site_name_ar, site_name_he, site_logo, footer_text_ar)

            # שמירת הקובץ
            target_path = os.path.join(PAGES_DIR, filename)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            response = {
                'success': True,
                'message': 'הדף נוצר בהצלחה!',
                'filename': filename,
                'path': '/pages/' + filename
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

            print('📄 ✅ Created page: ' + filename + ' (' + str(len(html_content)) + ' bytes)')

        except json.JSONDecodeError as e:
            self._send_error(400, '⚠️ JSON לא תקין: ' + str(e))
        except Exception as e:
            self._send_error(500, '❌ שגיאה ביצירת דף: ' + str(e))

    def _handle_save_page(self):
        """טיפול ביצירת קובץ HTML דרך save-page.php (פורמט שונה)"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length).decode('utf-8')
            data = json.loads(body)

            print('📥 Received data keys (save-page):', list(data.keys()))

            filename = data.get('filename', '')
            title_he = data.get('titleHe', '')
            title_ar = data.get('titleAr', '')
            content = data.get('content', '')

            if not filename:
                self._send_error(400, '⚠️ חסר filename')
                return

            if not content or content.strip() == '':
                self._send_error(400, '⚠️ תוכן הדף ריק - אנא הזן תוכן לפני שמירה')
                return

            # ניקוי שם קובץ
            filename = re.sub(r'[^a-zA-Z0-9\-_]', '', filename)
            if not filename:
                self._send_error(400, '⚠️ שם קובץ לא תקין')
                return

            if not filename.lower().endswith('.html'):
                filename = filename + '.html'

            # יצירת תיקיית pages אם אינה קיימת
            if not os.path.isdir(PAGES_DIR):
                os.makedirs(PAGES_DIR, exist_ok=True)
                print('📁 Created pages directory: ' + PAGES_DIR)

            # קריאת הגדרות אתר
            site_name_ar, site_name_he, site_logo, footer_text_ar = self._get_site_settings()
            title = title_he or title_ar or filename.replace('.html', '')
            html_content = self._build_html_page(filename, title, content, site_name_ar, site_name_he, site_logo, footer_text_ar)

            target_path = os.path.join(PAGES_DIR, filename)
            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._send_cors_headers()
            self.end_headers()
            response = {
                'success': True,
                'message': 'הדף נוצר בהצלחה!',
                'file': filename
            }
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

            print('📄 ✅ Created page (save-page): ' + filename)

        except json.JSONDecodeError as e:
            self._send_error(400, '⚠️ JSON לא תקין: ' + str(e))
        except Exception as e:
            self._send_error(500, '❌ שגיאה: ' + str(e))

    def _handle_health_check(self):
        """בדיקת תקינות השרת"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._send_cors_headers()
        self.end_headers()
        
        response = {
            'allPassed': True,
            'results': [
                {'status': 'ok', 'label': 'שרת Python פועל', 'detail': 'הכל תקין'},
                {'status': 'ok', 'label': 'תיקיית data', 'detail': DATA_DIR},
                {'status': 'ok', 'label': 'תיקיית pages', 'detail': PAGES_DIR}
            ]
        }
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))

    def _get_site_settings(self):
        """קריאת הגדרות אתר מקובץ settings.json ו-homepage.json"""
        site_name_ar = 'بوصلة نت'
        site_name_he = 'מצפן נט'
        site_logo = ''
        footer_text_ar = ''
        try:
            settings_path = os.path.join(DATA_DIR, 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    if 'siteNameAr' in settings: site_name_ar = settings['siteNameAr']
                    if 'siteNameHe' in settings: site_name_he = settings['siteNameHe']
                    if 'logoUrl' in settings: site_logo = settings['logoUrl']
                    if 'copyrightAr' in settings: footer_text_ar = settings['copyrightAr']
        except:
            pass
        try:
            homepage_path = os.path.join(DATA_DIR, 'homepage.json')
            if os.path.exists(homepage_path):
                with open(homepage_path, 'r', encoding='utf-8') as f:
                    hp = json.load(f)
                    if hp.get('logo'): site_logo = hp['logo']
                    if hp.get('siteName', {}).get('ar'): site_name_ar = hp['siteName']['ar']
                    if hp.get('siteName', {}).get('he'): site_name_he = hp['siteName']['he']
                    if hp.get('footerText', {}).get('ar'): footer_text_ar = hp['footerText']['ar']
        except:
            pass
        if not footer_text_ar:
            footer_text_ar = site_name_ar + ' © ' + str(__import__('datetime').datetime.now().year) + ' | وزارة التربية والتعليم'
        return site_name_ar, site_name_he, site_logo, footer_text_ar

    def _build_html_page(self, filename, title, content, site_name_ar, site_name_he, site_logo, footer_text_ar):
        """בניית דף HTML מלא – תואם לעיצוב האתר (page.html, faq.html, team.html)"""
        import html as html_mod
        from html import escape as esc
        year = __import__('datetime').datetime.now().year
        logo_html = esc(site_logo) if site_logo else ''
        logo_tag = f'<img src="{logo_html}" alt="logo">' if site_logo else '🧭'

        return f'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{esc(title)} — {esc(site_name_ar)}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;500;600;700;800;900&family=Tajawal:wght@200;300;400;500;700;800;900&display=swap" rel="stylesheet">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧭</text></svg>">
    <link rel="stylesheet" href="../css/style.css">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
            min-height: 100vh;
            background: var(--gray-50, #f3f3f3);
            display: flex;
            flex-direction: column;
        }}
        .cp-header {{
            background: linear-gradient(135deg, var(--primary, #0ca7aa) 0%, var(--primary-dark, #09787a) 100%);
            padding: 0; position: sticky; top: 0; z-index: 100;
            box-shadow: 0 4px 16px rgba(0,0,0,.06);
        }}
        .cp-header-inner {{
            max-width: 1200px; margin: 0 auto; padding: 16px 24px;
            display: flex; align-items: center; justify-content: space-between; gap: 16px;
        }}
        .cp-logo {{ display: flex; align-items: center; gap: 12px; color: #fff; text-decoration: none; }}
        .cp-logo-icon {{ font-size: 32px; line-height: 1; overflow: hidden; width: 52px; height: 52px; border-radius: 8px; border: 3px solid rgba(255,255,255,.4); background: rgba(255,255,255,.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }}
        .cp-logo-icon img {{ width: 100%; height: 100%; object-fit: cover; }}
        .cp-logo-text {{ font-size: 20px; font-weight: 800; color: #fff; }}
        .cp-btn-back {{
            background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.3);
            color: #fff; padding: 8px 18px; border-radius: 20px; font-size: 14px;
            font-weight: 600; cursor: pointer; transition: all .2s;
            font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
            text-decoration: none; display: inline-flex; align-items: center; gap: 6px;
        }}
        .cp-btn-back:hover {{ background: rgba(255,255,255,.3); }}
        .cp-hero {{ max-width: 1200px; width: 100%; margin: 0 auto; padding: 32px 24px 8px; text-align: center; }}
        .cp-hero-title {{ font-size: 28px; font-weight: 800; color: var(--gray-700, #24343f); margin-bottom: 6px; }}
        .cp-content {{
            flex: 1; max-width: 900px; width: 100%; margin: 0 auto; padding: 28px 24px 40px;
        }}
        .cp-content img {{ max-width: 100%; height: auto; border-radius: 8px; margin: 12px 0; }}
        .cp-content table {{ border-collapse: collapse; width: 100%; margin: 16px 0; }}
        .cp-content td, .cp-content th {{ border: 1px solid var(--gray-200, #e5e5e5); padding: 10px 14px; text-align: right; }}
        .cp-content th {{ background: var(--gray-50, #f7f7f7); font-weight: 700; }}
        .cp-content a {{ color: var(--primary, #0ca7aa); text-decoration: underline; }}
        .cp-content h1, .cp-content h2, .cp-content h3 {{ margin: 24px 0 12px; color: var(--gray-700, #24343f); line-height: 1.4; }}
        .cp-content h1 {{ font-size: 26px; }}
        .cp-content h2 {{ font-size: 22px; }}
        .cp-content h3 {{ font-size: 18px; }}
        .cp-content p {{ margin-bottom: 12px; line-height: 1.9; }}
        .cp-content ul, .cp-content ol {{ margin: 12px 0; padding-right: 24px; }}
        .cp-content li {{ margin-bottom: 6px; line-height: 1.8; }}
        .cp-content blockquote {{ border-right: 4px solid var(--primary, #0ca7aa); padding: 12px 20px; margin: 16px 0; background: #e9f6fb; border-radius: 0 8px 8px 0; color: var(--gray-600, #4c6373); }}
        .cp-content strong {{ font-weight: 700; }}
        .cp-content em {{ font-style: italic; }}
        .cp-footer {{
            text-align: center; padding: 18px; color: var(--gray-300, #999999); font-size: 12px;
            border-top: 1px solid var(--gray-100, #f2f2f2); background: rgba(255,255,255,.7); flex-shrink: 0;
        }}
        @media (max-width: 768px) {{
            .cp-header-inner {{ flex-wrap: wrap; }}
            .cp-hero {{ padding: 24px 16px 4px; }}
            .cp-hero-title {{ font-size: 24px; }}
            .cp-content {{ padding: 22px 16px 32px; }}
            .cp-logo-icon {{ width: 44px; height: 44px; font-size: 24px; }}
        }}
    </style>
</head>
<body>
    <header class="cp-header">
        <div class="cp-header-inner">
            <a class="cp-logo" href="../index.html">
                <span class="cp-logo-icon" id="globalHeaderLogo">{logo_tag}</span>
                <div class="cp-logo-text" id="globalHeaderName">{esc(site_name_ar)}</div>
            </a>
            <a href="../index.html" class="cp-btn-back">→ الرئيسية</a>
        </div>
    </header>
    <section class="cp-hero">
        <h1 class="cp-hero-title" id="pageTitle">{esc(title)}</h1>
    </section>
    <main class="cp-content" id="pageContent">
        {content}
    </main>
    <footer class="cp-footer" id="globalFooterText">
        {esc(footer_text_ar)}
    </footer>
    <script src="../js/data.js?v=4.10.0"></script>
    <script src="../js/global-ui.js?v=1.0.0"></script>
    <script>
        function initPage() {{
            var hp = DataStore.getHomepage();
            if (hp && hp.logo) {{
                var logoEl = document.getElementById('globalHeaderLogo');
                if (logoEl) logoEl.innerHTML = '<img src="' + hp.logo + '" alt="logo">';
            }}
            if (hp && hp.siteName) {{
                var nameEl = document.getElementById('globalHeaderName');
                if (nameEl) nameEl.textContent = hp.siteName.ar || hp.siteName.he || '';
            }}
            if (hp && hp.footerText) {{
                var footerEl = document.getElementById('globalFooterText');
                if (footerEl) footerEl.innerHTML = hp.footerText.ar || hp.footerText.he || footerEl.innerHTML;
            }}
            if (typeof GlobalUI !== 'undefined') GlobalUI.apply('ar');
        }}
        if (DataStore.init && typeof DataStore.init === 'function') {{
            var _t = setTimeout(initPage, 5000);
            DataStore.init().then(function() {{ clearTimeout(_t); initPage(); }}).catch(function() {{ clearTimeout(_t); initPage(); }});
        }} else {{
            initPage();
        }}
    </script>
</body>
</html>'''

    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self._send_cors_headers()
        self.end_headers()
        response = {'error': message}
        self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
        print('❌ ERR ' + str(code) + ': ' + message)

    def log_message(self, format, *args):
        if '/api/' in str(args[0]):
            print('🔄 API ' + self.address_string() + ' - ' + (format % args))


def main():
    print('=' * 60)
    print(' 🧭 Matspanet - local dev server')
    print('=' * 60)
    print(' 📂 Data folder  : ' + DATA_DIR)
    print(' 📂 Pages folder : ' + PAGES_DIR)
    print(' 🌐 Address      : http://localhost:' + str(PORT))
    print(' 🔐 Login page   : http://localhost:' + str(PORT) + '/login.html')
    print('=' * 60)
    print(' 🟢 Press Ctrl+C to stop')
    print('=' * 60)
    print()

    try:
        with http.server.HTTPServer(('', PORT), MatspanetHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n\n🛑 Server stopped.')
        sys.exit(0)
    except OSError as e:
        if e.errno == 98 or e.errno == 10048:
            print('\n⚠️ Port ' + str(PORT) + ' is already in use!')
            print('💡 Try another port:  python server.py')
        else:
            print('\n❌ Error: ' + str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()