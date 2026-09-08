document.addEventListener("DOMContentLoaded", () => {
    const searchForm = document.getElementById("search-form");
    const searchInput = document.getElementById("search-query");
    const searchBtn = document.getElementById("search-btn");
    const searchSpinner = document.getElementById("search-spinner");
    const errorAlert = document.getElementById("error-alert");
    
    const answerCard = document.getElementById("answer-card");
    const answerText = document.getElementById("answer-text");
    const queryTypeBadge = document.getElementById("query-type-badge");
    
    const resultsSection = document.getElementById("results-section");
    const resultsList = document.getElementById("results-list");

    const chipBtns = document.querySelectorAll(".chip-btn");

    // Load Stats & Evaluation metrics on startup
    loadStatsAndEvaluation();

    // Attach click listeners to query chips
    chipBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const query = btn.getAttribute("data-query");
            searchInput.value = query;
            performSearch(query);
        });
    });

    // Form submit listener
    searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });

    async function loadStatsAndEvaluation() {
        try {
            const statsRes = await fetch("/api/stats");
            if (statsRes.ok) {
                const stats = await statsRes.json();
                document.getElementById("stat-messages").textContent = stats.total_messages.toLocaleString();
                document.getElementById("stat-participants").textContent = stats.participants_count;
                document.getElementById("stat-daterange").textContent = stats.date_range;

                if (stats.evaluation_summary) {
                    const evalSum = stats.evaluation_summary;
                    document.getElementById("stat-top1").textContent = (evalSum.top1_accuracy * 100).toFixed(1) + "%";
                    document.getElementById("stat-mrr").textContent = evalSum.mrr.toFixed(3);
                    
                    document.getElementById("bm-top1").textContent = (evalSum.top1_accuracy * 100).toFixed(1) + "%";
                    document.getElementById("bm-top3").textContent = (evalSum.top3_accuracy * 100).toFixed(1) + "%";
                    document.getElementById("bm-top5").textContent = (evalSum.top5_accuracy * 100).toFixed(1) + "%";
                    document.getElementById("bm-mrr").textContent = evalSum.mrr.toFixed(4);
                }
            }
        } catch (err) {
            console.warn("Could not fetch stats on init:", err);
        }
    }

    async function performSearch(query) {
        // UI Reset
        hideError();
        setLoading(true);
        answerCard.style.display = "none";
        resultsSection.style.display = "none";
        resultsList.innerHTML = "";

        try {
            const res = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || `Server returned error ${res.status}`);
            }

            const data = await res.json();
            displayResults(data);
        } catch (err) {
            showError(err.message || "An unexpected error occurred while searching.");
        } finally {
            setLoading(false);
        }
    }

    function displayResults(data) {
        // Render Generated Answer Card
        answerText.textContent = data.answer;
        queryTypeBadge.textContent = capitalize(data.query_type);
        
        // Color code query type badge
        if (data.query_type === "attributed") {
            queryTypeBadge.style.background = "linear-gradient(135deg, #059669, #10b981)";
        } else if (data.query_type === "temporal") {
            queryTypeBadge.style.background = "linear-gradient(135deg, #d97706, #f59e0b)";
        } else {
            queryTypeBadge.style.background = "linear-gradient(135deg, #6366f1, #a855f7)";
        }
        
        answerCard.style.display = "block";

        if (!data.results || data.results.length === 0) {
            showError("No matching messages found for your query.");
            return;
        }

        // Render Results List
        data.results.forEach((item, index) => {
            const resultCard = document.createElement("div");
            resultCard.className = "result-card";

            const formattedTime = formatDate(item.timestamp);
            const scorePercent = (item.score * 100).toFixed(1);
            const senderInitial = item.sender ? item.sender.charAt(0).toUpperCase() : "?";

            let contextBeforeHtml = "";
            if (item.context_before && item.context_before.length > 0) {
                contextBeforeHtml = item.context_before.map(m => `
                    <div class="context-msg context-before">
                        <span class="context-sender">${escapeHtml(m.sender)}:</span>
                        <span class="context-text">${escapeHtml(m.message)}</span>
                        <span class="context-time">${formatTimeShort(m.timestamp)}</span>
                    </div>
                `).join("");
            }

            let contextAfterHtml = "";
            if (item.context_after && item.context_after.length > 0) {
                contextAfterHtml = item.context_after.map(m => `
                    <div class="context-msg context-after">
                        <span class="context-sender">${escapeHtml(m.sender)}:</span>
                        <span class="context-text">${escapeHtml(m.message)}</span>
                        <span class="context-time">${formatTimeShort(m.timestamp)}</span>
                    </div>
                `).join("");
            }

            resultCard.innerHTML = `
                <div class="result-main">
                    <div class="msg-header">
                        <div class="sender-info">
                            <div class="avatar">${senderInitial}</div>
                            <div>
                                <div class="sender-name">${escapeHtml(item.sender)}</div>
                                <div class="msg-timestamp">${formattedTime}</div>
                            </div>
                        </div>
                        <div class="score-badge">Similarity: ${scorePercent}%</div>
                    </div>
                    <div>
                        <span class="matched-label">⚡ Match #${index + 1} (Msg ID #${item.message_id})</span>
                        <p class="msg-text">"${escapeHtml(item.message)}"</p>
                    </div>
                </div>

                <button class="context-toggle-btn" onclick="toggleContext(this)">
                    <span>▼ Show Surrounding Conversation (5 Before, 5 After)</span>
                </button>

                <div class="context-container" style="display: none;">
                    <div class="context-section-label" style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Preceding Messages:</div>
                    ${contextBeforeHtml || '<div class="context-msg">No preceding context</div>'}
                    <div style="height: 1px; background: var(--border-color); margin: 0.25rem 0;"></div>
                    <div class="context-section-label" style="font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase;">Succeeding Messages:</div>
                    ${contextAfterHtml || '<div class="context-msg">No succeeding context</div>'}
                </div>
            `;

            resultsList.appendChild(resultCard);
        });

        resultsSection.style.display = "block";
    }

    window.toggleContext = function(btn) {
        const container = btn.nextElementSibling;
        if (container.style.display === "none") {
            container.style.display = "flex";
            btn.querySelector("span").textContent = "▲ Hide Surrounding Conversation";
        } else {
            container.style.display = "none";
            btn.querySelector("span").textContent = "▼ Show Surrounding Conversation (5 Before, 5 After)";
        }
    };

    function setLoading(isLoading) {
        if (isLoading) {
            searchSpinner.style.display = "inline-block";
            searchBtn.disabled = true;
        } else {
            searchSpinner.style.display = "none";
            searchBtn.disabled = false;
        }
    }

    function showError(msg) {
        errorAlert.textContent = msg;
        errorAlert.style.display = "block";
    }

    function hideError() {
        errorAlert.style.display = "none";
        errorAlert.textContent = "";
    }

    function formatDate(isoStr) {
        try {
            const dt = new Date(isoStr);
            return dt.toLocaleString('en-US', {
                month: 'short',
                day: 'numeric',
                year: 'numeric',
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
        } catch {
            return isoStr;
        }
    }

    function formatTimeShort(isoStr) {
        try {
            const dt = new Date(isoStr);
            return dt.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
        } catch {
            return '';
        }
    }

    function capitalize(str) {
        if (!str) return '';
        return str.charAt(0).toUpperCase() + str.slice(1);
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }
});
