/**
 * CrisisShield AI — Dashboard Panel Controllers
 */

const Dashboard = {
    // --- Hero Stats ---
    updateOverview(data) {
        if (!data) return;
        this._animateValue('statSignals', data.total_signals);
        this._animateValue('statAlerts', data.active_alerts);
        this._animateValue('statRiskZones', data.regions_at_risk);
        this._animateValue('statRescue', data.rescue_units_deployed);
        this._animateValue('statPeople', data.people_notified, true);
        this._animateValue('statAgents', data.agents_active);
    },

    _animateValue(id, newValue, formatLarge = false) {
        const el = document.getElementById(id);
        if (!el) return;
        const display = formatLarge ? this._formatNumber(newValue) : newValue.toString();
        if (el.textContent !== display) {
            el.textContent = display;
            el.classList.add('value-update');
            setTimeout(() => el.classList.remove('value-update'), 600);
        }
    },

    _formatNumber(num) {
        if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
        if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
        return num.toString();
    },

    // --- Agent Status ---
    updateAgents(data) {
        if (!data || !data.agents) return;
        const agents = data.agents;
        const agentNames = ['SignalWatch', 'RiskPredict', 'CitizenAlert', 'RescueCoordinator', 'ResourceSupply'];
        const icons = { SignalWatch: '📡', RiskPredict: '🎯', CitizenAlert: '📢', RescueCoordinator: '🚑', ResourceSupply: '📦' };

        let activeCount = 0;
        agentNames.forEach(name => {
            const card = document.querySelector(`.agent-card[data-agent="${name}"]`);
            if (!card) return;
            const status = agents[name];
            if (!status) return;

            const indicator = card.querySelector('.agent-indicator');
            const action = card.querySelector('.agent-action');
            const msgs = card.querySelector('.agent-msgs');
            const uptime = card.querySelector('.agent-uptime');

            // Update indicator
            indicator.className = 'agent-indicator ' + (status.state || 'idle');

            // Update text
            action.textContent = status.current_action || 'Idle';
            msgs.textContent = (status.messages_processed || 0) + ' msgs';
            uptime.textContent = this._formatUptime(status.uptime_seconds || 0);

            if (status.state === 'active' || status.state === 'processing') activeCount++;
        });

        const badge = document.getElementById('agentBadge');
        if (badge) badge.textContent = `${activeCount}/5 Active`;
    },

    _formatUptime(seconds) {
        if (seconds < 60) return Math.round(seconds) + 's';
        if (seconds < 3600) return Math.round(seconds / 60) + 'm';
        return (seconds / 3600).toFixed(1) + 'h';
    },

    // --- Risk Zones ---
    updateRiskZones(data) {
        if (!data || !data.risk_zones) return;
        const container = document.getElementById('riskGrid');
        const badge = document.getElementById('riskBadge');
        const zones = data.risk_zones;

        if (zones.length === 0) {
            container.innerHTML = '<div class="risk-placeholder"><div class="placeholder-icon">🌐</div><p>No active risk zones — all clear</p></div>';
            badge.textContent = '0 Zones';
            return;
        }

        badge.textContent = `${zones.length} Zone${zones.length > 1 ? 's' : ''}`;

        const typeIcons = { flood: '🌊', earthquake: '🫨', wildfire: '🔥', cyclone: '🌀' };

        container.innerHTML = zones.map(zone => {
            const level = (zone.risk_level || 'low').toLowerCase();
            return `
                <div class="risk-zone-card ${level}">
                    <div class="risk-score-badge ${level}">${Math.round(zone.risk_score)}</div>
                    <div class="risk-details">
                        <h4>${typeIcons[zone.disaster_type] || '⚠️'} ${zone.region_name || zone.region_id}</h4>
                        <div class="risk-meta">
                            ${zone.disaster_type.toUpperCase()} • ${zone.risk_level} •
                            ${(zone.population_at_risk || 0).toLocaleString()} at risk •
                            ETA: ${zone.estimated_impact_time_hours || '?'}h
                        </div>
                        <div class="risk-action">${zone.recommended_action || ''}</div>
                    </div>
                </div>
            `;
        }).join('');
    },

    // --- Alert Feed ---
    updateAlerts(data) {
        if (!data || !data.alerts) return;
        const container = document.getElementById('alertFeed');
        const badge = document.getElementById('alertBadge');
        const alerts = data.alerts.slice(0, 20);

        badge.textContent = `${data.total || alerts.length} Active`;

        if (alerts.length === 0) {
            container.innerHTML = '<div class="alert-placeholder"><div class="placeholder-icon">🔕</div><p>No active alerts — system monitoring</p></div>';
            return;
        }

        container.innerHTML = alerts.map(alert => {
            const level = (alert.risk_level || 'moderate').toLowerCase();
            const time = this._formatTime(alert.timestamp);
            const channels = (alert.channels || []).map(c =>
                `<span class="alert-channel">${c}</span>`
            ).join('');

            return `
                <div class="alert-item ${level === 'critical' ? 'critical-alert' : level === 'high' ? 'high-alert' : ''}">
                    <div class="alert-header">
                        <span class="alert-level ${level}">${alert.risk_level || 'ALERT'}</span>
                        <span class="alert-time">${time}</span>
                    </div>
                    <div class="alert-region">${alert.region_name || alert.region_id} — ${(alert.disaster_type || '').toUpperCase()}</div>
                    <div class="alert-message">${this._escapeHtml(alert.message || '')}</div>
                    <div class="alert-channels">${channels}</div>
                </div>
            `;
        }).join('');
    },

    _formatTime(isoString) {
        if (!isoString) return '';
        try {
            const d = new Date(isoString);
            return d.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        } catch { return ''; }
    },

    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // --- Rescue Units ---
    updateRescueUnits(data) {
        if (!data) return;
        const units = data.units || [];
        const deployed = units.filter(u => u.status !== 'standby');

        const badge = document.getElementById('rescueBadge');
        badge.textContent = `${deployed.length} Active`;

        // Summary bars
        const ambulances = units.filter(u => u.unit_type === 'ambulance');
        const boats = units.filter(u => u.unit_type === 'rescue_boat');
        const teams = units.filter(u => u.unit_type === 'relief_team');

        const ambDeployed = ambulances.filter(u => u.status !== 'standby').length;
        const boatDeployed = boats.filter(u => u.status !== 'standby').length;
        const teamDeployed = teams.filter(u => u.status !== 'standby').length;

        document.getElementById('rescueAmbulances').textContent = `${ambDeployed} / ${ambulances.length}`;
        document.getElementById('rescueBoats').textContent = `${boatDeployed} / ${boats.length}`;
        document.getElementById('rescueTeams').textContent = `${teamDeployed} / ${teams.length}`;

        document.getElementById('rescueAmbBar').style.width = ambulances.length ? (ambDeployed / ambulances.length * 100) + '%' : '0%';
        document.getElementById('rescueBoatBar').style.width = boats.length ? (boatDeployed / boats.length * 100) + '%' : '0%';
        document.getElementById('rescueTeamBar').style.width = teams.length ? (teamDeployed / teams.length * 100) + '%' : '0%';

        // Unit list (show only deployed, max 15)
        const list = document.getElementById('rescueUnitsList');
        const deployedUnits = deployed.slice(0, 15);
        list.innerHTML = deployedUnits.map(u => `
            <div class="rescue-unit-item">
                <span class="rescue-unit-id">${u.id}</span>
                <span class="rescue-unit-status ${u.status.replace(' ', '_')}">${u.status}</span>
                <span class="rescue-unit-region">${u.assigned_region_name || u.assigned_region}</span>
                ${u.eta_minutes > 0 ? `<span style="color: var(--accent-amber); font-size: 0.6rem;">ETA: ${u.eta_minutes}m</span>` : ''}
            </div>
        `).join('');
    },

    // --- Resources ---
    updateResources(inventory, allocations) {
        if (inventory && inventory.inventory) {
            const inv = inventory.inventory;
            const maxes = { food_packets: 50000, medical_kits: 8000, water_liters: 100000, shelter_capacity: 15000 };

            this._updateResourceItem('resFood', 'resFoodBar', inv.food_packets, maxes.food_packets);
            this._updateResourceItem('resMedical', 'resMedBar', inv.medical_kits, maxes.medical_kits);
            this._updateResourceItem('resWater', 'resWaterBar', inv.water_liters, maxes.water_liters);
            this._updateResourceItem('resShelter', 'resShelterBar', inv.shelter_capacity, maxes.shelter_capacity);
        }

        if (allocations && allocations.allocations) {
            const list = document.getElementById('allocationList');
            const allocs = allocations.allocations.slice(0, 10);
            list.innerHTML = allocs.map(a => `
                <div class="allocation-item">
                    <span class="allocation-region">${a.region_name || a.region_id}</span>
                    <span class="allocation-details">
                        🍞${a.food_packets} 🏥${a.medical_kits} 💧${a.water_liters}
                    </span>
                </div>
            `).join('');
        }
    },

    _updateResourceItem(valueId, barId, current, max) {
        const valueEl = document.getElementById(valueId);
        const barEl = document.getElementById(barId);
        if (!valueEl || !barEl) return;

        const val = Math.max(0, current || 0);
        valueEl.textContent = val.toLocaleString();
        const pct = max > 0 ? (val / max * 100) : 0;
        barEl.style.width = pct + '%';

        barEl.className = 'resource-fill';
        if (pct < 25) barEl.classList.add('low');
        else if (pct < 50) barEl.classList.add('medium');
    },

    // --- Signals ---
    updateSignals(data) {
        if (!data || !data.signals) return;
        const list = document.getElementById('signalList');
        const signals = data.signals.slice(0, 10);

        list.innerHTML = signals.map(s => `
            <div class="signal-item">
                <span class="signal-type ${s.disaster_type}">${s.disaster_type}</span>
                <span class="signal-region">${s.region_name || s.region_id}</span>
                <span class="signal-conf" style="color: ${s.confidence >= 75 ? 'var(--accent-red)' : s.confidence >= 50 ? 'var(--accent-amber)' : 'var(--accent-green)'}">${Math.round(s.confidence)}%</span>
            </div>
        `).join('');
    },
};
