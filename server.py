#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Matspanet - Local Development Server
with enhanced error handling for ConnectionAbortedError
"""

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
import threading
import time

# ============================================================
# הגדרות בסיסיות
# ============================================================

PORT = 8000
DATA_FOLDER = "data"
PAGES_FOLDER = "pages"

# הגדרת טיימאוט לחיבורים
socket.setdefaulttimeout(60)  # 60 שניות

# התעלמות משגיאות BrokenPipe
try:
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)
except AttributeError:
    pass  # Windows לא תומך ב-SIGPIPE

# ============================================================
# מחלקת Handler מותאמת עם טיפול בשגיאות
# ============================================================

class CustomHandler(SimpleHTTPRequestHandler):
    """Handler מותאם עם טיפול משופר בשגיאות חיבור"""
    
    server_version = "Matspanet/1.0"
    
    def __init__(self, *args, **kwargs):
        # הגדרת טיימאוט לקריאה וכתיבה
        super().__init__(*args, **kwargs)
        if hasattr(self, 'connection'):
            self.connection.settimeout(30)
    
    # ============================================================
    # שיטת do_GET עם טיפול בשגיאות (פתרון 1)
    # ============================================================
    
    def do_GET(self):
        """טיפול בבקשת GET עם הגנה מפני ניתוקים"""
        try:
            # בדיקה אם זו בקשת API
            if self.path.startswith('/api/'):
                self.handle_api_request()
                return
            
            # טיפול בבקשת קובץ רגילה
            super().do_GET()
            
        except ConnectionAbortedError as e:
            print(f"⚠️  Client disconnected during GET: {e}")
            # לא מחזירים תגובה כי החיבור כבר נותק
        except BrokenPipeError as e:
            print(f"⚠️  Broken pipe during GET: {e}")
        except ConnectionResetError as e:
            print(f"⚠️  Connection reset during GET: {e}")
        except socket.timeout as e:
            print(f"⚠️  Socket timeout during GET: {e}")
        except Exception as e:
            print(f"❌  Error in GET request: {e}")
            traceback.print_exc()
            try:
                self.send_error(500, f"Internal Server Error: {str(e)}")
            except:
                pass
    
    # ============================================================
    # שיטת do_POST עם טיפול בשגיאות (פתרון 1)
    # ============================================================
    
    def do_POST(self):
        """טיפול בבקשת POST עם הגנה מפני ניתוקים"""
        try:
            if self.path.startswith('/api/'):
                self.handle_api_request()
            else:
                self.send_error(404, "Not Found")
                
        except ConnectionAbortedError as e:
            print(f"⚠️  Client disconnected during POST: {e}")
        except BrokenPipeError as e:
            print(f"⚠️  Broken pipe during POST: {e}")
        except ConnectionResetError as e:
            print(f"⚠️  Connection reset during POST: {e}")
        except socket.timeout as e:
            print(f"⚠️  Socket timeout during POST: {e}")
        except Exception as e:
            print(f"❌  Error in POST request: {e}")
            traceback.print_exc()
            try:
                self.send_error(500, f"Internal Server Error: {str(e)}")
            except:
                pass
    
    # ============================================================
    # שיטת copyfile עם הגנה (פתרון 2)
    # ============================================================
    
    def copyfile(self, source, outputfile):
        """
        העתקת קובץ עם הגנה מפני ניתוקי חיבור
        """
        try:
            # הגדרת טיימאוט לכתיבה
            if hasattr(outputfile, 'settimeout'):
                outputfile.settimeout(60)
            
            # העתקת הקובץ עם טיפול בשגיאות
            chunk_size = 8192  # קריאה בנתחים קטנים להגנה
            while True:
                try:
                    buf = source.read(chunk_size)
                    if not buf:
                        break
                    outputfile.write(buf)
                    
                    # ניקוי מאגר הכתיבה מעת לעת
                    if hasattr(outputfile, 'flush'):
                        outputfile.flush()
                        
                except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
                    print(f"⚠️  Client disconnected during file copy: {e}")
                    return
                except socket.timeout as e:
                    print(f"⚠️  Socket timeout during file copy: {e}")
                    return
                    
        except Exception as e:
            print(f"❌  Error copying file: {e}")
            traceback.print_exc()
            raise
    
    # ============================================================
    # שיטת copyfileobj מותאמת (פתרון 2 - הרחבה)
    # ============================================================
    
    def copyfileobj_enhanced(self, source, outputfile, length=8192):
        """
        העתקת אובייקט קובץ עם הגנה מפני ניתוקים
        """
        try:
            if hasattr(outputfile, 'settimeout'):
                outputfile.settimeout(60)
            
            while True:
                try:
                    buf = source.read(length)
                    if not buf:
                        break
                    
                    # ניסיון כתיבה עם הגנה
                    try:
                        outputfile.write(buf)
                    except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
                        print(f"⚠️  Client disconnected during write: {e}")
                        return
                    
                    if hasattr(outputfile, 'flush'):
                        outputfile.flush()
                        
                except (ConnectionAbortedError, BrokenPipeError, ConnectionResetError) as e:
                    print(f"⚠️  Client disconnected during read: {e}")
                    return
                except socket.timeout as e:
                    print(f"⚠️  Socket timeout during copy: {e}")
                    return
                    
        except Exception as e:
            print(f"❌  Error in enhanced copy: {e}")
            traceback.print_exc()
    
    # ============================================================
    # טיפול בבקשות API
    # ============================================================
    
    def handle_api_request(self):
        """טיפול בבקשות API"""
        try:
            parsed_path = urlparse(self.path)
            endpoint = parsed_path.path
            
            if endpoint == '/api/data-save':
                self.handle_data_save()
            elif endpoint == '/api/data-load':
                self.handle_data_load()
            else:
                self.send_error(404, "API endpoint not found")
                
        except Exception as e:
            print(f"❌  API error: {e}")
            traceback.print_exc()
            try:
                self.send_error(500, f"API Error: {str(e)}")
            except:
                pass
    
    def handle_data_save(self):
        """שמירת נתונים"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length)
                data = json.loads(post_data.decode('utf-8'))
                
                # שמירת הנתונים
                filename = data.get('filename', 'activity_log.json')
                filepath = os.path.join(DATA_FOLDER, filename)
                
                # יצירת תיקייה אם לא קיימת
                os.makedirs(DATA_FOLDER, exist_ok=True)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = json.dumps({'success': True, 'message': 'Data saved successfully'})
                self.wfile.write(response.encode('utf-8'))
                
                print(f"✅  Saved {filename} ({len(post_data)} bytes)")
                
        except json.JSONDecodeError as e:
            print(f"❌  JSON decode error: {e}")
            self.send_error(400, "Invalid JSON data")
        except Exception as e:
            print(f"❌  Error saving data: {e}")
            traceback.print_exc()
            self.send_error(500, f"Error saving data: {str(e)}")
    
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
    # שיטת log_message מותאמת (הדפסת שגיאות יפות)
    # ============================================================
    
    def log_message(self, format, *args):
        """הדפסת הודעות לוג בצורה מותאמת"""
        try:
            message = format % args
            print(f"🔄  {self.client_address[0]} - {message}")
        except:
            pass

# ============================================================
# פונקציות הרצת השרת
# ============================================================

def run_server(port=PORT):
    """הרצת השרת עם טיפול משופר בשגיאות"""
    
    # בדיקת תיקיות נדרשות
    for folder in [DATA_FOLDER, PAGES_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁  Created folder: {folder}")
    
    handler = CustomHandler
    
    # יצירת השרת עם טיימאוט
    try:
        with HTTPServer(("", port), handler) as httpd:
            # הגדרת טיימאוט לסוקט
            httpd.socket.settimeout(60)
            httpd.timeout = 60
            
            print("=" * 60)
            print(" 🧭  Matspanet - Local Dev Server")
            print("=" * 60)
            print(f" 📂  Data folder  : {os.path.abspath(DATA_FOLDER)}")
            print(f" 📂  Pages folder : {os.path.abspath(PAGES_FOLDER)}")
            print(f" 🌐  Address      : http://localhost:{port}")
            print(f" 🔐  Login page   : http://localhost:{port}/login.html")
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
    # קבלת פורט משורת הפקודה אם צוין
    port = PORT
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌  Invalid port: {sys.argv[1]}")
            print("   Usage: python server.py [port]")
            sys.exit(1)
    
    # הרצת השרת
    run_server(port)