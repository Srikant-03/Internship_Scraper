let allInternships = [];

document.addEventListener("DOMContentLoaded", () => {
    loadData();
    checkScraperStatus();

    // Setup event listeners
    document.getElementById("search-input").addEventListener("input", renderListings);
    document.getElementById("source-filter").addEventListener("change", renderListings);

    // Group filter listeners
    setupFilters("location-filters", "location");
    setupFilters("stipend-filters", "stipend");
    setupFilters("org-filters", "org");
    setupFilters("role-filters", "role");

    // Region tab bar (Everything / India / Global / Remote)
    setupRegionTabs();

    document.getElementById("trigger-scrape-btn").addEventListener("click", triggerScraper);

    // Modal controls
    const modal = document.getElementById("instructions-modal");
    document.getElementById("info-btn").addEventListener("click", () => modal.classList.remove("hidden"));
    document.getElementById("close-modal-btn").addEventListener("click", () => modal.classList.add("hidden"));
    modal.addEventListener("click", (e) => {
        if (e.target === modal) modal.classList.add("hidden");
    });

    // Logs panel controls
    document.getElementById("toggle-logs-btn").addEventListener("click", () => {
        const panel = document.getElementById("logs-panel");
        panel.classList.toggle("hidden");
        if (!panel.classList.contains("hidden")) {
            fetchLogs();
        }
    });

    document.getElementById("close-logs-btn").addEventListener("click", () => {
        document.getElementById("logs-panel").classList.add("hidden");
    });

    // Poll status and logs
    setInterval(() => {
        checkScraperStatus();
        fetchLogs();
    }, 4000);
});

function setupFilters(containerId, filterType) {
    const container = document.getElementById(containerId);
    const buttons = container.querySelectorAll('.filter-btn');

    buttons.forEach(btn => {
        btn.addEventListener('click', (e) => {
            buttons.forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            const val = e.target.dataset.val;
            window[`active${filterType.charAt(0).toUpperCase() + filterType.slice(1)}Filter`] = val;

            // Sync region tab bar when sidebar location changes
            if (filterType === 'location') syncRegionTabs(val);

            renderListings();
        });
    });

    // Default
    window[`active${filterType.charAt(0).toUpperCase() + filterType.slice(1)}Filter`] = "all";
}

function setupRegionTabs() {
    const tabs = document.querySelectorAll('.region-tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const region = tab.dataset.region;
            // Update active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');
            // Sync location filter
            window.activeLocationFilter = region;
            // Sync sidebar buttons
            const sidebarBtns = document.querySelectorAll('#location-filters .filter-btn');
            sidebarBtns.forEach(b => {
                b.classList.toggle('active', b.dataset.val === region);
            });
            renderListings();
        });
    });
}

function syncRegionTabs(val) {
    const tabs = document.querySelectorAll('.region-tab');
    tabs.forEach(t => t.classList.toggle('active', t.dataset.region === val));
}

function updateRegionCounts() {
    const counts = { all: allInternships.length, India: 0, International: 0, Remote: 0 };
    allInternships.forEach(i => {
        if (i.location_type === 'India') counts.India++;
        else if (i.location_type === 'Remote') counts.Remote++;
        else counts.International++;
    });
    const fmt = n => n > 0 ? n.toLocaleString() : '—';
    document.getElementById('tab-count-all').textContent = fmt(counts.all);
    document.getElementById('tab-count-india').textContent = fmt(counts.India);
    document.getElementById('tab-count-global').textContent = fmt(counts.International);
    document.getElementById('tab-count-remote').textContent = fmt(counts.Remote);
}


async function loadData() {
    document.getElementById("loading-spinner").classList.remove("hidden");
    document.getElementById("listings-container").innerHTML = "";

    try {
        const res = await fetch("/api/internships");
        const data = await res.json();
        allInternships = data;

        document.getElementById("total-count").innerText = allInternships.length;

        // Populate sources
        const sources = [...new Set(allInternships.map(i => i.source_platform))];
        const sourceSelect = document.getElementById("source-filter");
        sourceSelect.innerHTML = '<option value="all">All Sources</option>';
        sources.forEach(s => {
            if (s) sourceSelect.innerHTML += `<option value="${s}">${s}</option>`;
        });

        renderListings();
        updateRegionCounts();
    } catch (err) {
        console.error("Failed to load data", err);
    } finally {
        document.getElementById("loading-spinner").classList.add("hidden");
    }
}

function renderListings() {
    const container = document.getElementById("listings-container");
    container.innerHTML = "";

    const searchQ = document.getElementById("search-input").value.toLowerCase();
    const sourceF = document.getElementById("source-filter").value;
    const locF = window.activeLocationFilter || "all";
    const stipF = window.activeStipendFilter || "all";
    const orgF = window.activeOrgFilter || "all";
    const roleF = window.activeRoleFilter || "all";

    let filtered = allInternships.filter(item => {
        // Search
        if (searchQ) {
            const str = `${item.role_title} ${item.company_name} ${item.required_skills}`.toLowerCase();
            if (!str.includes(searchQ)) return false;
        }

        // Source
        if (sourceF !== "all" && item.source_platform !== sourceF) return false;

        // Location
        if (locF !== "all" && item.location_type !== locF) return false;

        // Stipend
        const stipNum = parseFloat(item.stipend_numeric) || 0;
        if (stipF === "paid" && stipNum <= 0 && (!item.stipend || !item.stipend.toLowerCase().includes("month"))) return false;
        if (stipF === "10k" && stipNum < 10000) return false;
        if (stipF === "20k" && stipNum < 20000) return false;
        if (stipF === "50k" && stipNum < 50000) return false;
        if (stipF === "unpaid" && stipNum > 0) return false;

        // Org Type
        if (orgF !== "all" && item.org_type !== orgF) return false;

        // Role Type
        if (roleF !== "all" && item.role_type !== roleF) return false;

        return true;
    });

    // Sort by Match Score Descending, then Date
    filtered.sort((a, b) => {
        const scoreA = a.match_score || 0;
        const scoreB = b.match_score || 0;
        if (scoreB !== scoreA) {
            return scoreB - scoreA;
        }
        return new Date(b.date_scraped) - new Date(a.date_scraped);
    });

    document.getElementById("visible-count").innerText = filtered.length;

    if (filtered.length === 0) {
        container.innerHTML = `<p style="color:var(--text-muted); grid-column: 1/-1; text-align:center; padding: 40px;">No internships found matching your criteria.</p>`;
        return;
    }

    filtered.forEach((item, index) => {
        const isNewHtml = item.is_new ? `<div class="new-badge">New</div>` : '';
        const stipendDisp = item.stipend ? item.stipend : "Unpaid / Not Disclosed";
        const durDisp = item.duration ? item.duration : "N/A";
        const locDisp = item.location ? item.location : item.location_type;
        const skillsDisp = item.required_skills ? item.required_skills : "Not specified";
        const scoreBadge = item.match_score ? `<div class="match-score-badge ${item.match_score >= 80 ? 'high-score' : (item.match_score >= 60 ? 'med-score' : 'low-score')}">${item.match_score}% Match</div>` : '';
        const orgBadge = item.org_type ? `<span class="tag tag-org"><i class="ph ph-bank"></i> ${item.org_type}</span>` : '';
        const roleBadge = item.role_type ? `<span class="tag tag-role"><i class="ph ph-flask"></i> ${item.role_type}</span>` : '';

        const card = document.createElement("div");
        card.className = "card visible";
        card.style.animationDelay = `${index * 0.05}s`;
        card.innerHTML = `
            ${isNewHtml}
            ${scoreBadge}
            <div class="card-header" style="margin-top: ${item.match_score ? '20px' : '0'};">
                <div class="company-name"><i class="ph ph-buildings"></i> ${item.company_name}</div>
            </div>
            <h3 class="role-title">${item.role_title}</h3>
            
            <div class="tags">
                <span class="tag tag-loc"><i class="ph ph-map-pin"></i> ${locDisp}</span>
                <span class="tag tag-stipend"><i class="ph ph-money"></i> ${stipendDisp}</span>
                ${orgBadge}
                ${roleBadge}
            </div>
            
            <div class="skills-list">
                <strong>Skills:</strong> ${skillsDisp}
            </div>
            
            <div class="card-footer">
                <span class="source-info">Via ${item.source_platform} • ${item.date_scraped}</span>
                <a href="${item.apply_link}" target="_blank" class="apply-btn">View Details</a>
            </div>
        `;
        container.appendChild(card);
    });
}

async function triggerScraper() {
    setScrapingState(true);
    try {
        const res = await fetch("/api/scrape", { method: "POST" });
        const data = await res.json();
        setTimeout(checkScraperStatus, 2000);
    } catch (err) {
        console.error("Error triggering scrape", err);
        setScrapingState(false);
    }
}

async function checkScraperStatus() {
    try {
        const res = await fetch("/api/scrape/status");
        const data = await res.json();
        if (data.status === "running") {
            setScrapingState(true);
        } else {
            setScrapingState(false);
        }
    } catch (err) { }
}

let wasRunning = false;
function setScrapingState(isRunning) {
    const btn = document.getElementById("trigger-scrape-btn");
    const txt = document.getElementById("scrape-btn-text");
    const icon = btn.querySelector("i");

    if (isRunning) {
        btn.disabled = true;
        txt.innerText = "Scraping in progress...";
        icon.classList.add("ph-spinner", "ph-spin");
        icon.classList.remove("ph-arrows-clockwise");
        wasRunning = true;
    } else {
        btn.disabled = false;
        txt.innerText = "Run Scraper Now";
        icon.classList.remove("ph-spinner", "ph-spin");
        icon.classList.add("ph-arrows-clockwise");

        // If it just finished, reload data
        if (wasRunning) {
            wasRunning = false;
            loadData();
        }
    }
}

async function fetchLogs() {
    const panel = document.getElementById("logs-panel");
    if (panel && panel.classList.contains("hidden")) return;

    try {
        const res = await fetch("/api/logs");
        const data = await res.json();
        const content = document.getElementById("logs-content");

        const isScrolledToBottom = content.scrollHeight - content.clientHeight <= content.scrollTop + 10;

        content.innerHTML = data.logs.map(l => `<div>${l}</div>`).join("");

        if (isScrolledToBottom) {
            content.scrollTop = content.scrollHeight;
        }
    } catch (e) {
        console.error("Failed to fetch logs", e);
    }
}
