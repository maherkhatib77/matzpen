# מסמך אפיון טכני-מערכתי: קטגוריית "קטלוג פתרונות למידה"
**מערכת:** מצפן נט – מרכז לפיתוח סגלי הוראה  
**תאריך:** 24 במאי 2026  
**גרסת מסמך:** 1.0  
**מחבר:** צוות פיתוח מערכות

---

## 1. תקציר מנהלים

מסמך זה מתעד את האפיון הטכני והתהליכי של קטגוריית "פתרונות למידה" (השתלמויות) במערכת מצפן נט. המסמך מכסה את מבנה נתוני הצד האחורי (Back End), מנגנוני ייבוא/ייצוא, תהליכי עיבוד נתונים, ואופן התצוגה בצד הקדמי (Front End) בדף `catalog.html`.

---

## 2. ארכיטקטורת נתונים (Back End)

### 2.1 טבלאות ליבה מעורבות

| שם הטבלה (קובץ JSON) | מפתח ב-DataStore | תיאור | רשומות נוכחיות |
|----------------------|------------------|--------|----------------|
| `solutions.json` | `DataStore.KEYS.SOLUTIONS` | רשומות פתרונות למידה (השתלמויות) | ~18 רשומות פעילות |
| `solution_instructors.json` | `DataStore.KEYS.SOLUTION_INSTRUCTORS` | קישור מנחים לפתרונות (טבלת יחס רבים-לרבים עם נתונים נוספים) | ~17,378 רשומות (רובן ריקות) |
| `mentors.json` | `DataStore.KEYS.MENTORS` | מאגר מנחים/מרצים חיצוניים | ~21 רשומות |
| `guides_repo.json` | `DataStore.KEYS.GUIDES_REPO` | מאגר מדריכי פסג"ה (גורמים אחראיים) | 22 רשומות |
| `periods.json` | `DataStore.KEYS.PERIODS` | הגדרת תקופות שנתיות (תקופה א', תקופה ב') | מספר תקופות |

### 2.2 טבלאות עזר (Lookup Tables)

| שם הטבלה | מפתח | שדות עיקריים | שימוש |
|----------|------|--------------|-------|
| `lookup_domains.json` | `LOOKUP_DOMAINS` | `value`, `label`, `labelAr` | תחום ונושא (תחום דעת, בעלי תפקידים, נושא רוחב, etc.) |
| `lookup_field_knowledge.json` | `LOOKUP_FIELD_KNOWLEDGE` | `value`, `label`, `labelAr` | נושאי דעת ספציפיים (מתמטיקה, היסטוריה, etc.) |
| `lookup_education_stages.json` | `LOOKUP_EDUCATION_STAGES` | `value`, `label`, `labelAr`, `order` | שלבי חינוך (יסודי, חטיבה, etc.) |
| `lookup_education_types.json` | `LOOKUP_EDUCATION_TYPES` | `value`, `label`, `labelAr` | סוג חינוך (רגיל, חינוך מיוחד) |
| `lookup_meeting_types.json` | `LOOKUP_MEETING_TYPES` | `value`, `label`, `labelAr` | סוג מפגש (פנים אל פנים, סינכרוני, היברידי) |
| `lookup_week_days.json` | `LOOKUP_WEEK_DAYS` | `value`, `label`, `labelAr` | ימים בשבוע (א', ב', etc.) |
| `lookup_budget_types.json` | `LOOKUP_BUDGET_TYPES` | `value`, `label`, `labelAr` | סוגי תקצוב |
| `lookup_responsibility_types.json` | `LOOKUP_RESPONSIBILITY_TYPES` | `value`, `label`, `labelAr` | סוג אחריות (פסג"ה, בית-ספרי) |
| `lookup_solution_status.json` | `LOOKUP_SOLUTION_STATUS` | `value`, `label`, `labelAr` | סטטוס פתרון (פעיל, בתכנון, הושלם) |
| `lookup_performer_types.json` | `LOOKUP_PERFORMER_TYPES` | `value`, `label`, `labelAr` | סוג מבצע (external, internal, pedagogical) |

### 2.3 מבנה רשומת פתרון למידה (`solutions.json`)

| שדה | סוג | תיאור | דוגמה | שפה |
|-----|-----|-------|-------|-----|
| `id` | String (ID ייחודי) | מזהה ייחודי של הפתרון | `"msa60ti89iwjjqge2"` | - |
| `name` | String | שם הפתרון **בערבית** | `"نواب المدراء ابتدائي وتربية خاصة"` | ערבית |
| `description` | String | תיאור מפורט **בערבית** | `"يهدف الاستكمال إلى..."` | ערבית |
| `solutionNumber` | String | מספר פתרון (לרוב ריק) | `""` | - |
| `guideId` | String (FK) | מזהה המדריך האחראי מ-`guides_repo` | `"ms6fjlun4y7vydkxf"` | - |
| `topicType` | String (FK) | תחום כללי מ-`lookup_domains` | `"בעלי תפקידים"` | עברית |
| `topic` | String (FK) | נושא ספציפי מ-`lookup_field_knowledge` | `"סגן מנהל"` | עברית |
| `educationStage` | Array[String] | שלבי חינוך (ערכים מ-`lookup_education_stages`) | `["יסודי", "בתי ספר לחינוך מיוחד"]` | עברית |
| `educationType` | Array[String] | סוגי חינוך (ערכים מ-`lookup_education_types`) | `["רגיל", "חינוך מיוחד"]` | עברית |
| `startDate` | String | תאריך התחלה (לעיתים טקסט חופשי בערבית) | `"سيتم التحديد مع كلية كاي"` | ערבית/תאריך |
| `endDate` | String | תאריך סיום | `""` | - |
| `weekDay` | String (FK) | יום בשבוע מ-`lookup_week_days` | `"א"` | עברית |
| `meetingType` | String (FK) | סוג מפגש מ-`lookup_meeting_types` | `"היברידי"` | עברית |
| `academicHours` | Number | סך שעות אקדמיות לגמול | `40` | - |
| `whatsappLink` | String (URL) | קישור לקבוצת וואטסאפ | `"https://chat.whatsapp.com/..."` | - |
| `earlyRegistrationLink` | String (URL) | קישור לרישום מוקדם | `""` | - |
| `showInCatalog` | Boolean | האם להציג בקטלוג הציבורי | `true` | - |
| `budgetType` | String | סוג תקצוב (מתוקצב/לא מתוקצב) | `"מתוקצב"` | עברית |
| `budgetTypeValue` | String | פירוט סוג תקצוב מ-`lookup_budget_types` | `"תקציב רגיל"` | עברית |
| `budgetedHours` | Number | שעות מתוקצבות כוללות | `30` | - |
| `status` | String (FK) | סטטוס מ-`lookup_solution_status` | `"בתכנון"` | עברית |
| `responsibilityType` | String (FK) | סוג אחריות מ-`lookup_responsibility_types` | `"פסגה"` | עברית |
| `schoolName` | String | שם בית ספר (לפתרונות בית-ספריים) | `""` | - |
| `periodId` | String (FK) | מזהה תקופה מ-`periods.json` | `"ms4yv1ix1xah39iaf"` | - |
| `notes` | String | הערות כלליות | `""` | - |
| `createdBy` | String | מזהה יוצר הרשומה | `"usr_admin_001"` | - |
| `createdAt` | DateTime | תאריך יצירה | `"2026-08-01T09:24:53.216Z"` | - |
| `updatedAt` | DateTime | תאריך עדכון אחרון | `"2026-08-01T09:24:53.216Z"` | - |

### 2.4 מבנה רשומת מנחה משויך (`solution_instructors.json`)

| שדה | סוג | תיאור | דוגמה |
|-----|-----|-------|-------|
| `id` | String | מזהה ייחודי של הקישור | `"msa60tiai2hialhd9"` |
| `solutionId` | String (FK) | מזהה הפתרון מ-`solutions` | `"msa60ti89iwjjqge2"` |
| `mentorId` | String (FK) או null | מזהה המנחה מ-`mentors.json` (אם קיים) | `null` |
| `fullName` | String | שם המנחה (ישירות אם אין mentorId) | `"כוח פנים"` / `"מייסון מילחם"` |
| `idNumber` | String | תעודת זהות (לרוב ריק) | `""` |
| `phone` | String | טלפון | `""` |
| `email` | String | דוא"ל | `""` |
| `performerType` | String (FK) | סוג מבצע מ-`lookup_performer_types` | `"כוח פנים"` / `""` |
| `lecturerStatus` | String | סטטוס מרצה | `""` |
| `totalAcademicHours` | Number | סך שעות כולל | `10` |
| `period1Hours` | Number | שעות תקופה ב' (09-12) | `0` |
| `period2Hours` | Number | שעות תקופה א' (01-08) | `0` |
| `isAccompaniment` | Boolean | האם שעות ליווי | `false` |

**הערה קריטית:** שמות המנחים מאוחסנים בשני אופנים:
1. **עבור מנחים ממאגר mentors:** השמות נשמרים ב-`mentors.json` עם שדות `fullNameHe` ו-`fullNameAr`
2. **עבור "כוח פנים" או מנחים ללא רשומה:** השם נשמר ישירות ב-`solution_instructors.fullName`

### 2.5 מבנה מדריך אחראי (`guides_repo.json`)

| שדה | סוג | תיאור | דוגמה |
|-----|-----|-------|-------|
| `id` | String | מזהה ייחודי | `"ms6fjlun4y7vydkxf"` |
| `idNumber` | String | תעודת זהות | `"304910847"` |
| `fullName` | String | שם מלא בעברית | `"סולימאן נבין"` |
| `fullNameAr` | String | שם מלא בערבית | `"نيفين سليمان"` |
| `position` | String | תפקיד (בערבית) | `"مركّزة تربوية ومرشدة للتطوير المهني المدرسي"` |
| `phone` | String | טלפון | `"528089296"` |
| `email` | String | דוא"ל | `"neveen.suliman32@gmail.com"` |
| `specializations` | String | תחומי התמחות (ערבית, מופרד ב-\r\n) | `"الرفاه النفسي والمهني Well Being\r\nالتعلم الاجتماعي العاطفي SEL"` |

### 2.6 יחסי גומלין בין טבלאות (ERD)

```
┌─────────────────────┐
│     solutions       │
│  (פתרונות למידה)    │
└─────────┬───────────┘
          │
          │ guideId → guides_repo.id (יחס רבים-לאחד)
          │ periodId → periods.id (יחס רבים-לאחד)
          │
          ▼
┌─────────────────────┐         ┌─────────────────────┐
│ solution_instructors│ ◄────── │      mentors        │
│ (מנחים משויכים)     │ mentorId│   (מאגר מנחים)      │
└─────────┬───────────┘         └─────────────────────┘
          │
          │ solutionId → solutions.id (יחס רבים-אחד)
          │
          ▼
┌─────────────────────┐
│ lookup_* tables     │
│ (טבלאות עזר)        │
└─────────────────────┘
```

**יחסים:**
- **solutions → guides_repo:** יחס רבים-לאחד (כל פתרון משויך למדריך אחראי אחד)
- **solutions → solution_instructors:** יחס אחד-לרבים (כל פתרון יכול לכלול מספר מנחים)
- **solution_instructors → mentors:** יחס רבים-לאחד (אופציונלי, יכול להיות null עבור "כוח פנים")
- **solutions → lookup_*:** יחסים רבים-לאחד דרך ערכי FK

---

## 3. תהליך שליפת נתונים (Query Flow)

### 3.1 שליפת פתרון בודד להצגה

```javascript
// שלב 1: שליפת הפתרון עצמו
const solution = DataStore.getById(DataStore.KEYS.SOLUTIONS, solutionId);

// שלב 2: שליפת המדריך האחראי
const guide = DataStore.getById(DataStore.KEYS.GUIDES_REPO, solution.guideId);

// שלב 3: שליפת כל המנחים המשויכים לפתרון זה
const instructors = (DataStore.getAll(DataStore.KEYS.SOLUTION_INSTRUCTORS) || [])
    .filter(i => i.solutionId === solutionId);

// שלב 4: עבור כל מנחה עם mentorId, שליפת פרטים נוספים
instructors.forEach(inst => {
    if (inst.mentorId) {
        const mentor = DataStore.getById(DataStore.KEYS.MENTORS, inst.mentorId);
        // שימוש ב-mentor.fullNameHe / mentor.fullNameAr
    } else {
        // שימוש ב-inst.fullName ישירות
    }
});

// שלב 5: המרת ערכי Lookup לתוויות לפי שפה
const topicTypeLabel = getLookupLabel(DataStore.KEYS.LOOKUP_DOMAINS, solution.topicType);
const stageLabels = solution.educationStage.map(id => 
    getLookupLabel(DataStore.KEYS.LOOKUP_EDUCATION_STAGES, id));
```

### 3.2 פונקציית עזר `getLookupLabel`

```javascript
function getLookupLabel(lookupKey, value) {
    if (!value) return '';
    const list = DataStore.getAll(lookupKey) || [];
    const item = list.find(l => l.value === value);
    if (!item) return value;
    // בחירת שפה: ערבית מעדיפה labelAr, עברית מעדיפה label
    return lang === 'ar' ? (item.labelAr || item.label || item.value) 
                         : (item.label || item.value);
}
```

---

## 4. תהליך ייבוא נתונים מאקסל

### 4.1 מנגנון כללי

הייבוא מתבצע באמצעות ספריית `XLSX` (SheetJS) בדף הניהול (`app.js`):

1. **העלאת קובץ:** המשתמש בוחר קובץ `.xlsx` דרך `<input type="file">`
2. **קריאה ועיבוד:** הקובץ נקרא כ-`ArrayBuffer` ומעובד ל-JSON
3. **מיפוי עמודות:** המערכת מציגה חלונית מיפוי המאפשרת להתאים עמודות מהקובץ לשדות במערכת
4. **אימות והמרה:** ביצוע המרות סוגים (תאריכים, מספרים) ואימות ערכים
5. **שמירה:** כתיבת הרשומות ל-`localStorage` דרך `DataStore.create()` או `DataStore.update()`

### 4.2 מיפוי עמודות לפתרונות למידה

**כותרות עמודות צפויות בקובץ הייבוא:**

| עמודה | שדה ב-JSON | הערות |
|-------|-----------|-------|
| סוג האחריות | `responsibilityType` | ערך מ-`lookup_responsibility_types` |
| שם בית הספר | `schoolName` | טקסט חופשי |
| שם פתרון למידה | `name` | **בערבית** |
| מספר פתרון | `solutionNumber` | טקסט חופשי |
| תיאור | `description` | **בערבית** |
| מדריך אחראי | `guideId` | יש לחפש לפי שם ב-`guides_repo` |
| תחום | `topicType` | ערך מ-`lookup_domains` |
| נושא | `topic` | ערך מ-`lookup_field_knowledge` |
| שלב חינוך | `educationStage` | מערך ערכים מופרדים בפסיק |
| סוג חינוך | `educationType` | מערך ערכים מופרדים בפסיק |
| תאריך התחלה | `startDate` | תאריך או טקסט חופשי |
| תאריך סיום | `endDate` | תאריך |
| יום בשבוע | `weekDay` | ערך מ-`lookup_week_days` |
| סוג מפגש | `meetingType` | ערך מ-`lookup_meeting_types` |
| שעות אקדמיות | `academicHours` | מספר |
| מתוקצב? | `budgetType` | "כן"/"לא" או "מתוקצב"/"לא מתוקצב" |
| סה״כ שעות מתוקצבות | `budgetedHours` | מספר |
| סוג תקצוב | `budgetTypeValue` | ערך מ-`lookup_budget_types` |
| סוג המנחה | `performerType` | ערך מ-`lookup_performer_types` |
| שם המנחה | `fullName` (ב-`solution_instructors`) | טקסט |
| שעות תקופה ב׳ | `period1Hours` | מספר |
| שעות תקופה א׳ | `period2Hours` | מספר |
| קישור וואטסאפ | `whatsappLink` | URL |
| קישור רישום | `earlyRegistrationLink` | URL |
| הצג בקטלוג | `showInCatalog` | "כן"/"לא" → Boolean |
| הערה | `notes` | טקסט חופשי |

### 4.3 קוד מיפוי ב-`app.js`

```javascript
// מתוך app.js, שורות 7256-7293
function startImport(file, targetKey, type) {
    _importTargetKey = targetKey || null;
    
    if (file.type.includes('excel')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const wb = XLSX.read(e.target.result, { type: 'array', cellDates: true });
            const ws = wb.Sheets[wb.SheetNames[0]];
            const rawRows = XLSX.utils.sheet_to_json(ws, { header: 1, defval: '' });
            
            const headers = rawRows[0].map(h => h.trim());
            const rows = rawRows.slice(1);
            
            importWizardData = { type, headers, rows, mappings: {} };
            showMappingDialog(); // הצגת חלונית מיפוי
        };
        reader.readAsArrayBuffer(file);
    }
}
```

### 4.4 אתגרי ייבוא מזוהים

1. **שפות מעורבות:** שמות הפתרונות והתיאורים בערבית, אך ערכי ה-Lookup בעברית
2. **מנחים מרובים:** כל שורה באקסל מייצגת פתרון+מנחה אחד; פתרון עם 5 מנחים ייוצר כ-5 רשומות ב-`solution_instructors`
3. **"כוח פנים":** מנחים מסוג זה אינם דורשים רשומה ב-`mentors.json`
4. **תאריכים:** חלק מהתאריכים מופיעים כטקסט חופשי בערבית ("سيتم التحديد...")

---

## 5. תצוגת Front End (`catalog.html`)

### 5.1 שדות המוצגים בכרטיסיית פתרון

**כרטיסייה מינימלית (Grid View):**

| אלמנט | מקור הנתונים | עיבוד מקדים |
|-------|--------------|-------------|
| פס צבעוני עליון | `topic` → `getFieldColor()` | מיפוי לצבע לפי שם הנושא |
| שם הפתרון | `solution.name` | מוצג כ-is (ערבית) |
| שמות מנחים | `solution_instructors` + `mentors` | צירוף כל השמות עם תרגום לערבית |
| תגים (Badges) | `topicType`, `meetingType`, `weekDay`, `academicHours` | המרת ערכי Lookup לתוויות בערבית |
| כפתור "לפרטים" | - | פותח Modal |
| כפתור "רישום מוקדם" | - | קישור ל-`registration.html?solution={id}` |

**חלון פרטים מלא (Modal):**

| שדה | תווית (ערבית) | מקור הנתונים |
|-----|---------------|--------------|
| وصف (תיאור) | `descriptionLabel` | `solution.description` |
| المحاضرين (מנחים) | `mentorsLabel` | `getMentorNames(solutionId)` |
| المرشد المسؤول (מדריך אחראי) | `guideLabel` | `getGuideName(solution.guideId)` |
| مجال وموضوع (תחום ונושא) | `topicTypeLabel` | `lookup_domains` + `lookup_field_knowledge` |
| مرحلة تعليمية (שלב חינוך) | `educationStageLabel` | `lookup_education_stages` (Array) |
| نوع التعليم (סוג חינוך) | `educationTypeLabel` | `lookup_education_types` (Array) |
| تاريخ البدء (תאריך התחלה) | `startDateLabel` | `solution.startDate` + `formatDate()` |
| يوم في الأسبوع (יום בשבוע) | `weekDayLabel` | `lookup_week_days` |
| نوع اللقاء (סוג מפגש) | `meetingTypeLabel` | `lookup_meeting_types` |
| ساعات أكاديمية (שעות אקדמיות) | `academicHoursLabel` | `solution.academicHours` |
| ملاحظة (הערה) | `notesLabel` | `solution.notes` |
| واتساب (WhatsApp) | - | `solution.whatsappLink` (כפתור) |
| تسجيل مسبق (רישום מוקדם) | - | `solution.earlyRegistrationLink` (כפתור) |

### 5.2 תהליך רנדור הכרטיסייה

```javascript
// מתוך catalog.js, שורות 364-410
function createCard(item) {
    const card = document.createElement('div');
    card.className = 'catalog-card';
    
    // קבלת צבע לפי נושא
    const fieldColor = getFieldColor(item.topic || '');
    
    // שליפת שמות מנחים (לא מדריך אחראי!)
    const mentorNames = getMentorNames(item.id);
    
    // המרת ערכי Lookup לתוויות
    const meetingLabel = getLookupLabel(lookupMeetingTypes, item.meetingType);
    const dayLabel = getLookupLabel(lookupWeekDays, item.weekDay);
    
    card.innerHTML = `
        <div class="catalog-card-strip" style="background: ${fieldColor.bg}">
            <span class="strip-label">${item.name || ''}</span>
        </div>
        <div class="catalog-card-body">
            ${mentorNames ? `<div class="catalog-card-guide">
                <span class="guide-icon">👥</span> ${mentorNames}
            </div>` : ''}
            <div class="catalog-card-badges">
                ${badgesHtml}
            </div>
        </div>
        <div class="catalog-card-footer">
            <button class="btn btn-outline btn-sm catalog-view-btn">
                ${t('viewDetails')}
            </button>
            <a href="./registration.html?solution=${item.id}&name=${item.name}" 
               class="btn btn-primary btn-sm">
               ${t('registration')}
            </a>
        </div>`;
    
    // צירוף מאורעות
    card.addEventListener('click', () => openModal(item));
    return card;
}
```

### 5.3 לוגיקת בחירת שפה

**מנגנון דו-לשוני:**

1. **ברירת מחדל:** השפה היא ערבית (`lang = 'ar'`)
2. **כפתור החלפה:** משנה את `lang` בין `'ar'` ל-`'he'`
3. **החלת שפה:**
   - `document.documentElement.lang = lang`
   - `document.documentElement.dir = 'rtl'` (קבוע לשתי השפות)
   - עדכון כל התוויות דרך אובייקט תרגום `T`
   - רנדור מחדש של כל הכרטיסיות

```javascript
// מתוך catalog.js, שורות 112-123
const T = {
    he: { pageTitle: 'מצפן נט - קטלוג השתלמויות', ... },
    ar: { pageTitle: 'كتالوج الحلول التعليمية للعام 2026-2027', ... }
};

function t(key) {
    return (T[lang] && T[lang][key]) || key;
}

function getLookupLabel(lookupList, value) {
    const item = lookupList.find(l => l.value === value);
    if (!item) return value;
    return lang === 'ar' ? (item.labelAr || item.label || item.value) 
                         : (item.label || item.value);
}
```

### 5.4 סינון מנחים והצגת "כוח פנים"

**לוגיקת הצגת מנחים:**

```javascript
// מתוך catalog.js, שורות 138-170
function getMentorNames(solutionId) {
    const links = solutionInstructors.filter(si => si.solutionId === solutionId);
    
    return links.map(link => {
        if (link.mentorId) {
            // מנחה ממאגר mentors
            const mentor = mentorsRepo.find(m => m.id === link.mentorId);
            return mentor ? (lang === 'ar' && mentor.fullNameAr 
                            ? mentor.fullNameAr 
                            : mentor.fullName) : '';
        } else {
            // מנחה ללא רשומה (כוח פנים או שם חופשי)
            const fullName = link.fullName || '';
            if (lang === 'ar' && MENTOR_NAME_TRANSLATIONS[fullName]) {
                return MENTOR_NAME_TRANSLATIONS[fullName]; // תרגום ידני
            }
            return fullName;
        }
    }).filter(Boolean).join(', ');
}

// מילון תרגומים ידני
const MENTOR_NAME_TRANSLATIONS = {
    'אחלאם חגאזי': 'أحلام حجازي',
    'כוח פנים': 'قوى داخلية', // לא מופיע במילון - מוצג כ-is
    // ...
};
```

**הערה:** המילה "כוח פנים" **אינה מתורגמת אוטומטית** אלא אם כן קיימת במילון `MENTOR_NAME_TRANSLATIONS`.

---

## 6. דיאגרמת זרימת מידע (Data Flow Map)

```
┌──────────────────────────────────────────────────────────────────┐
│                        Excel Upload                               │
│                   (template_catalog_import.xlsx)                  │
└─────────────────────┬────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Import Wizard (app.js)                         │
│  1. קריאת קובץ באמצעות XLSX.read()                               │
│  2. המרה ל-JSON באמצעות sheet_to_json()                          │
│  3. הצגת חלונית מיפוי עמודות                                     │
│  4. אימות ערכים מול טבלאות Lookup                                │
│  5. יצירת/עדכון רשומות ב-DataStore                               │
└─────────────────────┬────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                     localStorage (matspanet_*)                    │
│  ┌──────────────┐  ┌──────────────────┐  ┌──────────────┐       │
│  │ solutions    │  │ solution_        │  │ mentors      │       │
│  │              │◄─┤ instructors      │◄─┤              │       │
│  │ (פתרונות)    │  │ (מנחים משויכים)  │  │ (מאגר מנחים) │       │
│  └──────┬───────┘  └──────────────────┘  └──────────────┘       │
│         │                                                        │
│         ▼                                                        │
│  ┌──────────────┐  ┌──────────────────────────────────┐         │
│  │ guides_repo  │  │ lookup_* tables                  │         │
│  │ (מדריכים)    │  │ (domains, education_stages, ...) │         │
│  └──────────────┘  └──────────────────────────────────┘         │
└─────────────────────┬────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                   catalog.js (Public Page)                        │
│  1. טעינת נתונים מ-DataStore                                     │
│  2. סינון לפי תקופה פעילה (periodId)                             │
│  3. בניית כרטיסיות באמצעות createCard()                          │
│  4. החלת שפה (lang = 'ar' / 'he')                                │
│  5. הצגת Modal בפתיחת כרטיסייה                                   │
└─────────────────────┬────────────────────────────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                    catalog.html (UI Rendering)                    │
│  - כרטיסיות עם פסים צבעוניים                                     │
│  - תגים (Badges) לנושא, סוג מפגש, יום, שעות                      │
│  - שמות מנחים (לא מדריך אחראי!)                                  │
│  - כפתורי WhatsApp ורישום מוקדם                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 7. נקודות תורפה ותקלות פוטנציאליות

### 7.1 בעיות מיפוי ונתונים

| # | נקודת תורפה | תיאור | השפעה | המלצה |
|---|-------------|-------|-------|-------|
| 1 | **שדות ריקים ב-solution_instructors** | 90% מהרשומות ריקות (ללא fullName, mentorId, performerType) | מנחים לא מוצגים בכרטיסיות | חובה לבצע אימות קלט בטופס יצירת פתרון |
| 2 | **חוסר עקביות בשמות מנחים** | שמות כתובים בעברית ב-`solution_instructors.fullName` אך אמורים להיות מוצגים בערבית | תצוגה שגויה בשפה הערבית | להוסיף שדה `fullNameAr` ל-`solution_instructors` או לחייב בחירה מ-`mentors` |
| 3 | **ערך "כוח פנים" לא מתורגם** | אין תרגום אוטומטי ל-"قوى داخلية" | מופיע כ-"כוח פנים" בגרסה הערבית | להוסיף ל-`MENTOR_NAME_TRANSLATIONS` או לטפל בלוגיקה |
| 4 | **תאריכים כטקסט חופשי** | שדה `startDate` מכיל טקסט ערבי ("سيتم التحديد...") במקום תאריך | לא ניתן לסנן/למיין לפי תאריך | להפריד לשדה `startDateActual` (תאריך) ו-`startDateNote` (טקסט) |
| 5 | **מערך educationStage כטקסט** | לעיתים מאוחסן כמחרוזת "יסודי, חטיבה" במקום מערך | פונקציית `splitCsvValue()` נדרשת | לאכוף שמירה כמערך בלבד |
| 6 | **חוסר Validation ביצירת פתרון** | ניתן לשמור פתרון ללא מנחים כלל | פתרון מוצג ללא מנחים | להוסיף בדיקת חובה: לפחות מנחה אחד לפני שמירה |
| 7 | **תלות ב-mapping ידני בייבוא** | המשתמש צריך למפות עמודות בכל ייבוא | סיכון לשגיאות אנוש | ליצור תבנית קבועה עם כותרות תואמות בדיוק |

### 7.2 בעיות ביצועים

| # | נקודת תורפה | תיאור | השפעה |
|---|-------------|-------|-------|
| 8 | **סינון In-memory** | כל הסינונים מתבצעים ב-client על כל הנתונים | האטה עם גדילת מספר הרשומות |
| 9 | **טעינת כל הנתונים בהתחלה** | `DataStore.getAll()` טוען הכל לזיכרון | זמן טעינה ראשוני ארוך |
| 10 | **לולאות מקוננות ב-render** | `getMentorNames()` מבצע `filter()` על כל כרטיסייה | O(n*m) כאשר n=כרטיסיות, m=מנחים |

### 7.3 בעיות נגישות ו-i18n

| # | נקודת תורפה | תיאור |
|---|-------------|-------|
| 11 | **חוסר שדות labelAr ב-lookup_tables מסוימים** | לא כל טבלאות ה-Lookup כוללות `labelAr` |
| 12 | **כיווניות מעורבת** | טקסט ערבי עם כיווניות RTL אך שמות עבריים בתוך הטקסט |
| 13 | **תאריכים בפורמט לא אחיד** | DD/MM/YYYY מול MM/DD/YYYY מול טקסט חופשי |

---

## 8. המלצות לשיפור

### 8.1 שינויים במבנה הנתונים

1. **הוספת שדה `fullNameAr` ל-`solution_instructors.json`**
   ```json
   {
     "id": "...",
     "solutionId": "...",
     "mentorId": null,
     "fullNameHe": "כוח פנים",
     "fullNameAr": "قوى داخلية",
     "performerType": "internal"
   }
   ```

2. **הפרדת שדה תאריך לשדה תאריך ושדה הערה**
   ```json
   {
     "startDate": "2026-09-01",
     "startDateNote": "سيتم التحديد مع كلية كاي"
   }
   ```

3. **אילוץ educationStage ו-educationType כמערך תמיד**
   ```javascript
   // ב-saveSolution():
   data.educationStage = Array.isArray(data.educationStage) 
       ? data.educationStage 
       : (data.educationStage || '').split(',').map(s => s.trim());
   ```

### 8.2 שיפורי UX/UI

1. **הוספת אינדיקטור "ללא מנחים"** ברשימת הפתרונות בניהול
2. **הצגת תצוגה מקדימה לפני ייבוא** עם זיהוי שגיאות
3. **הוספת כפתור "ייבוא מנחה ממאגר"** במקום הקלדה ידנית

### 8.3 שיפורי ביצועים

1. **יצירת Index על `solutionId` ב-`solution_instructors`**
   ```javascript
   // במקום filter() בכל פעם:
   const instructorsBySolId = {};
   allInstructors.forEach(i => {
       if (!instructorsBySolId[i.solutionId]) instructorsBySolId[i.solutionId] = [];
       instructorsBySolId[i.solutionId].push(i);
   });
   // גישה מיידית: instructorsBySolId[solutionId]
   ```

2. **Pagination או Virtual Scrolling** עבור קטלוגים גדולים (>100 פתרונות)

---

## 9. נספחים

### 9.1 רשימת שדות מלאה לייצוא Excel

```javascript
var _SOLUTION_EXPORT_HEADERS = [
    'סוג האחריות של פתרון למידה',      // 0
    'שם בית הספר',                     // 1
    'שם פתרון למידה',                  // 2
    'מספר פתרון למידה',                // 3
    'תיאור פתרון למידה',               // 4
    'מדריך אחראי',                     // 5
    'תחום',                           // 6
    'נושא',                           // 7
    'שלב חינוך',                      // 8
    'סוג חינוך',                      // 9
    'תאריך תחילת ההשתלמות',           // 10
    'תאריך סיום ההשתלמות',            // 11
    'יום בשבוע',                      // 12
    'סוג מפגש',                       // 13
    'שעות אקדמיות מוכרות לגמול',     // 14
    'מתוקצב?',                        // 15
    'סה"כ שעות מתוקצבות',             // 16
    'סוג תקצוב',                      // 17
    'סוג המנחה',                      // 18
    'שם המנחה',                       // 19
    'שעות לתקופה ב׳ 09-12',           // 20
    'שעות לתקופה א׳ 01-08',           // 21
    'סה"כ שעות',                      // 22
    'סה"כ שעות מתוקצבות (שעות ליווי)', // 23
    'קישור וואטסאפ',                  // 24
    'קישור רישום מוקדם',              // 25
    'הצג בקטלוג הציבורי',             // 26
    'הערה כללית'                      // 27
];
```

### 9.2 דוגמת רשומה מלאה

```json
{
  "responsibilityType": "פסגה",
  "schoolName": "",
  "name": "نواب المدراء ابتدائي وتربية خاصة",
  "solutionNumber": "",
  "description": "يهدف الاستكمال إلى تعزيز تصور النواب لدورهم الوظيفي والقيادي...",
  "guideId": "ms6fjlun4y7vydkxf",
  "topicType": "בעלי תפקידים",
  "topic": "סגן מנהל",
  "educationStage": ["יסודי", "בתי ספר לחינוך מיוחד"],
  "educationType": ["רגיל", "חינוך מיוחד"],
  "startDate": "سيتم التحديد مع كلية كاي",
  "endDate": "",
  "weekDay": "",
  "meetingType": "היברידי",
  "academicHours": 40,
  "whatsappLink": "https://chat.whatsapp.com/GG2iClu1kxrJZy8ZtbQjfa",
  "earlyRegistrationLink": "",
  "showInCatalog": true,
  "notes": "",
  "budgetType": "מתוקצב",
  "budgetTypeValue": "תקציב רגיל",
  "budgetedHours": 30,
  "status": "בתכנון",
  "createdBy": "usr_admin_001",
  "periodId": "ms4yv1ix1xah39iaf",
  "id": "msa60ti89iwjjqge2",
  "createdAt": "2026-08-01T09:24:53.216Z",
  "updatedAt": "2026-08-01T09:24:53.216Z"
}
```

---

**סוף מסמך אפיון**
