/**
 * CrisisShield AI — Canvas Charts
 */

class SignalChart {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.dataPoints = [];
        this.maxPoints = 30;
        this.colors = {
            flood: '#3b82f6',
            earthquake: '#a855f7',
            wildfire: '#f97316',
            cyclone: '#06b6d4',
        };
        this._resize();
        window.addEventListener('resize', () => this._resize());
    }

    _resize() {
        const rect = this.canvas.parentElement.getBoundingClientRect();
        this.canvas.width = rect.width - 32;
        this.canvas.height = 180;
        this.draw();
    }

    addDataPoint(signals) {
        const point = { timestamp: Date.now(), counts: {} };
        for (const type of ['flood', 'earthquake', 'wildfire', 'cyclone']) {
            const matching = signals.filter(s => s.disaster_type === type);
            point.counts[type] = matching.length > 0
                ? Math.max(...matching.map(s => s.confidence || 0))
                : 0;
        }
        this.dataPoints.push(point);
        if (this.dataPoints.length > this.maxPoints) {
            this.dataPoints.shift();
        }
        this.draw();
    }

    draw() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;
        const padding = { top: 20, right: 15, bottom: 25, left: 35 };
        const chartW = w - padding.left - padding.right;
        const chartH = h - padding.top - padding.bottom;

        // Clear
        ctx.clearRect(0, 0, w, h);

        // Background
        ctx.fillStyle = 'rgba(15, 23, 42, 0.4)';
        ctx.beginPath();
        ctx.roundRect(0, 0, w, h, 8);
        ctx.fill();

        // Grid lines
        ctx.strokeStyle = 'rgba(100, 116, 139, 0.15)';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 4; i++) {
            const y = padding.top + (chartH / 4) * i;
            ctx.beginPath();
            ctx.moveTo(padding.left, y);
            ctx.lineTo(w - padding.right, y);
            ctx.stroke();

            // Labels
            ctx.fillStyle = 'rgba(100, 116, 139, 0.6)';
            ctx.font = '9px Inter, sans-serif';
            ctx.textAlign = 'right';
            ctx.fillText((100 - i * 25).toString(), padding.left - 6, y + 3);
        }

        if (this.dataPoints.length < 2) {
            ctx.fillStyle = 'rgba(100, 116, 139, 0.4)';
            ctx.font = '12px Inter, sans-serif';
            ctx.textAlign = 'center';
            ctx.fillText('Collecting signal data...', w / 2, h / 2);
            return;
        }

        // Draw lines for each disaster type
        for (const [type, color] of Object.entries(this.colors)) {
            ctx.beginPath();
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.lineJoin = 'round';

            let hasData = false;
            this.dataPoints.forEach((point, i) => {
                const x = padding.left + (i / (this.maxPoints - 1)) * chartW;
                const val = point.counts[type] || 0;
                const y = padding.top + chartH - (val / 100) * chartH;

                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                if (val > 0) hasData = true;
            });

            if (hasData) {
                ctx.stroke();

                // Gradient fill
                const gradient = ctx.createLinearGradient(0, padding.top, 0, h - padding.bottom);
                gradient.addColorStop(0, color + '30');
                gradient.addColorStop(1, color + '05');

                ctx.lineTo(padding.left + ((this.dataPoints.length - 1) / (this.maxPoints - 1)) * chartW, h - padding.bottom);
                ctx.lineTo(padding.left, h - padding.bottom);
                ctx.closePath();
                ctx.fillStyle = gradient;
                ctx.fill();
            }
        }

        // Legend
        let legendX = padding.left;
        ctx.font = '9px Inter, sans-serif';
        for (const [type, color] of Object.entries(this.colors)) {
            ctx.fillStyle = color;
            ctx.fillRect(legendX, h - 10, 8, 8);
            ctx.fillStyle = 'rgba(148, 163, 184, 0.8)';
            ctx.textAlign = 'left';
            ctx.fillText(type.charAt(0).toUpperCase() + type.slice(1), legendX + 12, h - 3);
            legendX += ctx.measureText(type).width + 28;
        }
    }
}
