/* ================================================================
   CyberShield - Dashboard de Hacking Ético
   JavaScript Principal
   ================================================================ */

// ---- Particle Background ----
(function initParticles() {
    const canvas = document.getElementById('particleCanvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let particles = [];

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    class Particle {
        constructor() {
            this.reset();
        }
        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 1.5 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = (Math.random() - 0.5) * 0.4;
            this.opacity = Math.random() * 0.5 + 0.1;
        }
        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            if (this.x < 0 || this.x > canvas.width || this.y < 0 || this.y > canvas.height) {
                this.reset();
            }
        }
        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(6, 214, 160, ${this.opacity})`;
            ctx.fill();
        }
    }

    for (let i = 0; i < 80; i++) {
        particles.push(new Particle());
    }

    function drawLines() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 150) {
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = `rgba(6, 214, 160, ${0.08 * (1 - dist / 150)})`;
                    ctx.lineWidth = 0.5;
                    ctx.stroke();
                }
            }
        }
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        particles.forEach(p => { p.update(); p.draw(); });
        drawLines();
        requestAnimationFrame(animate);
    }
    animate();
})();

// ================================================================
// NAVIGATION
// ================================================================
function navigateTo(section) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));

    // Deactivate all nav links
    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));

    // Show target section
    const targetSection = document.getElementById(`section-${section}`);
    if (targetSection) {
        targetSection.classList.add('active');
    }

    // Activate nav link
    const targetLink = document.querySelector(`.nav-link[data-section="${section}"]`);
    if (targetLink) {
        targetLink.classList.add('active');
    }
}

// Setup navigation clicks
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        const section = link.dataset.section;
        navigateTo(section);
    });
});

// ================================================================
// TOAST NOTIFICATIONS
// ================================================================
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;

    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
    };

    toast.innerHTML = `
        <span style="font-size:1.1rem">${icons[type] || '●'}</span>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('toast-out');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ================================================================
// 1. PORT SCANNER
// ================================================================
async function startPortScan() {
    const target = document.getElementById('scan-target').value.trim();
    const startPort = parseInt(document.getElementById('scan-start-port').value);
    const endPort = parseInt(document.getElementById('scan-end-port').value);

    if (!target) {
        showToast('Ingresa una dirección IP o hostname', 'error');
        return;
    }

    if (startPort > endPort || startPort < 1 || endPort > 65535) {
        showToast('Rango de puertos inválido', 'error');
        return;
    }

    // Update UI
    const btn = document.getElementById('btn-scan');
    btn.disabled = true;
    btn.innerHTML = `
        <div class="cyber-loader" style="width:18px;height:18px;border-width:2px"></div>
        Escaneando...
    `;

    document.getElementById('scan-status').className = 'status-badge scanning';
    document.getElementById('scan-status').textContent = 'Escaneando';
    document.getElementById('scan-loading').classList.remove('hidden');
    document.getElementById('scan-empty').classList.add('hidden');
    document.getElementById('scan-results-table').classList.add('hidden');
    document.getElementById('scan-info').classList.add('hidden');

    try {
        const response = await fetch('/api/scan-ports', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ target, start_port: startPort, end_port: endPort })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        // Display results
        document.getElementById('scan-loading').classList.add('hidden');
        document.getElementById('scan-info').classList.remove('hidden');
        document.getElementById('scan-status').className = 'status-badge complete';
        document.getElementById('scan-status').textContent = 'Completado';

        // Fill info
        document.getElementById('info-target').textContent = data.target;
        document.getElementById('info-ip').textContent = data.target_ip;
        document.getElementById('info-total').textContent = data.total_scanned.toLocaleString();
        document.getElementById('info-open').textContent = data.open_count;
        document.getElementById('info-duration').textContent = `${data.scan_duration}s`;

        // Fill table
        const tbody = document.getElementById('scan-table-body');
        tbody.innerHTML = '';

        if (data.open_ports.length > 0) {
            document.getElementById('scan-results-table').classList.remove('hidden');
            data.open_ports.forEach((port, i) => {
                const row = document.createElement('tr');
                row.style.animationDelay = `${i * 0.05}s`;
                row.innerHTML = `
                    <td class="port-open">${port.port}</td>
                    <td><span style="color: var(--accent-cyan)">●</span> ${port.state}</td>
                    <td>${port.service}</td>
                    <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"
                        title="${escapeHtml(port.banner)}">${escapeHtml(port.banner) || '-'}</td>
                `;
                tbody.appendChild(row);
            });
            showToast(`Escaneo completado: ${data.open_count} puertos abiertos encontrados`, 'success');
        } else {
            document.getElementById('scan-results-table').classList.remove('hidden');
            tbody.innerHTML = `<tr><td colspan="4" style="text-align:center;color:var(--text-muted);padding:30px">
                No se encontraron puertos abiertos en el rango ${startPort}-${endPort}</td></tr>`;
            showToast('Escaneo completado: No se encontraron puertos abiertos', 'warning');
        }

    } catch (error) {
        document.getElementById('scan-loading').classList.add('hidden');
        document.getElementById('scan-empty').classList.remove('hidden');
        document.getElementById('scan-status').className = 'status-badge error';
        document.getElementById('scan-status').textContent = 'Error';
        showToast(`Error: ${error.message}`, 'error');
    }

    btn.disabled = false;
    btn.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="18" height="18">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        Iniciar Escaneo
    `;
}

// ================================================================
// 2. PASSWORD GENERATOR
// ================================================================
function updateLengthDisplay() {
    const value = document.getElementById('pwd-length').value;
    document.getElementById('pwd-length-display').textContent = value;
}

async function generatePasswords() {
    const length = parseInt(document.getElementById('pwd-length').value);
    const count = parseInt(document.getElementById('pwd-count').value);

    if (length < 8) {
        showToast('La longitud mínima es de 8 caracteres', 'error');
        return;
    }

    if (count < 1 || count > 100) {
        showToast('La cantidad debe ser entre 1 y 100', 'error');
        return;
    }

    const btn = document.getElementById('btn-generate');
    btn.disabled = true;
    document.getElementById('pwd-loading').classList.remove('hidden');
    document.getElementById('pwd-empty').classList.add('hidden');
    document.getElementById('pwd-results').innerHTML = '';

    try {
        const response = await fetch('/api/generate-passwords', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ length, count })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        document.getElementById('pwd-loading').classList.add('hidden');
        const container = document.getElementById('pwd-results');

        data.passwords.forEach((pwd, i) => {
            const item = document.createElement('div');
            item.className = 'password-item';
            item.style.animationDelay = `${i * 0.06}s`;

            const strengthWidth = (pwd.strength.score / 5) * 100;

            item.innerHTML = `
                <div class="password-row">
                    <span class="password-index">#${i + 1}</span>
                    <span class="password-text">${escapeHtml(pwd.password)}</span>
                    <button class="password-copy" onclick="copyPassword(this, '${escapeHtml(pwd.password)}')">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                            <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                        </svg>
                        Copiar
                    </button>
                </div>
                <div class="password-meta">
                    <div class="password-strength">
                        <div class="strength-bar-bg">
                            <div class="strength-bar" style="width:${strengthWidth}%;background:${pwd.strength.color}"></div>
                        </div>
                        <span class="strength-label" style="color:${pwd.strength.color}">${pwd.strength.level}</span>
                    </div>
                    <span class="password-entropy">Entropía: ${pwd.entropy} bits</span>
                </div>
            `;
            container.appendChild(item);
        });

        showToast(`${data.passwords.length} contraseñas generadas exitosamente`, 'success');

    } catch (error) {
        document.getElementById('pwd-loading').classList.add('hidden');
        document.getElementById('pwd-empty').classList.remove('hidden');
        showToast(`Error: ${error.message}`, 'error');
    }

    btn.disabled = false;
}

function copyPassword(btn, password) {
    navigator.clipboard.writeText(password).then(() => {
        btn.classList.add('copied');
        btn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
            Copiado
        `;
        showToast('Contraseña copiada al portapapeles', 'success');

        setTimeout(() => {
            btn.classList.remove('copied');
            btn.innerHTML = `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1"/>
                </svg>
                Copiar
            `;
        }, 2000);
    });
}

// ================================================================
// 3. SNIFFER
// ================================================================
let snifferPolling = null;

async function startSniffer() {
    const iface = document.getElementById('sniff-interface').value.trim();
    const count = parseInt(document.getElementById('sniff-count').value);
    const filter = document.getElementById('sniff-filter').value.trim();

    document.getElementById('btn-sniff-start').disabled = true;
    document.getElementById('btn-sniff-stop').disabled = false;

    try {
        const response = await fetch('/api/sniffer/start', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                interface: iface || null,
                packet_count: count,
                filter: filter
            })
        });

        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        document.getElementById('sniff-status-state').textContent = 'Capturando...';
        document.getElementById('sniff-status-state').style.color = 'var(--accent-cyan)';
        document.getElementById('sniff-status-iface').textContent = data.interface;
        document.getElementById('sniff-empty').classList.add('hidden');

        showToast('Sniffer iniciado - Capturando paquetes', 'success');

        // Start polling
        snifferPolling = setInterval(refreshSnifferPackets, 2000);

    } catch (error) {
        document.getElementById('btn-sniff-start').disabled = false;
        document.getElementById('btn-sniff-stop').disabled = true;
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function stopSniffer() {
    if (snifferPolling) {
        clearInterval(snifferPolling);
        snifferPolling = null;
    }

    try {
        const response = await fetch('/api/sniffer/stop', { method: 'POST' });
        const data = await response.json();

        document.getElementById('btn-sniff-start').disabled = false;
        document.getElementById('btn-sniff-stop').disabled = true;
        document.getElementById('sniff-status-state').textContent = 'Detenido';
        document.getElementById('sniff-status-state').style.color = 'var(--text-tertiary)';

        showToast(`Sniffer detenido - ${data.packets_captured || 0} paquetes capturados`, 'warning');
        refreshSnifferPackets();

    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function refreshSnifferPackets() {
    try {
        const [statusRes, packetsRes] = await Promise.all([
            fetch('/api/sniffer/status'),
            fetch('/api/sniffer/packets')
        ]);

        const status = await statusRes.json();
        const packetsData = await packetsRes.json();

        // Update status
        document.getElementById('sniff-status-count').textContent = status.packets_captured;

        if (!status.running && snifferPolling) {
            clearInterval(snifferPolling);
            snifferPolling = null;
            document.getElementById('btn-sniff-start').disabled = false;
            document.getElementById('btn-sniff-stop').disabled = true;
            document.getElementById('sniff-status-state').textContent = 'Completado';
            document.getElementById('sniff-status-state').style.color = 'var(--accent-blue)';
        }

        // Update table
        const packets = packetsData.packets || [];
        if (packets.length > 0) {
            document.getElementById('sniff-results-table').classList.remove('hidden');
            document.getElementById('sniff-empty').classList.add('hidden');

            const tbody = document.getElementById('sniff-table-body');
            tbody.innerHTML = '';

            packets.forEach(pkt => {
                const row = document.createElement('tr');
                const protocolClass = `protocol-${(pkt.protocol || 'other').toLowerCase()}`;

                let infoText = '';
                if (pkt.src_port) infoText += `${pkt.src_port} → ${pkt.dst_port}`;
                if (pkt.app_protocol) infoText += ` [${pkt.app_protocol}]`;
                if (pkt.payload_type === 'Texto Plano (¡No seguro!)') {
                    infoText += ' ⚠️';
                }

                const srcDisplay = pkt.src_ip || pkt.src_mac || '-';
                const dstDisplay = pkt.dst_ip || pkt.dst_mac || '-';

                row.innerHTML = `
                    <td>${pkt.id}</td>
                    <td>${pkt.timestamp}</td>
                    <td><span class="protocol-tag ${protocolClass}">${pkt.protocol || '-'}</span></td>
                    <td>${srcDisplay}</td>
                    <td>${dstDisplay}</td>
                    <td class="packet-payload ${pkt.payload_type === 'Texto Plano (¡No seguro!)' ? 'payload-insecure' : ''}"
                        title="${escapeHtml(pkt.payload || '')}">${escapeHtml(infoText)}</td>
                `;
                tbody.appendChild(row);
            });
        }

    } catch (error) {
        // Silently fail on polling errors
    }
}

// ================================================================
// 4. KEYLOGGER
// ================================================================
let keyloggerPolling = null;

async function startKeylogger() {
    document.getElementById('btn-keylog-start').disabled = true;
    document.getElementById('btn-keylog-stop').disabled = false;

    try {
        const response = await fetch('/api/keylogger/start', { method: 'POST' });
        const data = await response.json();

        if (data.error) {
            throw new Error(data.error);
        }

        document.getElementById('keylog-status-state').textContent = 'Capturando...';
        document.getElementById('keylog-status-state').style.color = 'var(--accent-cyan)';
        document.getElementById('keylog-status-time').textContent = data.start_time;
        document.getElementById('keylog-empty').classList.add('hidden');

        showToast('Keylogger iniciado - Capturando pulsaciones', 'success');

        keyloggerPolling = setInterval(refreshKeylogger, 1500);

    } catch (error) {
        document.getElementById('btn-keylog-start').disabled = false;
        document.getElementById('btn-keylog-stop').disabled = true;
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function stopKeylogger() {
    if (keyloggerPolling) {
        clearInterval(keyloggerPolling);
        keyloggerPolling = null;
    }

    try {
        const response = await fetch('/api/keylogger/stop', { method: 'POST' });
        const data = await response.json();

        document.getElementById('btn-keylog-start').disabled = false;
        document.getElementById('btn-keylog-stop').disabled = true;
        document.getElementById('keylog-status-state').textContent = 'Detenido';
        document.getElementById('keylog-status-state').style.color = 'var(--text-tertiary)';

        showToast(`Keylogger detenido - ${data.keys_captured || 0} teclas capturadas`, 'warning');
        refreshKeylogger();

    } catch (error) {
        showToast(`Error: ${error.message}`, 'error');
    }
}

async function refreshKeylogger() {
    try {
        const [statusRes, logRes] = await Promise.all([
            fetch('/api/keylogger/status'),
            fetch('/api/keylogger/log')
        ]);

        const status = await statusRes.json();
        const logData = await logRes.json();

        // Update status
        document.getElementById('keylog-status-count').textContent = status.keys_captured;

        // Update reconstructed text
        if (logData.reconstructed_text) {
            document.getElementById('keylog-text-container').classList.remove('hidden');
            const textEl = document.getElementById('keylog-reconstructed');
            // Highlight special keys
            textEl.innerHTML = escapeHtml(logData.reconstructed_text)
                .replace(/\[([^\]]+)\]/g, '<span class="key-special">[$1]</span>');
        }

        // Update table
        const keys = logData.keys || [];
        if (keys.length > 0) {
            document.getElementById('keylog-results-table').classList.remove('hidden');
            document.getElementById('keylog-empty').classList.add('hidden');

            const tbody = document.getElementById('keylog-table-body');
            tbody.innerHTML = '';

            // Show last 50 keys (reversed to show newest first)
            const recentKeys = keys.slice(-50).reverse();
            recentKeys.forEach(key => {
                const row = document.createElement('tr');
                const typeLabels = {
                    'character': 'Carácter',
                    'special': 'Especial',
                    'function': 'Función',
                };
                row.innerHTML = `
                    <td>${key.id}</td>
                    <td style="font-family:var(--font-mono)">${escapeHtml(key.key)}</td>
                    <td>${typeLabels[key.type] || key.type}</td>
                    <td>${key.timestamp}</td>
                `;
                tbody.appendChild(row);
            });
        }

    } catch (error) {
        // Silently fail on polling errors
    }
}

// ================================================================
// UTILITIES
// ================================================================
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcut to navigate sections
document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key >= '1' && e.key <= '5') {
        e.preventDefault();
        const sections = ['dashboard', 'port-scanner', 'password-gen', 'sniffer', 'keylogger'];
        const idx = parseInt(e.key) - 1;
        if (idx < sections.length) {
            navigateTo(sections[idx]);
        }
    }
});
