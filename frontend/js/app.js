/**
 * CrisisShield AI — Main Application
 */

(function () {
    'use strict';

    const POLL_INTERVAL = 5000; // 5 seconds
    let chart = null;
    let pollTimer = null;

    // --- Clock ---
    function updateClock() {
        const el = document.getElementById('navClock');
        if (el) {
            const now = new Date();
            el.textContent = now.toLocaleString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
            });
        }
    }

    // --- Data Polling ---
    async function fetchAllData() {
        try {
            // Fetch all endpoints in parallel
            const [overview, agents, riskZones, alerts, rescueUnits, inventory, allocations, signals] = await Promise.all([
                api.getOverview(),
                api.getAgentStatuses(),
                api.getRiskZones(),
                api.getAlerts(),
                api.getRescueUnits(),
                api.getResourceInventory(),
                api.getResourceAllocations(),
                api.getSignals(),
            ]);

            // Update all panels
            Dashboard.updateOverview(overview);
            Dashboard.updateAgents(agents);
            Dashboard.updateRiskZones(riskZones);
            Dashboard.updateAlerts(alerts);
            Dashboard.updateRescueUnits(rescueUnits);
            Dashboard.updateResources(inventory, allocations);
            Dashboard.updateSignals(signals);

            // Update chart
            if (chart && signals && signals.signals) {
                chart.addDataPoint(signals.signals);
            }

            // Update system status
            updateSystemStatus(overview);
        } catch (error) {
            console.error('[App] Data fetch error:', error);
        }
    }

    function updateSystemStatus(overview) {
        const statusEl = document.getElementById('systemStatus');
        if (!statusEl || !overview) return;

        const dot = statusEl.querySelector('.status-dot');
        const text = statusEl.querySelector('.status-text');

        if (overview.agents_active >= 4) {
            dot.className = 'status-dot pulse';
            text.textContent = 'System Active';
            statusEl.style.borderColor = 'rgba(34, 197, 94, 0.3)';
            statusEl.style.background = 'rgba(34, 197, 94, 0.1)';
            text.style.color = 'var(--accent-green)';
            dot.style.background = 'var(--accent-green)';
        } else if (overview.agents_active > 0) {
            dot.className = 'status-dot pulse';
            text.textContent = 'Partial Active';
            statusEl.style.borderColor = 'rgba(245, 158, 11, 0.3)';
            statusEl.style.background = 'rgba(245, 158, 11, 0.1)';
            text.style.color = 'var(--accent-amber)';
            dot.style.background = 'var(--accent-amber)';
        } else {
            dot.className = 'status-dot';
            text.textContent = 'Connecting...';
            statusEl.style.borderColor = 'rgba(100, 116, 139, 0.3)';
            statusEl.style.background = 'rgba(100, 116, 139, 0.1)';
            text.style.color = 'var(--text-muted)';
            dot.style.background = 'var(--text-muted)';
        }
    }

    // --- Initialization ---
    function init() {
        console.log('🛡️ CrisisShield AI Dashboard — Initializing');

        // Start clock
        updateClock();
        setInterval(updateClock, 1000);

        // Initialize chart
        chart = new SignalChart('signalChart');

        // Start polling
        fetchAllData();
        pollTimer = setInterval(fetchAllData, POLL_INTERVAL);

        console.log('🛡️ CrisisShield AI Dashboard — Online');
    }

    // Boot
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
