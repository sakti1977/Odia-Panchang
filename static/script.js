// Odia Panchang - Frontend JavaScript
// Handles API calls and dynamic content loading

let selectedCity = 'puri'; // Default city

// Load today's Panchang on page load
document.addEventListener('DOMContentLoaded', async () => {
    await loadCities();
    await loadTodayPanchang();
});

// Load available cities
async function loadCities() {
    try {
        const response = await fetch('/api/cities');
        const cities = await response.json();

        const cityGrid = document.getElementById('city-grid');
        cityGrid.innerHTML = '';

        cities.forEach(city => {
            const cityBtn = document.createElement('button');
            cityBtn.className = 'city-btn';
            if (city.key === selectedCity) {
                cityBtn.classList.add('active');
            }

            cityBtn.innerHTML = `
                <span class="city-name-or">${city.name_or}</span>
                <span class="city-name-en">${city.name}</span>
            `;

            cityBtn.onclick = () => selectCity(city.key);
            cityGrid.appendChild(cityBtn);
        });
    } catch (error) {
        console.error('Error loading cities:', error);
    }
}

// Select a city
function selectCity(cityKey) {
    selectedCity = cityKey;

    // Update active button
    document.querySelectorAll('.city-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.closest('.city-btn').classList.add('active');

    // Reload panchang for selected city
    loadTodayPanchang();
}

// Load today's Panchang
async function loadTodayPanchang() {
    const container = document.getElementById('today-panchang');
    container.innerHTML = '<p class="loading">Loading...</p>';

    try {
        const url = selectedCity === 'puri'
            ? '/today?enriched=false'
            : `/api/panchang/today/${selectedCity}`;

        const response = await fetch(url);
        const data = await response.json();

        container.innerHTML = renderPanchang(data);
    } catch (error) {
        console.error('Error loading panchang:', error);
        container.innerHTML = '<p>Error loading Panchang. Please try again.</p>';
    }
}

// Render Panchang data
function renderPanchang(data) {
    let html = `
        <div class="panchang-grid">
            <div class="panchang-item">
                <strong>ତାରିଖ - Date</strong>
                <span class="odia">${formatDate(data.date)}</span>
            </div>
            <div class="panchang-item">
                <strong>ବାର - Day</strong>
                <span class="odia">${data.vara.or}</span>
                <span class="english">${data.vara.en}</span>
            </div>
            <div class="panchang-item">
                <strong>ତିଥି - Tithi</strong>
                <span class="odia">${data.tithi.or}</span>
                <span class="english">${data.tithi.en}</span>
            </div>
            <div class="panchang-item">
                <strong>ନକ୍ଷତ୍ର - Nakshatra</strong>
                <span class="odia">${data.nakshatra.or}</span>
                <span class="english">${data.nakshatra.en}</span>
            </div>
            <div class="panchang-item">
                <strong>ଯୋଗ - Yoga</strong>
                <span class="odia">${data.yoga.or}</span>
                <span class="english">${data.yoga.en}</span>
            </div>
            <div class="panchang-item">
                <strong>ମାସ - Masa</strong>
                <span class="odia">${data.chandra_masa.or}</span>
                <span class="english">${data.chandra_masa.en}</span>
            </div>
            <div class="panchang-item">
                <strong>ପକ୍ଷ - Paksha</strong>
                <span class="odia">${data.paksha.or}</span>
                <span class="english">${data.paksha.en}</span>
            </div>
            <div class="panchang-item">
                <strong>🌅 Sunrise</strong>
                <span class="odia">${data.sunrise || 'N/A'}</span>
            </div>
            <div class="panchang-item">
                <strong>🌇 Sunset</strong>
                <span class="odia">${data.sunset || 'N/A'}</span>
            </div>
        </div>
    `;

    // Add festivals if any
    if (data.festivals && data.festivals.length > 0) {
        html += '<div class="festival-list"><h3>🎉 ପର୍ବ - Festivals</h3>';
        data.festivals.forEach(festival => {
            html += `
                <div class="festival-item">
                    <span class="festival-name">${festival.name.or}</span>
                    <span class="english"> (${festival.name.en})</span>
                    <p>${festival.description}</p>
                </div>
            `;
        });
        html += '</div>';
    }

    return html;
}

// Format date for display
function formatDate(dateStr) {
    const date = new Date(dateStr);
    const options = { year: 'numeric', month: 'long', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
}

// Download monthly Panchang
async function downloadMonthly() {
    try {
        const today = new Date();
        const year = today.getFullYear();
        const month = today.getMonth() + 1;

        const url = `/api/panchang/monthly/${year}/${month}/download?city=${selectedCity}`;
        window.open(url, '_blank');
    } catch (error) {
        console.error('Error downloading monthly panchang:', error);
        alert('Error downloading monthly Panchang. Please try again.');
    }
}

// Show festivals
async function showFestivals() {
    try {
        const today = new Date();
        const year = today.getFullYear();

        const response = await fetch(`/festivals/${year}`);
        const festivals = await response.json();

        // Create modal or navigate to festivals page
        alert(`Found ${festivals.length} festivals this year. Full festival page coming soon!`);
    } catch (error) {
        console.error('Error loading festivals:', error);
    }
}

// Show Muhurta information
async function showMuhurta() {
    try {
        const response = await fetch('/today?enriched=true');
        const data = await response.json();

        if (data.enrichment && data.enrichment.astronomical) {
            const muhurtas = data.enrichment.astronomical.muhurtas;
            let muhurtaText = 'Today\'s Muhurtas:\n\n';

            for (const [key, value] of Object.entries(muhurtas)) {
                muhurtaText += `${key}: ${value}\n`;
            }

            alert(muhurtaText);
        } else {
            alert('Muhurta information not available. Enable AI enrichment for detailed muhurtas.');
        }
    } catch (error) {
        console.error('Error loading muhurta:', error);
        alert('Error loading Muhurta information.');
    }
}

// Service Worker registration for PWA (offline support)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => console.log('SW registered:', registration))
            .catch(error => console.log('SW registration failed:', error));
    });
}
