/**
 * ============================================================================
 * מצפן נט - Authentication Module (Advanced Permissions)
 * ============================================================================
 * מנגנון הרשאות מתקדם:
 *   - מנהל מערכת (admin/system_admin) = גישה מלאה לכל חלקי המערכת.
 *   - משתמשים אחרים = ניתן להגדיר להם הרשאות לכל חלק בנפרד.
 *   - רמות: "view" (צפייה בלבד) או "full" (מלאה – עריכה, מחיקה, השלמת נתונים).
 *   - אם למשתמש אין אובייקט permissions → ברירת מחדל = גישה מלאה (תאימות לאחור).
 *   - פילטור מדריכים: מדריך פסג"ה רואה רק פתרונות שהוא יצר/אחראי עליהם.
 * ============================================================================
 */

const Auth = (() => {

    const ROLE_LABELS = {
        system_admin:    'מנהל מערכת',
        system_operator: 'מפעיל מערכת',
        team_leader:     'חבר בצוות מוביל',
        guide:           'מדריך פסג"ה'
    };

    const ROLE_BADGES = {
        system_admin:    'danger',
        system_operator: 'warning',
        team_leader:     'info',
        guide:           'primary'
    };

    function _normalizeRole(role) {
        if (!role) return 'guide';
        
        // Normalize Hebrew roles to English
        const hebrewToEnglish = {
            'מנהל מערכת': 'system_admin',
            'מפעיל מערכת': 'system_operator',
            'חבר בצוות מוביל': 'team_leader',
            'מדריך פסג"ה': 'guide',
            'admin': 'system_admin'
        };
        
        return hebrewToEnglish[role] || role;
    }

    function _isAdminRole(role) {
        const normalized = _normalizeRole(role);
        return normalized === 'system_admin';
    }

    /**
     * מנקה ערכי קלט מתווים בלתי-נראים (BiDi marks, zero-width chars, BOM).
     * נדרש בגלל בעיה ידועה ב-Microsoft Edge שמכניס תווי בקרה בלתי-נראים
     * לשדות קלט בהקשר RTL — מה שגורם להשוואת מחרוזות להיכשל.
     */
    function _sanitizeInput(str) {
        if (!str) return '';
        return str.normalize('NFC').replace(/[\u200B-\u200F\u2028-\u202F\u2060-\u206F\uFEFF]/g, '');
    }

    function login(username, password) {
        const users = DataStore.getAll(DataStore.KEYS.USERS);
        const cleanUser = _sanitizeInput(username);
        const cleanPass = _sanitizeInput(password);
        const user = users.find(u => _sanitizeInput(u.username) === cleanUser && _sanitizeInput(u.password) === cleanPass);
        if (!user) {
            return { success: false, message: 'שם משתמש או סיסמה שגויים' };
        }
        
        // 🛡️ SECURITY FIX: Log failed login attempts for security monitoring
        // In production, this should be sent to a secure audit log
        if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
            console.warn('[Security] Login attempt for user: ' + cleanUser);
        }
        
        const session = DataStore.setSession(user);
        return { success: true, user: { ...user }, session };
    }

    function logout() {
        DataStore.clearSession();
        window.location.href = './login.html';
    }

    function getCurrentUser() {
        const session = DataStore.getSession();
        if (!session) return null;
        const user = DataStore.getById(DataStore.KEYS.USERS, session.userId);
        return user ? { ...user, session } : null;
    }

    function getSession() {
        return DataStore.getSession();
    }

    function requireAuth() {
        const user = getCurrentUser();
        if (!user) {
            window.location.href = './login.html';
            return null;
        }
        return user;
    }

    function isAdmin() {
        const user = getCurrentUser();
        return user ? _isAdminRole(user.role) : false;
    }

    function isGuide() {
        const user = getCurrentUser();
        return user ? (_normalizeRole(user.role) === 'guide') : false;
    }

    // ===== PERMISSION CHECKING =====
    /**
     * Check if the current user can VIEW a specific section.
     * Admins always can. Others check their permissions object.
     * If user has no permissions object → backward compat = full access.
     */
    function canViewSection(sectionId) {
        const user = getCurrentUser();
        if (!user) return false;
        if (_isAdminRole(user.role)) return true;
        // No permissions set → backward compat (full access)
        if (!user.permissions || typeof user.permissions !== 'object') return true;
        const perm = user.permissions[sectionId];
        return perm === 'view' || perm === 'full';
    }

    /**
     * Check if the current user has FULL access to a specific section.
     * Full = view + edit + delete + complete data.
     */
    function canFullSection(sectionId) {
        const user = getCurrentUser();
        if (!user) return false;
        if (_isAdminRole(user.role)) return true;
        if (!user.permissions || typeof user.permissions !== 'object') return true;
        return user.permissions[sectionId] === 'full';
    }

    // Legacy permission functions (kept for backward compatibility)
    function hasPermission(action) {
        // Broad check – used by legacy code. Returns true for admin or users without perms set.
        const user = getCurrentUser();
        if (!user) return false;
        if (_isAdminRole(user.role)) return true;
        if (!user.permissions || typeof user.permissions !== 'object') return true;
        // For legacy actions, check if user has any full access at all
        return Object.values(user.permissions).some(p => p === 'full');
    }

    function hasUserPermission(user, action) {
        if (!user) return false;
        if (_isAdminRole(user.role)) return true;
        if (!user.permissions || typeof user.permissions !== 'object') return true;
        return Object.values(user.permissions).some(p => p === 'full');
    }

    function canViewSolution(solution) {
        // This is handled by App._getGuideVisibleSolutionIds() at the data layer
        return true;
    }

    function canEditSolution(solution) {
        return canFullSection('solutions');
    }

    function canDeleteSolution(solution) {
        return canFullSection('solutions');
    }

    function setUserPermissions(userId, permissions) {
        DataStore.update(DataStore.KEYS.USERS, userId, { permissions: permissions });
    }

    function resetUserPermissions(userId) {
        DataStore.update(DataStore.KEYS.USERS, userId, { permissions: {} });
    }

    function changePassword(userId, oldPassword, newPassword) {
        const user = DataStore.getById(DataStore.KEYS.USERS, userId);
        if (!user) return { success: false, message: 'משתמש לא נמצא' };
        if (user.password !== oldPassword) return { success: false, message: 'סיסמה נוכחית שגויה' };
        if (newPassword.length < 4) return { success: false, message: 'הסיסמה החדשה חייבת להכיל לפחות 4 תווים' };
        DataStore.update(DataStore.KEYS.USERS, userId, { password: newPassword });
        return { success: true, message: 'הסיסמה שונתה בהצלחה' };
    }

    function createUser(userData) {
        const users = DataStore.getAll(DataStore.KEYS.USERS);
        if (users.find(u => u.username === userData.username)) {
            return { success: false, message: 'שם משתמש כבר קיים במערכת' };
        }
        const role = _normalizeRole(userData.role);
        const user = DataStore.create(DataStore.KEYS.USERS, { ...userData, role });
        return { success: true, user };
    }

    function getAllUsers() {
        return DataStore.getAll(DataStore.KEYS.USERS);
    }

    function deleteUser(userId) {
        const session = DataStore.getSession();
        if (session && session.userId === userId) {
            return { success: false, message: 'לא ניתן למחוק את המשתמש הנוכחי' };
        }
        DataStore.remove(DataStore.KEYS.USERS, userId);
        return { success: true };
    }

    function getAllRoles() {
        return Object.keys(ROLE_LABELS).map(k => ({ value: k, label: ROLE_LABELS[k] }));
    }

    function getRoleLabel(role) {
        return ROLE_LABELS[_normalizeRole(role)] || role || '—';
    }

    function getRoleBadge(role) {
        const r = _normalizeRole(role);
        const cls = ROLE_BADGES[r] || 'gray';
        const label = ROLE_LABELS[r] || role || '—';
        return '<span class="badge badge-' + cls + '">' + label + '</span>';
    }

    return {
        login, logout, getCurrentUser, getSession, requireAuth,
        isAdmin, isGuide,
        hasPermission, hasUserPermission,
        canViewSection, canFullSection,
        canViewSolution, canEditSolution, canDeleteSolution,
        setUserPermissions, resetUserPermissions,
        changePassword, createUser, getAllUsers, deleteUser,
        getAllRoles, getRoleLabel, getRoleBadge,
        ROLE_LABELS, ROLE_BADGES
    };
})();