/**
 * components/layout.js
 * Shared sidebar va header komponentlari
 */

// ── SIDEBAR KONFIGURATSIYASI ─────────────────────────────

const SIDEBAR_CONFIG = {
    admin: {
        color: 'purple',
        label: 'Admin Panel',
        icon: '⚙️',
        links: [
            { href: '/pages/admin/dashboard.html',  icon: '📊', label: 'Boshqaruv paneli' },
            { href: '/pages/admin/users.html',       icon: '👥', label: 'Foydalanuvchilar' },
            { href: '/pages/admin/groups.html',      icon: '🏫', label: 'Guruhlar' },
            { href: '/pages/admin/stats.html',       icon: '📈', label: 'Statistika' },
        ]
    },
    teacher: {
        color: 'blue',
        label: "O'qituvchi paneli",
        icon: '👨‍🏫',
        links: [
            { href: '/pages/teacher/dashboard.html',   icon: '📊', label: 'Boshqaruv paneli' },
            { href: '/pages/teacher/topics.html',      icon: '📚', label: 'Mavzular' },
            { href: '/pages/teacher/assignments.html', icon: '📝', label: 'Topshiriqlar' },
            { href: '/pages/teacher/grading.html',     icon: '✅', label: 'Baholash' },
            { href: '/pages/teacher/statistics.html',  icon: '📈', label: 'Statistika' },
        ]
    },
    student: {
        color: 'emerald',
        label: 'Talaba kabineti',
        icon: '🎓',
        links: [
            { href: '/pages/student/dashboard.html',  icon: '📊', label: 'Boshqaruv paneli' },
            { href: '/pages/student/lessons.html',    icon: '📚', label: 'Darslar (M1–M12)' },
            { href: '/pages/student/assignment.html', icon: '📝', label: 'Topshiriqlarim' },
            { href: '/pages/student/grades.html',     icon: '🏆', label: 'Baholarim' },
        ]
    }
};

const COLOR_MAP = {
    purple: { bg: 'bg-purple-600', light: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', active: 'bg-purple-100 text-purple-800' },
    blue:   { bg: 'bg-blue-600',   light: 'bg-blue-50',   text: 'text-blue-700',   border: 'border-blue-200',   active: 'bg-blue-100 text-blue-800'   },
    emerald:{ bg: 'bg-emerald-600',light: 'bg-emerald-50',text: 'text-emerald-700',border: 'border-emerald-200',active: 'bg-emerald-100 text-emerald-800' },
};

/**
 * Sidebar va header'ni sahifaga qo'shish
 * @param {string} containerId - sidebar qo'yiladigan div id
 */
function renderLayout(containerId = 'sidebar') {
    const user = requireAuth();
    if (!user) return;

    const config = SIDEBAR_CONFIG[user.role];
    if (!config) return;

    const c = COLOR_MAP[config.color];
    const currentPath = window.location.pathname;

    // ── SIDEBAR HTML ──
    const sidebarEl = document.getElementById(containerId);
    if (sidebarEl) {
        sidebarEl.innerHTML = `
        <div class="flex flex-col h-full bg-white border-r border-gray-100 shadow-sm" style="width:240px">
            <!-- Logo -->
            <div class="px-5 py-5 border-b border-gray-100">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl ${c.bg} flex items-center justify-center text-white text-lg shadow-sm">
                        ${config.icon}
                    </div>
                    <div>
                        <div class="font-bold text-gray-900 text-sm leading-tight">Urdu Education</div>
                        <div class="text-xs ${c.text} font-medium">${config.label}</div>
                    </div>
                </div>
            </div>

            <!-- Nav links -->
            <nav class="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
                ${config.links.map(link => {
                    const isActive = currentPath.endsWith(link.href.split('/').pop()) ||
                                     currentPath === link.href;
                    return `
                    <a href="${link.href}"
                       class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all
                              ${isActive
                                  ? `${c.active} font-semibold`
                                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                              }">
                        <span class="text-base">${link.icon}</span>
                        <span>${link.label}</span>
                    </a>`;
                }).join('')}
            </nav>

            <!-- User info + logout -->
            <div class="px-4 py-4 border-t border-gray-100">
                <div class="flex items-center gap-3 mb-3">
                    <div class="w-8 h-8 rounded-full ${c.bg} flex items-center justify-center text-white text-sm font-bold">
                        ${(user.full_name || user.username || 'U')[0].toUpperCase()}
                    </div>
                    <div class="flex-1 min-w-0">
                        <div class="text-sm font-semibold text-gray-900 truncate">${user.full_name || user.username}</div>
                        <div class="text-xs text-gray-500">${user.username}</div>
                    </div>
                </div>
                <button onclick="AuthAPI.logout()"
                    class="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-gray-500
                           hover:bg-red-50 hover:text-red-600 transition-colors font-medium">
                    <span>🚪</span> Chiqish
                </button>
            </div>
        </div>`;
    }

    // ── MOBILE HEADER ──
    const headerEl = document.getElementById('mobile-header');
    if (headerEl) {
        headerEl.innerHTML = `
        <div class="flex items-center justify-between px-4 py-3 bg-white border-b border-gray-200 md:hidden sticky top-0 z-50">
            <div class="flex items-center gap-2">
                <div class="w-8 h-8 rounded-lg ${c.bg} flex items-center justify-center text-white">
                    ${config.icon}
                </div>
                <span class="font-bold text-gray-900 text-sm">Urdu Education</span>
            </div>
            <div class="flex items-center gap-1">
                <!-- Mobile Logout Button -->
                <button onclick="AuthAPI.logout()" class="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-red-500 hover:bg-red-50 transition-colors">
                    <span class="text-lg">🚪</span>
                    <span class="text-sm font-semibold hidden sm:inline">Chiqish</span>
                </button>
                <button onclick="toggleMobileSidebar()" class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 hidden">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
                    </svg>
                </button>
            </div>
        </div>`;
    }
}

function toggleMobileSidebar() {
    // Kelajakda mobile sidebar ulash uchun bo'sh joy
    console.log("Mobile sidebar toggled");
}

// ── FOYDALANUVCHI NOMINI SAHIFAGA QO'YISH ──

function renderUserName(elementId = 'user-name') {
    const user = Auth.getUser();
    const el = document.getElementById(elementId);
    if (el && user) {
        el.textContent = user.full_name || user.username;
    }
}

// ── TOAST XABARLARI ──────────────────────────────────────

function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    const colors = {
        success: 'bg-emerald-500',
        error:   'bg-red-500',
        info:    'bg-blue-500',
        warning: 'bg-amber-500',
    };
    toast.className = `fixed top-5 right-5 z-50 ${colors[type]} text-white px-5 py-3 rounded-xl shadow-lg text-sm font-medium
                       transform translate-x-full transition-transform duration-300`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => {
        toast.style.transform = 'translateX(0)';
        setTimeout(() => {
            toast.style.transform = 'translateX(calc(100% + 20px))';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    });
}

// ── MODAL ────────────────────────────────────────────────

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.remove('hidden');
        modal.classList.add('flex');
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.classList.add('hidden');
        modal.classList.remove('flex');
        document.body.style.overflow = '';
    }
}

// Modal overlay click yopish
document.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.closest('[id]')?.classList.add('hidden');
        e.target.closest('[id]')?.classList.remove('flex');
        document.body.style.overflow = '';
    }
});

// ── PROGRESS BAR ─────────────────────────────────────────

function renderProgressBar(percent, color = 'indigo', size = 'md') {
    const heights = { sm: 'h-1.5', md: 'h-2', lg: 'h-3' };
    const colors = {
        indigo:  'bg-indigo-500',
        emerald: 'bg-emerald-500',
        blue:    'bg-blue-500',
        amber:   'bg-amber-500',
        red:     'bg-red-500',
    };
    return `
    <div class="w-full bg-gray-100 rounded-full ${heights[size] || heights.md}">
        <div class="${colors[color] || colors.indigo} ${heights[size] || heights.md} rounded-full transition-all duration-500"
             style="width: ${Math.min(100, Math.max(0, percent))}%">
        </div>
    </div>`;
}

// ── BAHO BADGE ────────────────────────────────────────────

function gradeBadge(grade) {
    if (!grade) return '<span class="text-gray-400 text-sm">–</span>';
    const styles = {
        5: 'bg-emerald-100 text-emerald-700 border-emerald-200',
        4: 'bg-blue-100 text-blue-700 border-blue-200',
        3: 'bg-amber-100 text-amber-700 border-amber-200',
        2: 'bg-red-100 text-red-700 border-red-200',
    };
    const labels = { 5: "A'lo (5)", 4: "Yaxshi (4)", 3: "Qoniqarli (3)", 2: "Qoniqarsiz (2)" };
    return `<span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[grade] || ''}">
        ${labels[grade] || grade}
    </span>`;
}

window.renderLayout = renderLayout;
window.renderUserName = renderUserName;
window.showToast = showToast;
window.openModal = openModal;
window.closeModal = closeModal;
window.renderProgressBar = renderProgressBar;
window.gradeBadge = gradeBadge;
