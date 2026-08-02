#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import socket
import signal
import datetime
import traceback
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# ============================================================
# הגדרות עם טיימאוטים מורחבים
# ============================================================

PORT = 8000
DATA_FOLDER = "data"
PAGES_FOLDER = "pages"

# הגדרת טיימאוט גבוה יותר - 120 שניות
TIMEOUT = 120  # שונה מ-60 ל-120

# הגדרת טיימאוט גלובלי לחיבורים
socket.setdefaulttimeout(TIMEOUT)

# התעלמות משגיאות BrokenPipe
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except AttributeError:
    pass  # Windows

# ============================================================
# מחלקת Handler עם טיימאוט מורחב
# ============================================================

class CustomHandler(SimpleHTTPRequestHandler):
    """Handler מותאם עם טיימאוט מורחב"""
    
    server_version = "Matspanet/2.0"
    timeout = TIMEOUT  # הוספת timeout בכתובת המחלקה
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # הגדרת טיימאוט לחיבור עצמו
        if hasattr(self, 'connection'):
            try:
                self.connection.settimeout(TIMEOUT)
            except:
                pass
        
        # הגדרת טיימאוט לקריאה ולכתיבה
        if hasattr(self, 'rfile'):
            try:
                self.rfile._sock.settimeout(TIMEOUT)
            except:
                pass
        
        if hasattr(self, 'wfile'):
            try:
                self.wfile._sock.settimeout(TIMEOUT)
            except:
                pass
    
    # ============================================================
    # שיטת handle_one_request עם טיפול בטיימאוט
    # ============================================================
    
    def handle_one_request(self):
        """טיפול בבקשה אחת עם הגנה מפני Timeout"""
        try:
            # הגדרת טיימאוט לפני כל בקשה
            if hasattr(self, 'connection'):
                try:
                    self.connection.settimeout(TIMEOUT)
                except:
                    pass
            
            super().handle_one_request()
            
        except socket.timeout:
            print(f"⏰  Request timed out: {self.client_address[0]}")
            try:
                self.send_error(408, "Request Timeout")
            except:
                pass
        except TimeoutError as e:
            print(f"⏰  Request timed out: {e}")
            try:
                self.send_error(408, "Request Timeout")
            except:
                pass
        except Exception as e:
            print(f"❌  Error handling request: {e}")
            traceback.print_exc()
    
    # ============================================================
    # שיטת do_GET עם טיימאוט מורחב
    # ============================================================
    
    def do_GET(self):
        """טיפול בבקשת GET עם טיימאוט מורחב"""
        try:
            # בדיקה אם זו בקשת API
            if self.path.startswith('/api/'):
                self.handle_api_request()
                return
            
            # טיפול בבקשת קובץ רגילה
            super().do_GET()
            
        except socket.timeout:
            print(f"⏰  GET request timed out: {self.path}")
            try:
                self.send_error(408, "Request Timeout")
            except:
                pass
        except ConnectionAbortedError as e:
            print(f"⚠️  Client disconnected during GET: {e}")
        except BrokenPipeError as e:
            print(f"⚠️  Broken pipe during GET: {e}")
        except TimeoutError as e:
            print(f"⏰  GET request timed out: {e}")
        except Exception as e:
            print(f"❌  Error in GET request: {e}")
            traceback.print_exc()
    
    # ============================================================
    # שיטת do_POST עם טיימאוט מורחב
    # ============================================================
    
    def do_POST(self):
        """טיפול בבקשת POST עם טיימאוט מורחב"""
        try:
            if self.path.startswith('/api/'):
                self.handle_api_request()
            else:
                self.send_error(404, "Not Found")
                
        except socket.timeout:
            print(f"⏰  POST request timed out: {self.path}")
            try:
                self.send_error(408, "Request Timeout")
            except:
                pass
        except ConnectionAbortedError as e:
            print(f"⚠️  Client disconnected during POST: {e}")
        except BrokenPipeError as e:
            print(f"⚠️  Broken pipe during POST: {e}")
        except TimeoutError as e:
            print(f"⏰  POST request timed out: {e}")
        except Exception as e:
            print(f"❌  Error in POST request: {e}")
            traceback.print_exc()
    
    # ============================================================
    # שיטת copyfile עם טיימאוט מורחב
    # ============================================================
    
    def copyfile(self, source, outputfile):
        """העתקת קובץ עם טיימאוט מורחב"""
        try:
            # הגדרת טיימאוט לכתיבה
            if hasattr(outputfile, 'settimeout'):
                try:
                    outputfile.settimeout(TIMEOUT)
                except:
                    pass
            
            chunk_size = 8192
            while True:
                try:
                    buf = source.read(chunk_size)
                    if not buf:
                        break
                    outputfile.write(buf)
                    
                    if hasattr(outputfile, 'flush'):
                        outputfile.flush()
                        
                except socket.timeout:
                    print(f"⏰  Timeout during file copy")
                    return
                except TimeoutError:
                    print(f"⏰  Timeout during file copy")
                    return
                except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
                    print(f"⚠️  Client disconnected during file copy: {e}")
                    return
                    
        except Exception as e:
            print(f"❌  Error copying file: {e}")
            traceback.print_exc()
    
    # ============================================================
    # שיטת handle_api_request עם טיימאוט מורחב
    # ============================================================
    
    def handle_api_request(self):
        """טיפול בבקשות API עם טיימאוט מורחב"""
        try:
            parsed_path = urlparse(self.path)
            endpoint = parsed_path.path
            
            if endpoint == '/api/data-save':
                self.handle_data_save()
            elif endpoint == '/api/data-load':
                self.handle_data_load()
            elif endpoint == '/api/create-page-file':
                self.handle_create_page_file()
            else:
                self.send_error(404, "API endpoint not found")
                
        except socket.timeout:
            print(f"⏰  API request timed out")
            try:
                self.send_error(408, "Request Timeout")
            except:
                pass
        except TimeoutError as e:
            print(f"⏰  API request timed out: {e}")
        except Exception as e:
            print(f"❌  API error: {e}")
            traceback.print_exc()
    
    def handle_data_save(self):
        """שמירת נתונים עם טיימאוט מורחב"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                # קריאת הנתונים עם טיימאוט
                try:
                    post_data = self.rfile.read(content_length)
                except socket.timeout:
                    print(f"⏰  Timeout reading POST data")
                    self.send_error(408, "Request Timeout")
                    return
                except TimeoutError:
                    print(f"⏰  Timeout reading POST data")
                    self.send_error(408, "Request Timeout")
                    return
                
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"❌  JSON decode error: {e}")
                    self.send_error(400, "Invalid JSON data")
                    return
                
                # שמירת הנתונים
                filename = data.get('filename', 'activity_log.json')
                filepath = os.path.join(DATA_FOLDER, filename)
                
                os.makedirs(DATA_FOLDER, exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = json.dumps({'success': True, 'message': 'Data saved successfully'})
                self.wfile.write(response.encode('utf-8'))
                
                print(f"✅  Saved {filename} ({len(post_data)} bytes)")
                
        except Exception as e:
            print(f"❌  Error saving data: {e}")
            traceback.print_exc()
            try:
                self.send_error(500, f"Error saving data: {str(e)}")
            except:
                pass
    
    def handle_data_load(self):
        """טעינת נתונים"""
        try:
            parsed_path = urlparse(self.path)
            params = parse_qs(parsed_path.query)
            filename = params.get('filename', ['activity_log.json'])[0]
            
            filepath = os.path.join(DATA_FOLDER, filename)
            
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = json.dumps(data, ensure_ascii=False)
                self.wfile.write(response.encode('utf-8'))
            else:
                self.send_error(404, f"File {filename} not found")
                
        except Exception as e:
            print(f"❌  Error loading data: {e}")
            traceback.print_exc()
            self.send_error(500, f"Error loading data: {str(e)}")
    
    def handle_create_page_file(self):
        """יצירת קובץ HTML בתיקיית pages/"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                try:
                    post_data = self.rfile.read(content_length)
                except socket.timeout:
                    print(f"⏰  Timeout reading POST data")
                    self.send_error(408, "Request Timeout")
                    return
                except TimeoutError:
                    print(f"⏰  Timeout reading POST data")
                    self.send_error(408, "Request Timeout")
                    return
                
                try:
                    data = json.loads(post_data.decode('utf-8'))
                except json.JSONDecodeError as e:
                    print(f"❌  JSON decode error: {e}")
                    self.send_error(400, "Invalid JSON data")
                    return
                
                action = data.get('action', 'save')
                
                if action == 'delete':
                    filename = data.get('filename', '')
                    if not filename:
                        self.send_error(400, "Filename is required")
                        return
                    
                    if not filename.endswith('.html'):
                        filename += '.html'
                    
                    filepath = os.path.join(PAGES_FOLDER, filename)
                    
                    if os.path.exists(filepath):
                        try:
                            os.remove(filepath)
                            print(f"✅  Deleted page file: {filename}")
                        except Exception as e:
                            print(f"❌  Error deleting file: {e}")
                            self.send_error(500, f"Failed to delete file: {str(e)}")
                            return
                    else:
                        print(f"ℹ️  File did not exist: {filename}")
                    
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    response = json.dumps({'success': True, 'message': 'Page file deleted successfully', 'filename': filename})
                    self.wfile.write(response.encode('utf-8'))
                    return
                
                filename = data.get('filename', '')
                title = data.get('title', '')
                content = data.get('content', '')
                
                if not filename:
                    self.send_error(400, "Filename is required")
                    return
                
                if not title:
                    self.send_error(400, "Title is required")
                    return
                
                filename = os.path.basename(filename)
                
                import re
                if not re.match(r'^[a-zA-Z0-9_-]+\.html$', filename):
                    self.send_error(400, "Invalid filename. Only alphanumeric, hyphens, underscores allowed with .html extension")
                    return
                
                os.makedirs(PAGES_FOLDER, exist_ok=True)
                
                site_name_ar = 'بوصلة نت'
                site_name_he = 'מצפן נט'
                site_logo = ''
                footer_text_ar = ''
                footer_text_he = ''
                
                settings_path = os.path.join(DATA_FOLDER, 'settings.json')
                if os.path.exists(settings_path):
                    try:
                        with open(settings_path, 'r', encoding='utf-8') as f:
                            settings = json.load(f)
                        site_name_ar = settings.get('siteNameAr', site_name_ar)
                        site_name_he = settings.get('siteNameHe', site_name_he)
                        site_logo = settings.get('logoUrl', site_logo)
                        footer_text_ar = settings.get('copyrightAr', footer_text_ar)
                        footer_text_he = settings.get('copyrightHe', footer_text_he)
                    except:
                        pass
                
                homepage_path = os.path.join(DATA_FOLDER, 'homepage.json')
                if os.path.exists(homepage_path):
                    try:
                        with open(homepage_path, 'r', encoding='utf-8') as f:
                            homepage = json.load(f)
                        if homepage.get('logo'):
                            site_logo = homepage['logo']
                        if homepage.get('siteName', {}).get('ar'):
                            site_name_ar = homepage['siteName']['ar']
                        if homepage.get('siteName', {}).get('he'):
                            site_name_he = homepage['siteName']['he']
                        if homepage.get('footerText', {}).get('ar'):
                            footer_text_ar = homepage['footerText']['ar']
                        if homepage.get('footerText', {}).get('he'):
                            footer_text_he = homepage['footerText']['he']
                    except:
                        pass
                
                if not footer_text_ar:
                    footer_text_ar = site_name_ar + ' © ' + datetime.datetime.now().strftime('%Y') + ' | وزارة التربية والتعليم'
                
                logo_html = '🧭'
                if site_logo:
                    logo_html = '<img src="' + self.escape_html(site_logo) + '" alt="logo">'
                
                html_content = self.build_html_page(
                    filename, title, content,
                    site_name_ar, site_name_he, logo_html, footer_text_ar, footer_text_he
                )
                
                filepath = os.path.join(PAGES_FOLDER, filename)
                result = len(html_content.encode('utf-8'))
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                print(f"✅  Created page file: {filename} ({result} bytes)")
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = json.dumps({
                    'success': True,
                    'message': 'Page file created successfully',
                    'filename': filename,
                    'filepath': 'pages/' + filename,
                    'size': result
                })
                self.wfile.write(response.encode('utf-8'))
                
        except Exception as e:
            print(f"❌  Error creating page file: {e}")
            traceback.print_exc()
            try:
                self.send_error(500, f"Error creating page file: {str(e)}")
            except:
                pass
    
    def escape_html(self, text):
        """בריחת תווים מיוחדים ב-HTML"""
        return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    
    def build_html_page(self, filename, title, content, site_name_ar, site_name_he, logo_html, footer_text_ar, footer_text_he):
        """בניית דף HTML עם עיצוב אחיד"""
        from html import escape
        
        html = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>''' + escape(title) + ' — ' + escape(site_name_ar) + '''</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@300;400;500;600;700;800;900&family=Tajawal:wght@200;300;400;500;700;800;900&display=swap" rel="stylesheet">
    <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🧭</text></svg>">
    <link rel="stylesheet" href="../css/style.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
            min-height: 100vh;
            background: var(--gray-50, #f3f3f3);
            display: flex;
            flex-direction: column;
        }
        .cp-header {
            background: linear-gradient(135deg, var(--primary, #0ca7aa) 0%, var(--primary-dark, #09787a) 100%);
            padding: 0; position: sticky; top: 0; z-index: 100;
            box-shadow: 0 4px 16px rgba(0,0,0,.06);
        }
        .cp-header-inner {
            max-width: 1200px; margin: 0 auto; padding: 16px 24px;
            display: flex; align-items: center; justify-content: space-between; gap: 16px;
        }
        .cp-logo { display: flex; align-items: center; gap: 12px; color: #fff; text-decoration: none; }
        .cp-logo-icon { font-size: 32px; line-height: 1; overflow: hidden; width: 52px; height: 52px; border-radius: 8px; border: 3px solid rgba(255,255,255,.4); background: rgba(255,255,255,.15); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
        .cp-logo-icon img { width: 100%; height: 100%; object-fit: cover; }
        .cp-logo-text { font-size: 20px; font-weight: 800; color: #fff; }
        .cp-btn-back {
            background: rgba(255,255,255,.18); border: 1px solid rgba(255,255,255,.3);
            color: #fff; padding: 8px 18px; border-radius: 20px; font-size: 14px;
            font-weight: 600; cursor: pointer; transition: all .2s;
            font-family: 'Noto Sans Arabic', 'Tajawal', sans-serif;
            text-decoration: none; display: inline-flex; align-items: center; gap: 6px;
        }
        .cp-btn-back:hover { background: rgba(255,255,255,.3); }
        .cp-hero { max-width: 1200px; width: 100%; margin: 0 auto; padding: 32px 24px 8px; text-align: center; }
        .cp-hero-title { font-size: 28px; font-weight: 800; color: var(--gray-700, #24343f); margin-bottom: 6px; }
        .cp-content {
            flex: 1; max-width: 900px; width: 100%; margin: 0 auto; padding: 28px 24px 40px;
        }
        .cp-content img { max-width: 100%; height: auto; border-radius: 8px; margin: 12px 0; }
        .cp-content table { border-collapse: collapse; width: 100%; margin: 16px 0; }
        .cp-content td, .cp-content th { border: 1px solid var(--gray-200, #e5e5e5); padding: 10px 14px; text-align: right; }
        .cp-content th { background: var(--gray-50, #f7f7f7); font-weight: 700; }
        .cp-content a { color: var(--primary, #0ca7aa); text-decoration: underline; }
        .cp-content h1, .cp-content h2, .cp-content h3 { margin: 24px 0 12px; color: var(--gray-700, #24343f); line-height: 1.4; }
        .cp-content h1 { font-size: 26px; }
        .cp-content h2 { font-size: 22px; }
        .cp-content h3 { font-size: 18px; }
        .cp-content p { margin-bottom: 12px; line-height: 1.9; }
        .cp-content ul, .cp-content ol { margin: 12px 0; padding-right: 24px; }
        .cp-content li { margin-bottom: 6px; line-height: 1.8; }
        .cp-content blockquote { border-right: 4px solid var(--primary, #0ca7aa); padding: 12px 20px; margin: 16px 0; background: #e9f6fb; border-radius: 0 8px 8px 0; color: var(--gray-600, #4c6373); }
        .cp-content strong { font-weight: 700; }
        .cp-content em { font-style: italic; }
        .cp-footer {
            text-align: center; padding: 18px; color: var(--gray-300, #999999); font-size: 12px;
            border-top: 1px solid var(--gray-100, #f2f2f2); background: rgba(255,255,255,.7); flex-shrink: 0;
        }
        @media (max-width: 768px) {
            .cp-header-inner { flex-wrap: wrap; }
            .cp-hero { padding: 24px 16px 4px; }
            .cp-hero-title { font-size: 24px; }
            .cp-content { padding: 22px 16px 32px; }
            .cp-logo-icon { width: 44px; height: 44px; font-size: 24px; }
        }
    </style>
</head>
<body>
    <header class="cp-header">
        <div class="cp-header-inner">
            <a class="cp-logo" href="../index.html">
                <span class="cp-logo-icon" id="globalHeaderLogo">''' + logo_html + '''</span>
                <div class="cp-logo-text" id="globalHeaderName">''' + escape(site_name_ar) + '''</div>
            </a>
            <a href="../index.html" class="cp-btn-back">→ ''' + 'الرئيسية' + '''</a>
        </div>
    </header>
    <main class="cp-content" id="pageContent">
        <div class="cp-hero"><h1 class="cp-hero-title">''' + escape(title) + '''</h1></div>
        ''' + content + '''
    </main>
    <footer class="cp-footer" id="globalFooterText">
        ''' + escape(footer_text_ar) + '''
    </footer>
    <script src="../js/data.js?v=4.10.0"></script>
    <script src="../js/global-ui.js?v=1.0.0"></script>
    <script>
        function initPage() {
            var hp = DataStore.getHomepage();
            if (hp && hp.logo) {
                var logoEl = document.getElementById('globalHeaderLogo');
                if (logoEl) logoEl.innerHTML = '<img src="' + hp.logo + '" alt="logo">';
            }
            if (hp && hp.siteName) {
                var nameEl = document.getElementById('globalHeaderName');
                if (nameEl) nameEl.textContent = hp.siteName.ar || hp.siteName.he || '';
            }
            if (hp && hp.footerText) {
                var footerEl = document.getElementById('globalFooterText');
                if (footerEl) footerEl.innerHTML = hp.footerText.ar || hp.footerText.he || footerEl.innerHTML;
            }
            if (typeof GlobalUI !== 'undefined') GlobalUI.apply('ar');
        }
        if (DataStore.init && typeof DataStore.init === 'function') {
            var _t = setTimeout(initPage, 5000);
            DataStore.init().then(function() { clearTimeout(_t); initPage(); }).catch(function() { clearTimeout(_t); initPage(); });
        } else {
            initPage();
        }
    </script>
</body>
</html>'''
        
        return html
    
    # ============================================================
    # שיטת log_message מותאמת
    # ============================================================
    
    def log_message(self, format, *args):
        """הדפסת הודעות לוג"""
        try:
            message = format % args
            print(f"🔄  {self.client_address[0]} - {message}")
        except:
            pass

# ============================================================
# הרצת השרת
# ============================================================

def run_server(port=PORT):
    """הרצת השרת עם טיימאוט מורחב"""
    
    for folder in [DATA_FOLDER, PAGES_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁  Created folder: {folder}")
    
    handler = CustomHandler
    
    try:
        with HTTPServer(("", port), handler) as httpd:
            # הגדרת טיימאוט לסוקט הראשי
            httpd.socket.settimeout(TIMEOUT)
            httpd.timeout = TIMEOUT
            
            print("=" * 60)
            print(" 🧭  Matspanet - Local Dev Server (v2)")
            print("=" * 60)
            print(f" 📂  Data folder  : {os.path.abspath(DATA_FOLDER)}")
            print(f" 📂  Pages folder : {os.path.abspath(PAGES_FOLDER)}")
            print(f" 🌐  Address      : http://localhost:{port}")
            print(f" 🔐  Login page   : http://localhost:{port}/login.html")
            print(f" ⏰  Timeout      : {TIMEOUT} seconds")
            print("=" * 60)
            print(" 🟢  Press Ctrl+C to stop")
            print("=" * 60)
            print()
            
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n🛑  Server stopped by user")
            except Exception as e:
                print(f"❌  Server error: {e}")
                traceback.print_exc()
                
    except socket.error as e:
        print(f"❌  Socket error: {e}")
        print(f"   Port {port} might be in use. Try changing the port.")
        sys.exit(1)
    except Exception as e:
        print(f"❌  Failed to start server: {e}")
        traceback.print_exc()
        sys.exit(1)

# ============================================================
# כניסה ראשית
# ============================================================

if __name__ == "__main__":
    port = PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌  Invalid port: {sys.argv[1]}")
            print("   Usage: python server.py [port]")
            sys.exit(1)
    
    run_server(port)