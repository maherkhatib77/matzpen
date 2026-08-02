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