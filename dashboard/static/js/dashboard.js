// =================== dashboard.js ===================

// 🔍 Détecter le rôle (ici: "directeur")
const role = document.body.dataset.role;

// 📦 Données fictives (aujourd'hui)
async function loadData(role) {
    // 📌 Plus tard: remplacer par un fetch API
    return {
        revenues: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'], data: [35, 38, 42, 39, 45, 48, 52, 49, 47, 51, 54, 58] },
        audience: { labels: ['Al Aoula', 'Arryadia', 'Arrabia', 'Al Maghribia', 'Assadissa', 'Aflam TV'], data: [28.5, 22.3, 18.7, 15.2, 8.9, 6.4] },
        budget: { labels: ['Production', 'Technique', 'RH', 'Marketing', 'Administration', 'Infrastructure'], data: [35, 25, 20, 10, 5, 5] },
        employees: { labels: ['Production', 'Technique', 'Administration', 'Commercial', 'Juridique'], data: [425, 387, 198, 156, 81] },
        regional: { labels: ['Q1', 'Q2', 'Q3', 'Q4'], data: [85, 92, 88, 94] },
        objectives: { labels: ['Audience', 'Budget', 'Innovation', 'Qualité', 'RH', 'Digital'], data: [92, 87, 78, 95, 89, 82], targets: [90, 85, 80, 90, 85, 75] },
        casablancaTrend: { labels: ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun'], data: [15.2, 16.8, 17.3, 18.1, 17.9, 18.7] },
        productions: { labels: ['Informatif', 'Divertissement', 'Sport', 'Culturel', 'Jeunesse', 'Documentaire'], data: [30, 25, 20, 12, 8, 5] }
    };
}

// 🎨 Couleurs et gradients
const colors = {
    primary: '#667eea', success: '#10b981', warning: '#f59e0b',
    danger: '#ef4444', info: '#06b6d4', purple: '#8b5cf6', orange: '#f97316'
};
const gradients = {
    blue: ['#667eea', '#764ba2'], green: ['#10b981', '#059669'],
    orange: ['#f97316', '#ea580c'], purple: ['#8b5cf6', '#7c3aed'], pink: ['#ec4899', '#db2777']
};
function createGradient(ctx, colors) {
    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, colors[0]);
    gradient.addColorStop(1, colors[1]);
    return gradient;
}

// 📊 Créer les graphiques
async function buildCharts() {
    const data = await loadData(role);

    // 1. Revenus mensuels
    new Chart(document.getElementById('revenueChart').getContext('2d'), {
        type: 'line',
        data: { labels: data.revenues.labels, datasets: [{
            label: 'Revenus (Millions DH)', data: data.revenues.data,
            borderColor: colors.primary, backgroundColor: createGradient(document.getElementById('revenueChart').getContext('2d'), gradients.blue),
            borderWidth: 3, fill: true, tension: 0.4,
            pointBackgroundColor: colors.primary, pointBorderColor: '#fff', pointBorderWidth: 2, pointRadius: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    // 2. Audience
    new Chart(document.getElementById('audienceChart').getContext('2d'), {
        type: 'bar',
        data: { labels: data.audience.labels, datasets: [{
            label: "Part d'audience (%)", data: data.audience.data,
            backgroundColor: [colors.primary, colors.success, colors.warning, colors.danger, colors.info, colors.purple],
            borderRadius: 8, borderSkipped: false }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    // 3. Budget
    new Chart(document.getElementById('budgetChart').getContext('2d'), {
        type: 'pie',
        data: { labels: data.budget.labels, datasets: [{ data: data.budget.data, backgroundColor: [colors.primary, colors.success, colors.warning, colors.danger, colors.info, colors.purple], borderWidth: 2, borderColor: '#fff' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#fff', padding: 20 } } } }
    });

    // 4. Employés
    new Chart(document.getElementById('employeesChart').getContext('2d'), {
        type: 'doughnut',
        data: { labels: data.employees.labels, datasets: [{ data: data.employees.data, backgroundColor: [colors.primary, colors.success, colors.warning, colors.danger, colors.info], borderWidth: 3, borderColor: '#fff' }] },
        options: { responsive: true, maintainAspectRatio: false, cutout: '60%', plugins: { legend: { position: 'bottom', labels: { color: '#fff', padding: 15 } } } }
    });

    // 5. Rabat
    new Chart(document.getElementById('rabatChart').getContext('2d'), {
        type: 'bar',
        data: { labels: data.regional.labels, datasets: [{ label: 'Performance (%)', data: data.regional.data, backgroundColor: createGradient(document.getElementById('rabatChart').getContext('2d'), gradients.green), borderRadius: 8 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    // 6. Objectifs vs Réalisations
    new Chart(document.getElementById('objectifsChart').getContext('2d'), {
        type: 'radar',
        data: { labels: data.objectives.labels, datasets: [
            { label: 'Réalisé', data: data.objectives.data, backgroundColor: 'rgba(102,126,234,0.3)', borderColor: colors.primary, borderWidth: 2, pointBackgroundColor: colors.primary, pointBorderColor: '#fff', pointBorderWidth: 2 },
            { label: 'Objectif', data: data.objectives.targets, backgroundColor: 'rgba(16,185,129,0.3)', borderColor: colors.success, borderWidth: 2, pointBackgroundColor: colors.success, pointBorderColor: '#fff', pointBorderWidth: 2 }
        ] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { labels: { color: '#fff' } } } }
    });

    // 7. Casablanca
    new Chart(document.getElementById('casablancaChart').getContext('2d'), {
        type: 'line',
        data: { labels: data.casablancaTrend.labels, datasets: [{
            label: 'Audience (%)', data: data.casablancaTrend.data,
            borderColor: colors.orange, backgroundColor: createGradient(document.getElementById('casablancaChart').getContext('2d'), gradients.orange),
            borderWidth: 3, fill: true, tension: 0.4, pointBackgroundColor: colors.orange, pointBorderColor: '#fff', pointBorderWidth: 2, pointRadius: 6 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
    });

    // 8. Productions
    new Chart(document.getElementById('productionsChart').getContext('2d'), {
        type: 'pie',
        data: { labels: data.productions.labels, datasets: [{ data: data.productions.data, backgroundColor: [colors.primary, colors.success, colors.warning, colors.danger, colors.info, colors.purple], borderWidth: 2, borderColor: '#fff' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom', labels: { color: '#fff', padding: 20 } } } }
    });
}

// ✅ Filtres et dropdowns (copie tout ton code ici, tel quel)
// Ex : addEventListener sur 'dept-dropdown-btn', 'type-dropdown-btn', filterDiagrams()...

// ✅ Lancer au chargement
document.addEventListener('DOMContentLoaded', buildCharts);
// =================== GESTION DES FILTRES ===================

document.getElementById('dept-dropdown-btn').addEventListener('click', function() {
    const menu = document.getElementById('dept-dropdown-menu');
    const arrow = this.querySelector('.dropdown-arrow');
    menu.classList.toggle('show');
    arrow.style.transform = menu.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    document.getElementById('type-dropdown-menu').classList.remove('show');
    document.querySelector('#type-dropdown-btn .dropdown-arrow').style.transform = 'rotate(0deg)';
});

document.getElementById('type-dropdown-btn').addEventListener('click', function() {
    const menu = document.getElementById('type-dropdown-menu');
    const arrow = this.querySelector('.dropdown-arrow');
    menu.classList.toggle('show');
    arrow.style.transform = menu.classList.contains('show') ? 'rotate(180deg)' : 'rotate(0deg)';
    document.getElementById('dept-dropdown-menu').classList.remove('show');
    document.querySelector('#dept-dropdown-btn .dropdown-arrow').style.transform = 'rotate(0deg)';
});

// Fermer quand on clique ailleurs
document.addEventListener('click', function(event) {
    if (!event.target.closest('.dropdown-container')) {
        document.getElementById('dept-dropdown-menu').classList.remove('show');
        document.getElementById('type-dropdown-menu').classList.remove('show');
        document.querySelector('#dept-dropdown-btn .dropdown-arrow').style.transform = 'rotate(0deg)';
        document.querySelector('#type-dropdown-btn .dropdown-arrow').style.transform = 'rotate(0deg)';
    }
});

// Clic sur item département
document.querySelectorAll('#dept-dropdown-menu .dropdown-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('#dept-dropdown-menu .dropdown-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('dept-selected').textContent = this.textContent;
        document.getElementById('dept-dropdown-menu').classList.remove('show');
        document.querySelector('#dept-dropdown-btn .dropdown-arrow').style.transform = 'rotate(0deg)';
        filterDiagrams();
    });
});

// Clic sur item type diagramme
document.querySelectorAll('#type-dropdown-menu .dropdown-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('#type-dropdown-menu .dropdown-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
        document.getElementById('type-selected').textContent = this.textContent;
        document.getElementById('type-dropdown-menu').classList.remove('show');
        document.querySelector('#type-dropdown-btn .dropdown-arrow').style.transform = 'rotate(0deg)';
        filterDiagrams();
    });
});

// Fonction de filtrage
function filterDiagrams() {
    const charts = document.querySelectorAll('.chart-card');
    const activeDeptFilter = document.querySelector('#dept-dropdown-menu .dropdown-item.active').getAttribute('data-filter');
    const activeTypeFilter = document.querySelector('#type-dropdown-menu .dropdown-item.active').getAttribute('data-diagram');

    charts.forEach(chart => {
        const department = chart.getAttribute('data-department');
        const type = chart.getAttribute('data-type');
        let showChart = true;
        if (activeDeptFilter !== 'all' && department !== activeDeptFilter && department !== 'all') showChart = false;
        if (activeTypeFilter !== 'all' && type !== activeTypeFilter) showChart = false;
        if (showChart) {
            chart.style.display = 'block';
            setTimeout(() => {
                chart.style.opacity = '1';
                chart.style.transform = 'scale(1)';
            }, 10);
        } else {
            chart.style.opacity = '0';
            chart.style.transform = 'scale(0.8)';
            setTimeout(() => {
                chart.style.display = 'none';
            }, 300);
        }
    });
}
