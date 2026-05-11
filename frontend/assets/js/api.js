/**
 * api.js — Barcha API so'rovlar uchun markaziy modul
 * Backend: Django REST Framework (JWT autentifikatsiya)
 */

const API_BASE = 'http://127.0.0.1:8000/api';

// ── TOKEN BOSHQARUVI ────────────────────────────────────

const Auth = {
    getAccess: () => localStorage.getItem('access_token'),
    getRefresh: () => localStorage.getItem('refresh_token'),
    setTokens: (access, refresh) => {
        localStorage.setItem('access_token', access);
        if (refresh) localStorage.setItem('refresh_token', refresh);
    },
    clear: () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
    },
    getUser: () => JSON.parse(localStorage.getItem('user') || 'null'),
    setUser: (user) => localStorage.setItem('user', JSON.stringify(user)),
};

// ── ASOSIY SO'ROV FUNKSIYASI ───────────────────────────

async function apiRequest(endpoint, options) {
    options = options || {};
    const url = API_BASE + endpoint;
    const token = Auth.getAccess();

    const headers = {
        'Content-Type': 'application/json',
    };
    if (token) headers['Authorization'] = 'Bearer ' + token;
    if (options.headers) {
        Object.assign(headers, options.headers);
    }

    // FormData bo'lsa Content-Type o'chiriladi
    if (options.body instanceof FormData) {
        delete headers['Content-Type'];
    }

    let response = await fetch(url, Object.assign({}, options, { headers: headers }));

    // Token muddati o'tgan bo'lsa — yangilash
    if (response.status === 401) {
        const refreshed = await refreshToken();
        if (refreshed) {
            headers['Authorization'] = 'Bearer ' + Auth.getAccess();
            response = await fetch(url, Object.assign({}, options, { headers: headers }));
        } else {
            Auth.clear();
            window.location.href = getBasePath() + 'index.html';
            return null;
        }
    }

    if (response.status === 204) return null;

    if (!response.ok) {
        const err = await response.json().catch(function() { return { detail: 'Server xatosi' }; });
        throw new Error(JSON.stringify(err));
    }

    return response.json();
}

async function refreshToken() {
    const refresh = Auth.getRefresh();
    if (!refresh) return false;

    const res = await fetch(API_BASE + '/auth/refresh/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh: refresh })
    });

    if (res.ok) {
        const data = await res.json();
        Auth.setTokens(data.access, data.refresh);
        return true;
    }
    return false;
}

// Sahifa joylashuviga qarab base path aniqlash
function getBasePath() {
    const path = window.location.pathname;
    if (path.indexOf('/pages/') !== -1) {
        return '../../';
    }
    return '';
}

// ── AUTENTIFIKATSIYA ───────────────────────────────────

const AuthAPI = {
    login: async function(username, password) {
        const data = await apiRequest('/auth/login/', {
            method: 'POST',
            body: JSON.stringify({ username: username, password: password })
        });
        Auth.setTokens(data.access, data.refresh);
        const user = await AuthAPI.getMe();
        Auth.setUser(user);
        return user;
    },

    getMe: function() {
        return apiRequest('/users/me/');
    },

    logout: function() {
        Auth.clear();
        window.location.href = getBasePath() + 'index.html';
    }
};

// ── FOYDALANUVCHILAR API ───────────────────────────────

const UsersAPI = {
    list: function(params) {
        params = params || '';
        return apiRequest('/users/?' + params);
    },
    get: function(id) {
        return apiRequest('/users/' + id + '/');
    },
    create: function(data) {
        return apiRequest('/users/', { method: 'POST', body: JSON.stringify(data) });
    },
    update: function(id, data) {
        return apiRequest('/users/' + id + '/', { method: 'PATCH', body: JSON.stringify(data) });
    },
    delete: function(id) {
        return apiRequest('/users/' + id + '/', { method: 'DELETE' });
    },
    students: function() {
        return apiRequest('/users/students/');
    },
    teachers: function() {
        return apiRequest('/users/teachers/');
    },
    stats: function() {
        return apiRequest('/users/stats/');
    },
};

// ── GURUHLAR API ───────────────────────────────────────

const GroupsAPI = {
    list: function() {
        return apiRequest('/groups/');
    },
    get: function(id) {
        return apiRequest('/groups/' + id + '/');
    },
    create: function(data) {
        return apiRequest('/groups/', { method: 'POST', body: JSON.stringify(data) });
    },
    update: function(id, data) {
        return apiRequest('/groups/' + id + '/', { method: 'PATCH', body: JSON.stringify(data) });
    },
    delete: function(id) {
        return apiRequest('/groups/' + id + '/', { method: 'DELETE' });
    },
    addStudents: function(groupId, studentIds) {
        return apiRequest('/groups/' + groupId + '/add_students/', {
            method: 'POST',
            body: JSON.stringify({ student_ids: studentIds })
        });
    },
    removeStudent: function(groupId, studentId) {
        return apiRequest('/groups/' + groupId + '/remove_student/?student_id=' + studentId, { method: 'DELETE' });
    },
    statistics: function(groupId) {
        return apiRequest('/groups/' + groupId + '/statistics/');
    },
};

// ── KURS / MAVZULAR API ────────────────────────────────

const CoursesAPI = {
    list: function() {
        return apiRequest('/courses/');
    },
    get: function(id) {
        return apiRequest('/courses/' + id + '/');
    },
    create: function(data) {
        return apiRequest('/courses/', { method: 'POST', body: JSON.stringify(data) });
    },
    updateTopic: function(id, data) {
        if (data instanceof FormData) {
            return apiRequest('/courses/' + id + '/', { method: 'PATCH', body: data });
        }
        return apiRequest('/courses/' + id + '/', { method: 'PATCH', body: JSON.stringify(data) });
    },
    markLessonViewed: function(topicId) {
        return apiRequest('/courses/' + topicId + '/mark_lesson_viewed/', { method: 'POST' });
    },
    myProgress: function() {
        return apiRequest('/courses/my_progress/');
    },
};

// ── BAHOLASH API ───────────────────────────────────────

const AssessmentsAPI = {
    assignments: {
        list: function() {
            return apiRequest('/assessments/assignments/');
        },
        get: function(id) {
            return apiRequest('/assessments/assignments/' + id + '/');
        },
        create: function(data) {
            return apiRequest('/assessments/assignments/', { method: 'POST', body: JSON.stringify(data) });
        },
        submissions: function(id) {
            return apiRequest('/assessments/assignments/' + id + '/submissions/');
        },
        submit: function(id, data) {
            if (data.submitted_file) {
                const form = new FormData();
                if (data.text_answer) form.append('text_answer', data.text_answer);
                form.append('submitted_file', data.submitted_file);
                return apiRequest('/assessments/assignments/' + id + '/submit/', {
                    method: 'POST', body: form
                });
            }
            return apiRequest('/assessments/assignments/' + id + '/submit/', {
                method: 'POST',
                body: JSON.stringify({ text_answer: data.text_answer || '' })
            });
        },
        grade: function(submissionId, data) {
            return apiRequest('/assessments/assignments/grade/' + submissionId + '/', {
                method: 'POST', body: JSON.stringify(data)
            });
        },
    },

    tests: {
        list: function() {
            return apiRequest('/assessments/tests/');
        },
        get: function(id) {
            return apiRequest('/assessments/tests/' + id + '/');
        },
        create: function(data) {
            return apiRequest('/assessments/tests/', { method: 'POST', body: JSON.stringify(data) });
        },
        addQuestions: function(testId, questions) {
            return apiRequest('/assessments/tests/' + testId + '/add_questions/', {
                method: 'POST', body: JSON.stringify(questions)
            });
        },
        startAttempt: function(testId) {
            return apiRequest('/assessments/tests/' + testId + '/start_attempt/', { method: 'POST' });
        },
        submitAttempt: function(testId, attemptId, answers) {
            return apiRequest('/assessments/tests/' + testId + '/submit_attempt/', {
                method: 'POST',
                body: JSON.stringify({ attempt_id: attemptId, answers: answers })
            });
        },
    },

    progress: {
        list: function(studentId) {
            const q = studentId ? '?student_id=' + studentId : '';
            return apiRequest('/assessments/progress/' + q);
        },
        summary: function() {
            return apiRequest('/assessments/progress/summary/');
        },
    }
};

// ── YORDAMCHI FUNKSIYALAR ──────────────────────────────

function showError(message, container) {
    let errMsg = message;
    try {
        const parsed = JSON.parse(message);
        errMsg = Object.values(parsed).flat().join(', ');
    } catch(e) {}

    if (container) {
        container.innerHTML = '<div style="background:#fef2f2;border:1px solid #fca5a5;color:#dc2626;padding:12px 16px;border-radius:8px;font-size:13px;">⚠️ ' + errMsg + '</div>';
    } else {
        alert(errMsg);
    }
}

function gradeColor(grade) {
    if (!grade) return 'color:#9ca3af';
    if (grade === 5) return 'color:#059669';
    if (grade === 4) return 'color:#2563eb';
    if (grade === 3) return 'color:#d97706';
    return 'color:#dc2626';
}

function gradeLabel(grade) {
    const labels = { 5: "A'lo", 4: "Yaxshi", 3: "Qoniqarli", 2: "Qoniqarsiz" };
    return labels[grade] || '–';
}

function formatDate(dateStr) {
    if (!dateStr) return '–';
    return new Date(dateStr).toLocaleDateString('uz-UZ', {
        year: 'numeric', month: 'long', day: 'numeric'
    });
}

function formatDateTime(dateStr) {
    if (!dateStr) return '–';
    return new Date(dateStr).toLocaleString('uz-UZ');
}

function requireAuth(allowedRoles) {
    allowedRoles = allowedRoles || [];
    const user = Auth.getUser();
    if (!user) {
        window.location.href = getBasePath() + 'index.html';
        return null;
    }
    if (allowedRoles.length && allowedRoles.indexOf(user.role) === -1) {
        window.location.href = getBasePath() + 'index.html';
        return null;
    }
    return user;
}

// Global eksport
window.API_BASE = API_BASE;
window.Auth = Auth;
window.AuthAPI = AuthAPI;
window.UsersAPI = UsersAPI;
window.GroupsAPI = GroupsAPI;
window.CoursesAPI = CoursesAPI;
window.AssessmentsAPI = AssessmentsAPI;
window.showError = showError;
window.gradeColor = gradeColor;
window.gradeLabel = gradeLabel;
window.formatDate = formatDate;
window.formatDateTime = formatDateTime;
window.requireAuth = requireAuth;
window.getBasePath = getBasePath;