/**
 * CrisisShield AI — API Client
 */

const API_BASE = '';

const api = {
    async get(endpoint) {
        try {
            const response = await fetch(`${API_BASE}${endpoint}`);
            if (!response.ok) throw new Error(`API Error: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`[API] ${endpoint}:`, error.message);
            return null;
        }
    },

    // Dashboard
    async getOverview() { return this.get('/api/dashboard/overview'); },
    async getSignals() { return this.get('/api/dashboard/signals'); },
    async getRiskZones() { return this.get('/api/dashboard/risk-zones'); },
    async getWeather() { return this.get('/api/dashboard/weather'); },
    async getEvents() { return this.get('/api/dashboard/events'); },

    // Alerts
    async getAlerts() { return this.get('/api/alerts'); },
    async getAlertHistory() { return this.get('/api/alerts/history'); },

    // Agents
    async getAgentStatuses() { return this.get('/api/agents/status'); },
    async getAgentDetail(name) { return this.get(`/api/agents/${name}`); },
    async getRescueUnits() { return this.get('/api/agents/rescue/units'); },
    async getResourceInventory() { return this.get('/api/agents/resources/inventory'); },
    async getResourceAllocations() { return this.get('/api/agents/resources/allocations'); },
};
