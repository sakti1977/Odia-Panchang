// Odia Panchang — Full frontend JavaScript
// Handles all tab navigation, API calls, and dynamic rendering

'use strict';

// ── Constants ──────────────────────────────────────────────────────────────
const DB_START_DATE = '2020-01-01';
const OR_MONTHS = ['ଜାନୁଆରୀ','ଫେବ୍ରୁଆରୀ','ମାର୍ଚ୍ଚ','ଏପ୍ରିଲ','ମଇ','ଜୁନ',
                   'ଜୁଲାଇ','ଅଗଷ୍ଟ','ସେପ୍ଟେମ୍ବର','ଅକ୍ଟୋବର','ନଭେମ୍ବର','ଡିସେମ୍ବର'];

let selectedCity = 'bhubaneswar';
let selectedTradition = 'all';
let userPickedCity = false; // if true, tradition change does not override city
let currentTemple = 'jagannath';
let currentHeritage = 'personalities';
let templeData = null;   // cached
let heritageData = null; // cached
let sankrantiData = null; // cached

const TRADITION_DEFAULT_CITY = {
    all: 'bhubaneswar',
    common: 'bhubaneswar',
    jagannath: 'puri',
    biraja: 'jajpur',
};

const TRADITION_HINTS = {
    all: 'Shows all festivals. Pick a city for local sunrise.',
    common: 'Shared Odia / Hindu observances only.',
    jagannath: 'Jagannath + common festivals. Default city: Puri.',
    biraja: 'Biraja + common festivals. Default city: Jajpur.',
};

const API_BASE = (window.PANCHANG_API_BASE || '').replace(/\/$/, '');
function apiUrl(path) {
    if (!path.startsWith('/')) path = '/' + path;
    return `${API_BASE}${path}`;
}


// ── Initialisation ─────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    initDateInput();
    initFestivalYears();
    loadCities();
    loadTodayPanchang();
});

// ── Tab navigation ─────────────────────────────────────────────────────────
function initTabs() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;
            document.querySelectorAll('.tab-btn').forEach(b => {
                b.classList.remove('active');
                b.setAttribute('aria-selected', 'false');
            });
            document.querySelectorAll('.tab-panel').forEach(p => {
                p.classList.remove('active');
                p.hidden = true;
            });
            btn.classList.add('active');
            btn.setAttribute('aria-selected', 'true');
            const panel = document.getElementById('tab-' + tab);
            panel.classList.add('active');
            panel.hidden = false;

            // Lazy-load tab content on first visit
            if (tab === 'festivals') loadFestivals();
            if (tab === 'muhurta')   loadMuhurta();
            if (tab === 'mandira')   loadMandira();
            if (tab === 'sankranti') loadSankranti();
            if (tab === 'virasat')   loadVirasat();
        });
    });
}

// ── Festival year options ───────────────────────────────────────────────────
function initFestivalYears() {
    const sel = document.getElementById('festival-year');
    if (!sel) return;
    const cur = new Date().getFullYear();
    sel.innerHTML = '';
    for (let y = 2020; y <= cur + 2; y++) {
        const opt = document.createElement('option');
        opt.value = y;
        opt.textContent = y;
        if (y === cur) opt.selected = true;
        sel.appendChild(opt);
    }
}

// ── Date input default ──────────────────────────────────────────────────────
function initDateInput() {
    const today = new Date();
    const y = today.getFullYear();
    const m = String(today.getMonth() + 1).padStart(2, '0');
    const d = String(today.getDate()).padStart(2, '0');
    const el = document.getElementById('lookup-date');
    if (el) {
        el.value = `${y}-${m}-${d}`;
        el.max = `${y + 1}-12-31`;
        el.min = DB_START_DATE;
    }
    // Set festival year default
    const fy = document.getElementById('festival-year');
    if (fy) fy.value = String(y);
}

// ── City selector ───────────────────────────────────────────────────────────
async function loadCities() {
    try {
        // First, try to detect user's city from IP
        try {
            const detectResp = await fetch(apiUrl('/api/detect-city'));
            if (detectResp.ok) {
                const detectData = await detectResp.json();
                if (detectData.detected_city) {
                    selectedCity = detectData.detected_city;
                }
            }
        } catch (e) {
            console.log('City detection not available, using default');
        }

        const resp = await fetch(apiUrl('/api/cities'));
        const cities = await resp.json();
        const grid = document.getElementById('city-grid');
        grid.innerHTML = '';
        // Prefer Odisha cities first in the grid (region flag or known keys)
        const odishaKeys = new Set(['bhubaneswar','puri','jajpur','cuttack','berhampur','sambalpur','rourkela','balasore','konark','baripada','bhadrak']);
        cities.sort((a, b) => {
            const ao = odishaKeys.has(a.key) ? 0 : 1;
            const bo = odishaKeys.has(b.key) ? 0 : 1;
            if (ao !== bo) return ao - bo;
            return a.name.localeCompare(b.name);
        });
        cities.forEach(city => {
            const btn = document.createElement('button');
            btn.className = 'city-btn' + (city.key === selectedCity ? ' active' : '');
            btn.dataset.cityKey = city.key;
            btn.innerHTML = `<span class="city-name-or">${city.name_or}</span>
                             <span class="city-name-en">${city.name}</span>`;
            btn.onclick = () => selectCity(city.key, city.name_or, btn);
            grid.appendChild(btn);
        });

        // Update the badge with detected city
        const detectedCityInfo = cities.find(c => c.key === selectedCity);
        if (detectedCityInfo) {
            const badge = document.getElementById('today-city-badge');
            if (badge) badge.textContent = detectedCityInfo.name_or;
        }
    } catch (e) {
        console.error('Cities load error:', e);
    }
}

function selectCity(cityKey, nameOr, btn) {
    selectedCity = cityKey;
    userPickedCity = true;
    document.querySelectorAll('.city-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    const badge = document.getElementById('today-city-badge');
    if (badge) badge.textContent = nameOr || cityKey;
    loadTodayPanchang();
}

function selectTradition(tradition, btn) {
    selectedTradition = tradition || 'all';
    document.querySelectorAll('.tradition-btn').forEach(b => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    const hint = document.getElementById('tradition-hint');
    if (hint) hint.textContent = TRADITION_HINTS[selectedTradition] || '';

    // Apply tradition default city unless user already chose a city
    if (!userPickedCity) {
        const def = TRADITION_DEFAULT_CITY[selectedTradition] || 'bhubaneswar';
        selectedCity = def;
        const cityBtn = document.querySelector(`.city-btn`);
        // re-mark active city button if present
        document.querySelectorAll('.city-btn').forEach(b => {
            const key = b.dataset.cityKey;
            b.classList.toggle('active', key === selectedCity);
            if (key === selectedCity) {
                const badge = document.getElementById('today-city-badge');
                const or = b.querySelector('.city-name-or');
                if (badge && or) badge.textContent = or.textContent;
            }
        });
    }
    loadTodayPanchang();
}

// ── Today's Panchang ────────────────────────────────────────────────────────
async function loadTodayPanchang() {
    const el = document.getElementById('today-panchang');
    el.innerHTML = spinner();
    try {
        const q = new URLSearchParams({ tradition: selectedTradition });
        const url = `/api/panchang/today/${selectedCity}?${q}`;
        const resp = await fetch(apiUrl(url));
        if (!resp.ok) throw new Error(resp.statusText);
        const data = await resp.json();
        el.innerHTML = renderPanchang(data);
    } catch (e) {
        el.innerHTML = errorBox('Could not load today\'s Panchang. Please try again.');
    }
}

// ── Panchang rendering ──────────────────────────────────────────────────────
function renderPanchang(data) {
    const d = new Date(data.date + 'T00:00:00');
    const dateOr = `${d.getDate()} ${OR_MONTHS[d.getMonth()]} ${d.getFullYear()}`;
    const dateEn = d.toLocaleDateString('en-IN', { year:'numeric', month:'long', day:'numeric' });

    const items = [
        { label: 'ବାର · Vara',              or: data.vara?.or,         en: data.vara?.en },
        { label: 'ସୌର ମାସ · Soura Masa',    or: data.soura_masa?.or,   en: data.soura_masa?.en },
        { label: 'ଚାନ୍ଦ୍ର ମାସ · Chandra',  or: data.chandra_masa?.or, en: data.chandra_masa?.en },
        { label: 'ପକ୍ଷ · Paksha',           or: data.paksha?.or,       en: data.paksha?.en },
        { label: 'ତିଥି · Tithi',            or: data.tithi?.or,        en: `${data.tithi?.en} (${data.tithi?.num})` },
        { label: 'ନକ୍ଷତ୍ର · Nakshatra',     or: data.nakshatra?.or,    en: data.nakshatra?.en },
        { label: 'ଯୋଗ · Yoga',              or: data.yoga?.or,         en: data.yoga?.en },
        { label: 'କରଣ · Karana',            or: data.karana?.or,       en: data.karana?.en },
        { label: '🌅 ସୂର୍ଯ୍ୟୋଦୟ · Sunrise', or: data.sunrise || '—',   en: '' },
        { label: '🌇 ସୂର୍ଯ୍ୟାସ୍ତ · Sunset',  or: data.sunset  || '—',   en: '' },
    ];

    let html = `
        <div class="panchang-date-hero">
            <div class="date-or">${dateOr}</div>
            <div class="date-en">${dateEn}</div>
            <div class="vara-or">${data.vara?.or || ''}</div>
        </div>
        <div class="panchang-grid">
            ${items.map(i => `
            <div class="panchang-item">
                <span class="label">${i.label}</span>
                <span class="value-or">${i.or || '—'}</span>
                ${i.en ? `<span class="value-en">${i.en}</span>` : ''}
            </div>`).join('')}
        </div>`;

    if (data.meta) {
        html += `<div class="meta-strip">
            <span class="meta-pill">${esc(data.meta.city || '')}</span>
            <span class="meta-pill">${esc(data.meta.tradition || '')}</span>
            <span class="meta-pill muted">${esc(data.meta.masa_system || '')}</span>
        </div>`;
    }

    if (data.festivals?.length) {
        html += `<div class="festival-strip">
            <h4>🎉 ପର୍ବ · Festivals &amp; Stories</h4>
            ${data.festivals.map(f => renderFestivalStoryBlock(f, 'strip')).join('')}
        </div>`;
    } else if (data.festivals) {
        html += `<div class="festival-strip"><p class="fest-desc">No festivals for this tradition filter.</p></div>`;
    }

    return html;
}

/** Escape text for HTML text nodes */
function esc(s) {
    if (s == null || s === '') return '';
    return String(s)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
}

/**
 * Inner story + why_today HTML (used inside collapsible).
 */
function renderStoryWhyInner(f) {
    const storyOr = f.story?.or || '';
    const storyEn = f.story?.en || '';
    const whyOr = f.why_today?.or || '';
    const whyEn = f.why_today?.en || '';

    const storyBody = (storyOr || storyEn)
        ? `<div class="fest-story">
             <div class="fest-story-label">📖 କାହାଣୀ · Story</div>
             ${storyOr ? `<p class="fest-story-or">${esc(storyOr)}</p>` : ''}
             ${storyEn ? `<p class="fest-story-en">${esc(storyEn)}</p>` : ''}
           </div>`
        : '';
    const whyBody = (whyOr || whyEn)
        ? `<div class="fest-why">
             <div class="fest-story-label">✨ ଆଜି କାହିଁକି · Why today</div>
             ${whyOr ? `<p class="fest-story-or">${esc(whyOr)}</p>` : ''}
             ${whyEn && whyEn !== whyOr ? `<p class="fest-story-en">${esc(whyEn)}</p>` : ''}
           </div>`
        : '';
    return { storyBody, whyBody, hasContent: !!(storyBody || whyBody) };
}

/**
 * Collapsible wrapper — collapsed by default (mobile-friendly).
 * Uses <details>/<summary> for accessibility without extra JS.
 */
function renderStoryCollapse(f, opts = {}) {
    const { storyBody, whyBody, hasContent } = renderStoryWhyInner(f);
    if (!hasContent) return '';

    const openAttr = opts.open ? ' open' : '';
    return `
      <details class="fest-story-details"${openAttr}>
        <summary class="fest-story-summary">
          <span class="fest-summary-label">
            <span class="fest-summary-icon" aria-hidden="true">📖</span>
            <span class="fest-summary-text-or">କାହାଣୀ ପଢ଼ନ୍ତୁ</span>
            <span class="fest-summary-text-en">Read story</span>
          </span>
          <span class="fest-summary-hint" aria-hidden="true"></span>
        </summary>
        <div class="fest-story-panel">
          ${storyBody}
          ${whyBody}
        </div>
      </details>`;
}

/**
 * Festival card with story + why_today.
 * mode: 'strip' (today/lookup) | 'list' (festivals tab)
 */
function renderFestivalStoryBlock(f, mode) {
    const kind = f.story_kind || '';
    const kindLabel = {
        puranic_tradition: 'Traditional lore',
        historical_cultural: 'Cultural history',
        ritual_observance: 'Ritual observance',
    }[kind] || kind;

    const collapse = renderStoryCollapse(f, { open: false });

    if (mode === 'strip') {
        return `
        <div class="festival-strip-item has-story">
            <div class="fest-title-row">
                <span class="fest-or">${esc(f.name?.or || '')}</span>
                <span class="fest-en">${esc(f.name?.en || '')}</span>
                ${kindLabel ? `<span class="fest-kind-pill">${esc(kindLabel)}</span>` : ''}
            </div>
            ${f.description ? `<span class="fest-desc">${esc(f.description)}</span>` : ''}
            ${collapse}
        </div>`;
    }

    return { collapse, kindLabel };
}

// ── Date lookup ─────────────────────────────────────────────────────────────
async function lookupDate() {
    const dateVal = document.getElementById('lookup-date').value;
    if (!dateVal) return;
    const el = document.getElementById('lookup-result');
    el.innerHTML = `<div class="card" style="margin-top:12px;">${spinner()}</div>`;
    try {
        const q = new URLSearchParams({
            tradition: selectedTradition,
            city: selectedCity,
        });
        const resp = await fetch(apiUrl(`/panchang/${dateVal}?${q}`));
        if (!resp.ok) throw new Error(`${resp.status}: ${await resp.text()}`);
        const data = await resp.json();
        el.innerHTML = `<div class="card" style="margin-top:12px;">${renderPanchang(data)}</div>`;
    } catch (e) {
        el.innerHTML = `<div style="margin-top:12px;">${errorBox('No data for this date. ' + e.message)}</div>`;
    }
}

// ── Festivals tab ───────────────────────────────────────────────────────────
async function loadFestivals() {
    const el = document.getElementById('festivals-result');
    el.removeAttribute('data-loaded');
    el.innerHTML = spinner();
    const year = document.getElementById('festival-year')?.value || new Date().getFullYear();
    const tradition = document.getElementById('festival-tradition')?.value || 'all';
    try {
        const url = tradition === 'all'
            ? `/festivals/${year}`
            : `/festivals/${year}?tradition=${tradition}`;
        const resp = await fetch(apiUrl(url));
        if (!resp.ok) throw new Error(resp.statusText);
        const festivals = await resp.json();
        el.innerHTML = renderFestivalList(festivals);
        el.dataset.loaded = '1';
    } catch (e) {
        el.innerHTML = errorBox('Could not load festivals. ' + e.message);
    }
}

function renderFestivalList(festivals) {
    if (!festivals.length) return infoBox('No festivals found for the selected year/tradition.');

    // Group by month
    const byMonth = {};
    festivals.forEach(f => {
        const d = new Date(f.date + 'T00:00:00');
        const key = d.toLocaleDateString('en-IN', { month: 'long', year: 'numeric' });
        if (!byMonth[key]) byMonth[key] = [];
        byMonth[key].push(f);
    });

    const tradBadge = { jagannath: 'badge-jagannath', biraja: 'badge-biraja', common: 'badge-common', lingaraj: 'badge-jagannath' };
    const tradLabel = { jagannath: 'Jagannath', biraja: 'Biraja', common: 'Common', lingaraj: 'Lingaraj' };

    return Object.entries(byMonth).map(([month, fests]) => `
        <div class="festival-month-group">
            <div class="festival-month-heading">${month}</div>
            ${fests.map(f => {
                const d = new Date(f.date + 'T00:00:00');
                const wd = d.toLocaleDateString('en-IN', { weekday: 'short' });
                const mn = d.toLocaleDateString('en-IN', { month: 'short' });
                const badge = tradBadge[f.tradition] || 'badge-common';
                const label = tradLabel[f.tradition] || f.tradition;
                const storyParts = renderFestivalStoryBlock(f, 'list');
                return `
                <div class="festival-card has-story">
                    <div class="festival-date-col">
                        <div class="festival-date-day">${d.getDate()}</div>
                        <div class="festival-date-mon">${mn}</div>
                        <div class="festival-date-weekday">${wd}</div>
                    </div>
                    <div class="festival-info-col">
                        <div class="festival-name-or">${esc(f.name?.or || '')}</div>
                        <div class="festival-name-en">${esc(f.name?.en || '')}</div>
                        <span class="festival-tradition-badge ${badge}">${esc(label)}</span>
                        ${storyParts.kindLabel ? `<span class="fest-kind-pill">${esc(storyParts.kindLabel)}</span>` : ''}
                        ${f.description ? `<div class="festival-desc">${esc(f.description)}</div>` : ''}
                        ${storyParts.collapse || ''}
                    </div>
                </div>`;
            }).join('')}
        </div>
    `).join('');
}

// ── Muhurta tab ─────────────────────────────────────────────────────────────
async function loadMuhurta() {
    const el = document.getElementById('muhurta-result');
    if (el.dataset.loaded) return;
    el.innerHTML = spinner();
    try {
        const resp = await fetch(apiUrl('/today?enriched=true'));
        if (!resp.ok) throw new Error(resp.statusText);
        const data = await resp.json();
        el.innerHTML = renderMuhurta(data);
        el.dataset.loaded = '1';
    } catch (e) {
        el.innerHTML = errorBox('Could not load Muhurta information. ' + e.message);
    }
}

function renderMuhurta(data) {
    const astro = data.enrichment?.astronomical || {};
    const muhurtas = astro.muhurtas || {};
    const specialDay = astro.special_day_type || '';
    const yogas = astro.special_yogas || [];

    const muhurtaIcons = {
        brahma_muhurta:   { icon: '🌙', name: 'Brahma Muhurta', name_or: 'ବ୍ରାହ୍ମ ମୁହୂର୍ତ୍ତ', type: 'auspicious' },
        abhijit_muhurta:  { icon: '✨', name: 'Abhijit Muhurta', name_or: 'ଅଭିଜିତ ମୁହୂର୍ତ୍ତ', type: 'auspicious' },
        rahu_kalam:       { icon: '⚠️', name: 'Rahu Kalam', name_or: 'ରାହୁ କାଳ', type: 'inauspicious' },
        gulika_kalam:     { icon: '🔴', name: 'Gulika Kalam', name_or: 'ଗୁଳିକ କାଳ', type: 'inauspicious' },
        yamaganda_kalam:  { icon: '🔶', name: 'Yamaganda', name_or: 'ଯମଗଣ୍ଡ', type: 'inauspicious' },
        dur_muhurta:      { icon: '❌', name: 'Dur Muhurta', name_or: 'ଦୁଃ ମୁହୂର୍ତ୍ତ', type: 'inauspicious' },
        amrit_kalam:      { icon: '💧', name: 'Amrit Kalam', name_or: 'ଅମୃତ କାଳ', type: 'auspicious' },
        varjyam:          { icon: '🚫', name: 'Varjyam', name_or: 'ବର୍ଜ୍ୟ', type: 'inauspicious' },
    };

    let html = '';

    if (specialDay && specialDay !== 'normal') {
        const emojiMap = { ekadashi: '🌙', purnima: '🌕', amavasya: '🌑', pradosha: '🕉️', chaturthi: '🐘' };
        html += `<div class="special-day-banner">${emojiMap[specialDay] || '⭐'} Special Day: <strong>${specialDay.charAt(0).toUpperCase() + specialDay.slice(1)}</strong></div>`;
    }
    if (yogas?.length) {
        html += `<div class="yoga-banner">✅ Special Yogas today: <strong>${yogas.join(', ')}</strong></div>`;
    }

    const entries = Object.entries(muhurtas);
    if (!entries.length) {
        html += infoBox('Muhurta data requires AI enrichment (GROQ_API_KEY). '
                      + 'Basic Panchang is always available.');
    } else {
        html += '<div class="muhurta-grid">';
        entries.forEach(([key, val]) => {
            const info = muhurtaIcons[key] || { icon: '🕐', name: key, name_or: key, type: 'neutral' };
            html += `
            <div class="muhurta-card muhurta-${info.type}">
                <div class="muhurta-icon">${info.icon}</div>
                <div class="muhurta-name-or">${info.name_or}</div>
                <div class="muhurta-name">${info.name}</div>
                <div class="muhurta-time">${val}</div>
            </div>`;
        });
        html += '</div>';
    }

    return html;
}

// ── Sankranti tab ───────────────────────────────────────────────────────────
async function loadSankranti() {
    const el = document.getElementById('sankranti-result');
    if (el.dataset.loaded) return;
    el.innerHTML = spinner();
    try {
        if (!sankrantiData) {
            const resp = await fetch(apiUrl('/api/sankrantis'));
            if (!resp.ok) throw new Error(resp.statusText);
            sankrantiData = await resp.json();
        }
        el.innerHTML = renderSankrantis(sankrantiData.sankrantis);
        el.dataset.loaded = '1';
    } catch (e) {
        el.innerHTML = errorBox('Could not load Sankranti information. ' + e.message);
    }
}

function renderSankrantis(list) {
    return `<div class="sankranti-grid">
        ${list.map(s => `
        <div class="sankranti-card sig-${s.significance}">
            <span class="sankranti-importance imp-${s.significance}">${
                s.significance === 'most_important' ? '★ Most Important' :
                s.significance === 'important' ? '● Important' : '○ Observed'
            }</span>
            <div class="sankranti-masa-or">${s.soura_masa_or}</div>
            <div class="sankranti-name-or">${s.name_or}</div>
            <div class="sankranti-name-en">${s.name_en}</div>
            <span class="sankranti-date">☀️ Approx: ${s.approx_date}</span>
            <div class="sankranti-desc">${s.description}</div>
            ${s.customs?.length ? `
            <ul class="sankranti-customs">
                ${s.customs.map(c => `<li>${c}</li>`).join('')}
            </ul>` : ''}
        </div>`).join('')}
    </div>`;
}

// ── Mandira (Temple) tab ────────────────────────────────────────────────────
async function loadMandira() {
    const el = document.getElementById('mandira-result');
    if (!templeData) {
        el.innerHTML = spinner();
        try {
            const [nitisResp, specialsResp, beshasResp] = await Promise.all([
                fetch(apiUrl('/api/temple-nitis')),
                fetch(apiUrl('/api/temple-specials')),
                fetch(apiUrl('/api/beshas')),
            ]);
            if (!nitisResp.ok) throw new Error('temple-nitis: ' + nitisResp.statusText);
            templeData = {
                nitis:    await nitisResp.json(),
                specials: await specialsResp.json(),
                beshas:   (await beshasResp.json()).beshas,
            };
        } catch (e) {
            el.innerHTML = errorBox('Could not load temple data. ' + e.message);
            return;
        }
    }
    renderTemplePanel(currentTemple);

    // Wire up temple sub-tabs
    document.querySelectorAll('.temple-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.temple-tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentTemple = btn.dataset.temple;
            renderTemplePanel(currentTemple);
        });
    });
}

function renderTemplePanel(temple) {
    const el = document.getElementById('mandira-result');
    const t = templeData.nitis[temple];
    const specials = temple === 'jagannath' ? templeData.specials.jagannath_beshas
                   : temple === 'biraja'    ? templeData.specials.biraja_specials
                                            : templeData.specials.lingaraj_specials;
    const specialsTitle = temple === 'jagannath' ? '🌟 ବିଶେଷ ବେଶ · Annual Beshas'
                        : '🌟 ବିଶେଷ ଅନୁଷ୍ଠାନ · Special Occasions';

    el.innerHTML = `
        <div class="temple-header">
            <div class="temple-name-or">${t.temple_or}</div>
            <div class="temple-name">${t.temple} · <span class="temple-location">${t.location}</span></div>
            <div class="temple-desc">${t.description}</div>
        </div>

        <h3 style="color:var(--primary);margin-bottom:12px;">⏰ ଦୈନିକ ନୀତି · Daily Rituals</h3>
        <div class="niti-timeline">
            ${t.nitis.map(n => `
            <div class="niti-item">
                <div class="niti-time">${n.time}</div>
                <div class="niti-name-or">${n.name_or}</div>
                <div class="niti-name-en">${n.name_en}</div>
                <div class="niti-desc">${n.description}</div>
            </div>`).join('')}
        </div>

        <h3 style="color:var(--primary);margin:20px 0 12px;">${specialsTitle}</h3>
        ${temple === 'jagannath'
            ? `<div class="besha-grid">${specials.map(b => `
              <div class="besha-card">
                  <div class="besha-name-or">${b.name_or}</div>
                  <div class="besha-name-en">${b.name_en}</div>
                  <span class="besha-trigger">🗓️ ${b.trigger}</span>
                  <div class="besha-desc">${b.description}</div>
              </div>`).join('')}</div>`
            : `<div class="special-occasions-grid">${specials.map(s => `
              <div class="special-card">
                  <div class="special-name-or">${s.name_or}</div>
                  <div class="special-name-en">${s.name_en}</div>
                  <span class="special-time">🗓️ ${s.time}</span>
                  <div class="special-desc">${s.description}</div>
              </div>`).join('')}</div>`
        }
    `;
}

// ── Virasat (Heritage) tab ──────────────────────────────────────────────────
async function loadVirasat() {
    const el = document.getElementById('virasat-result');
    if (!heritageData) {
        el.innerHTML = spinner();
        try {
            const resp = await fetch(apiUrl('/api/heritage'));
            if (!resp.ok) throw new Error(resp.statusText);
            heritageData = await resp.json();
        } catch (e) {
            el.innerHTML = errorBox('Could not load heritage data. ' + e.message);
            return;
        }
    }
    renderHeritagePanel(currentHeritage);

    document.querySelectorAll('.heritage-tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.heritage-tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentHeritage = btn.dataset.heritage;
            renderHeritagePanel(currentHeritage);
        });
    });
}

function renderHeritagePanel(type) {
    const el = document.getElementById('virasat-result');
    if (type === 'personalities') {
        el.innerHTML = `
            <div class="personality-grid">
                ${heritageData.personalities.map(p => `
                <div class="personality-card">
                    <div class="personality-name">${p.name}</div>
                    <div class="personality-name-or">${p.name_or}</div>
                    <div class="personality-period">📅 ${p.period}</div>
                    <span class="personality-category">${p.category}</span>
                    <div class="personality-sig">${p.significance}</div>
                </div>`).join('')}
            </div>`;
    } else {
        el.innerHTML = `
            <div class="history-timeline">
                ${heritageData.history.map(h => `
                <div class="history-item">
                    <div class="history-period">${h.period}</div>
                    <div class="history-event-or">${h.event_or}</div>
                    <div class="history-event-en">${h.event_en}</div>
                    <div class="history-desc">${h.description}</div>
                </div>`).join('')}
            </div>`;
    }
}

// ── Monthly download ────────────────────────────────────────────────────────
function downloadMonthly() {
    const today = new Date();
    const url = `/api/panchang/monthly/${today.getFullYear()}/${today.getMonth() + 1}/download?city=${selectedCity}`;
    window.open(url, '_blank');
}

// ── Helpers ─────────────────────────────────────────────────────────────────
function spinner() {
    return '<div class="loading-spinner"><div class="spinner"></div><p>Loading…</p></div>';
}
function errorBox(msg) {
    return `<div class="error-box">⚠️ ${msg}</div>`;
}
function infoBox(msg) {
    return `<div class="info-box">ℹ️ ${msg}</div>`;
}

// ── Service Worker ──────────────────────────────────────────────────────────
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(r => console.log('[SW] registered:', r.scope))
            .catch(e => console.warn('[SW] registration failed:', e));
    });
}
