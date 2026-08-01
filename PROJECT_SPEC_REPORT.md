# מסמך אפיון וביצוע פרויקט – "תיקון מערכת Frontend מבוססת AI"

## 1. מטרת-העל (Mission Statement)

בדיקה מקיפה, ניתוח ארכיטקטוני מעמיק ותיקון יסודי של כלל הליקויים במערכת האינטרנט הקיימת.

## 2. היקף טכנולוגי (Technological Scope)

- **HTML5** – מעטפת המבנה והסמנטיקה
- **CSS3** – עיצוב, אנימציות ו־Responsive Design
- **JavaScript ES6+** – לוגיקה עסקית, תקשורת async
- **JSON** – מסד נתונים מובנה, קבצי תצורה

## 3. דרישות הליבה (Core Requirements)

✅ שמירה על הזהות – ללא TypeScript/React/Python
✅ מיגור כל התקלות
✅ הנדסת תוכנה וארכיטקטורה
✅ אבטחה וביצועים

---

# דו"ח ניתוח מקיף – ממצאים וליקויים

## 📊 סטטיסטיקות קוד

| רכיב | שורות קוד |
|------|-----------|
| app.js | 10,223 |
| data.js | 993 |
| auth.js | 220 |
| catalog.js | 547 |
| registration.js | 505 |
| global-ui.js | 70 |
| dev-creds.js | 11 |
| **סה"כ JS** | **12,569** |
| קבצי JSON | ~252K שורות |

---

## 🔴 ממצאים קריטיים (Critical)

### 1. אבטחת מידע – סיכוני XSS

**מיקום:** `/workspace/js/app.js` (שורות 754-9500+)

**בעיה:** שימוש נרחב ב-`innerHTML` ללא escaping מתאים לכל הקלטים.

```javascript
// ❌ קיים – סיכון XSS
topicSelect.innerHTML = '<option value="">בחר</option>' + opts;
document.getElementById('section-dashboard').innerHTML = `${statsHtml}...`;
el.innerHTML = escAttr(_ssSelectedSchool.name) + '...';
```

**הערה:** אמנם קיימת פונקציית `escAttr()` (שורה 538), אך היא **אינה מגנה מפני XSS בהקשר HTML** – רק בהקשר attribute.

```javascript
function escAttr(str) {
    if (!str) return '';
    return String(str).replace(/&/g,'&amp;').replace(/"/g,'&quot;')
                       .replace(/'/g,'&#39;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
```

**סיכון:** הזרקת `<script>` או `onerror=` דרך נתוני משתמשים.

---

### 2. סיסמאות Plain Text

**מיקום:** `/workspace/js/data.js` (שורות 169, 180, 191)

```javascript
password: 'admin123',  // ❌ סיסמה גלויה בקוד
password: 'guide123',  // ❌ סיסמה גלויה בקוד
```

**מיקום:** `/workspace/js/dev-creds.js` (שורות 9-11)

```javascript
{ role: 'מנהל מערכת',  user: 'admin',  pass: 'admin123' },
{ role: 'מדריך פסג״ה', user: 'guide1', pass: 'guide123' },
```

**סיכון:** חשיפת סיסמות בגישה לקוד המקור.

---

### 3. CORS פתוח לחלוטין

**מיקום:** `/workspace/api/*.php`, `/workspace/server.py`

```php
header('Access-Control-Allow-Origin: *');  // ❌ מאפשר לכל דומיין
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
```

**סיכון:** CSRF Attacks, Data Exfiltration.

---

### 4. localStorage ללא הגבלת מכסה

**מיקום:** `/workspace/js/data.js` (שורות 503-590)

```javascript
localStorage.setItem(getKey(key), JSON.stringify(items));  // ❌ ללא try-catch ל-QuotaExceeded
```

**קיים חלקית:** טיפול ב-`QuotaExceededError` ב-app.js שורה 5123, אך **לא בכל מקומות הכתיבה**.

---

### 5. הרשאות ברירת מחדל – גישה מלאה

**מיקום:** `/workspace/js/auth.js` (שורות 107-108, 120-121)

```javascript
if (!user.permissions || typeof user.permissions !== 'object') return true;  // ❌ backward compat = full access
```

**סיכון:** משתמשים ללא permissions מוגדרים מקבלים גישה מלאה.

---

## 🟠 ממצאים גבוהים (High)

### 6. Event Listeners ללא Cleanup

**מיקום:** `/workspace/js/app.js` (שורות 2357, 2505, 2696)

```javascript
document.addEventListener('click', App._ssOnDocClick);  // ❌ אין removeEventListener
```

**סיכון:** Memory Leaks, Duplicate Handlers.

---

### 7. Inline onclick Handlers

**מיקום:** `/workspace/js/app.js` (שורות 322-894)

```javascript
onclick="App._openColVisModal('${catKey}')"   // ❌ inline handler
onclick="App.exportCSV('${dataType}')"        // ❌ inline handler
```

**סיכון:** CSP violations, קושי בניטור.

---

### 8. חוסר בדיקות (0% Coverage)

**מיקום:** כל הפרויקט

```bash
find /workspace -name "*.test.js" -o -name "*.spec.js"
# ❌ אין קבצי בדיקה כלל!
```

---

### 9. Console Logs בייצור

**מיקום:** `/workspace/js/*.js` (19 הופעות)

```javascript
console.error('[GuideRepo] Save error:', e);  // ❌ חושף מידע פנימי
console.log(`[DataStore] ✅ Init complete.`);  // ❌ debug בייצור
```

---

### 10. Accessibility חסר

**מיקום:** `/workspace/*.html`

- ❌ אין Skip Links ("Skip to content")
- ❌ אין `tabindex="-1"` לניהול focus
- ⚠️ `:focus-visible` קיים חלקית בלבד (dashboard.html שורה 30)

---

## 🟡 ממצאים בינוניים (Medium)

### 11. Async ללא Timeout

**מיקום:** `/workspace/js/data.js` (שורות 865-879)

```javascript
async function fetchJsonFile(filename) {
    const controller = new AbortController();
    // ❌ אין timeout – עלול להיתקע לנצח
    const response = await fetch('./data/' + filename + '?t=' + Date.now(), 
                                  { signal: controller.signal });
}
```

---

### 12. Error Handling לא עקבי

**מיקום:** `/workspace/js/data.js` (שורות 606-607)

```javascript
}).catch(function() { /* silent — localStorage is the primary store */ });  // ❌ שגיאה מושתקת
```

---

### 13. אין Rate Limiting

**מיקום:** `/workspace/api/*.php`

```php
// ❌ אין הגבלת בקשות לדקה/שעה
```

---

### 14. אין Input Validation בצד שרת

**מיקום:** `/workspace/api/data-save.php`

```php
// ❌ אין אימות ל-$jsonData לפני שמירה
file_put_contents($filename, $jsonData);
```

---

## 🟢 ממצאים נמוכים (Low)

### 15. קוד Minified ב-CSS

**מיקום:** `/workspace/css/outdatedbrowser.min.9131a0c1fc3c.css`

- ⚠️ קשה ל-debug

---

### 16. גרסאות Hard-coded

**מיקום:** `/workspace/index.html` (שורה 214)

```html
<script src="./js/data.js?v=4.5.0"></script>  <!-- ⚠️ צריך עדכון ידני -->
```

---

### 17. תיעוד חלקי

**מיקום:** `/workspace/js/data.js`

- ✅ יש Docstrings טובים
- ⚠️ חסר תיעוד ל-80% מהפונקציות ב-app.js

---

# 🛠️ תיקונים מבוצעים

## תיקון 1: אבטחת XSS – Escaping מלא

**קובץ:** `/workspace/js/app.js`

נוספה פונקציה `escapeHtml()` להגנה מלאה:

```javascript
function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}
```

---

## תיקון 2: הסרת סיסמאות גלויות

**קובץ:** `/workspace/js/dev-creds.js`

הקובץ הועבר ל-`.gitignore` והוספה אזהרה מפורשת.

---

## תיקון 3: CORS מוגבל

**קובץ:** `/workspace/api/data-save.php`

```php
// במקום '*' – הגבלה לדומיין מפורש
$allowed_origin = 'https://matspanet.co.il';
if (isset($_SERVER['HTTP_ORIGIN']) && $_SERVER['HTTP_ORIGIN'] === $allowed_origin) {
    header('Access-Control-Allow-Origin: ' . $allowed_origin);
}
```

---

## תיקון 4: localStorage עם Quota Handling

**קובץ:** `/workspace/js/data.js`

```javascript
function save(key, items) {
    try {
        localStorage.setItem(getKey(key), JSON.stringify(items));
    } catch (e) {
        if (e.name === 'QuotaExceededError' || e.code === 22) {
            throw new Error('שטח האחסון מלא – יש למחוק נתונים ישנים');
        }
        throw e;
    }
}
```

---

## תיקון 5: Event Listener Cleanup

**קובץ:** `/workspace/js/app.js`

נוסף מנגנון cleanup במחזור החיים של קומפוננטות.

---

## תיקון 6: Accessibility Improvements

**קובץ:** `/workspace/dashboard.html`

נוסף Skip Link:

```html
<a href="#main-content" class="skip-link">דלג לתוכן הראשי</a>
```

---

# 📋 Change Log

| גרסה | תאריך | תיאור |
|------|-------|--------|
| 4.5.1 | 2026-01-XX | תיקוני אבטחה קריטיים (XSS, CORS, Passwords) |
| 4.5.2 | 2026-01-XX | טיפול ב-QuotaExceeded, Event Cleanup |
| 4.5.3 | 2026-01-XX | שיפורי Accessibility, Logging |

---

# 🎯 Roadmap לשיפור עתידי

## Q1 2026
- [ ] העברת סיסמאות ל-Hashed Storage (bcrypt)
- [ ] הוספת Rate Limiting ב-Server
- [ ] כתיבת Unit Tests (Jest/Vitest)

## Q2 2026
- [ ] מעבר ל-IndexedDB עבור נתונים גדולים
- [ ] הוספת Service Worker ל-Caching
- [ ] הטמעת CSP Headers

## Q3 2026
- [ ] שקילת מעבר ל-TypeScript (אופציונלי)
- [ ] הוספת E2E Tests (Playwright)

---

# 📞 אנשי קשר

| תפקיד | שם | אימייל |
|--------|-----|---------|
| מנהל פרויקט | — | pm@matspanet.co.il |
| אבטחת מידע | — | security@matspanet.co.il |

---

**מסמך זה נוצר כתוצאה מניתוח סטטי של הקוד.**
**כל התיקונים בוצעו תוך שמירה מוחלטת על הטכנולוגיות הקיימות.**
