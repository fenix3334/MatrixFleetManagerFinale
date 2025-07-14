// EFFETTI MATRIX AVANZATI - Matrix Fleet Manager
class MatrixEffect {
    constructor() {
        this.canvas = document.getElementById('matrix-canvas');
        this.ctx = this.canvas.getContext('2d');
        this.characters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!@#$%^&*()_+-=[]{}|;:,.<>?';
        this.fontSize = 14;
        this.columns = 0;
        this.drops = [];
        
        this.init();
        this.animate();
        this.addInteractiveEffects();
    }
    
    init() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
        this.columns = this.canvas.width / this.fontSize;
        
        // Inizializza le gocce
        for (let i = 0; i < this.columns; i++) {
            this.drops[i] = Math.random() * this.canvas.height / this.fontSize;
        }
    }
    
    animate() {
        // Sfondo semi-trasparente per effetto scia
        this.ctx.fillStyle = 'rgba(13, 17, 23, 0.05)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Stile del testo
        this.ctx.fillStyle = '#00ff41';
        this.ctx.font = `${this.fontSize}px monospace`;
        
        // Disegna i caratteri
        for (let i = 0; i < this.drops.length; i++) {
            const text = this.characters.charAt(Math.floor(Math.random() * this.characters.length));
            const x = i * this.fontSize;
            const y = this.drops[i] * this.fontSize;
            
            // Gradiente di opacità
            const opacity = Math.random() * 0.5 + 0.5;
            this.ctx.fillStyle = `rgba(0, 255, 65, ${opacity})`;
            this.ctx.fillText(text, x, y);
            
            // Reset delle gocce
            if (y > this.canvas.height && Math.random() > 0.975) {
                this.drops[i] = 0;
            }
            
            this.drops[i]++;
        }
        
        requestAnimationFrame(() => this.animate());
    }
    
    addInteractiveEffects() {
        // Effetto particelle al movimento del mouse
        let mouseX = 0;
        let mouseY = 0;
        
        document.addEventListener('mousemove', (e) => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            
            // Crea particelle verdi intorno al cursore
            if (Math.random() > 0.9) {
                this.createParticles(mouseX, mouseY);
            }
        });
        
        // Effetti al click
        document.addEventListener('click', (e) => {
            this.createExplosion(e.clientX, e.clientY);
        });
        
        // Resize handler
        window.addEventListener('resize', () => {
            this.init();
        });
    }
    
    createParticles(x, y) {
        const particle = document.createElement('div');
        particle.style.position = 'fixed';
        particle.style.left = x + 'px';
        particle.style.top = y + 'px';
        particle.style.width = '4px';
        particle.style.height = '4px';
        particle.style.background = '#00ff41';
        particle.style.borderRadius = '50%';
        particle.style.pointerEvents = 'none';
        particle.style.zIndex = '9999';
        particle.style.boxShadow = '0 0 10px #00ff41';
        
        document.body.appendChild(particle);
        
        // Animazione particella
        const animation = particle.animate([
            { transform: 'translate(0, 0) scale(1)', opacity: 1 },
            { transform: `translate(${Math.random() * 100 - 50}px, ${Math.random() * 100 - 50}px) scale(0)`, opacity: 0 }
        ], {
            duration: 1000,
            easing: 'ease-out'
        });
        
        animation.onfinish = () => particle.remove();
    }
    
    createExplosion(x, y) {
        for (let i = 0; i < 12; i++) {
            setTimeout(() => {
                const particle = document.createElement('div');
                particle.style.position = 'fixed';
                particle.style.left = x + 'px';
                particle.style.top = y + 'px';
                particle.style.width = '6px';
                particle.style.height = '6px';
                particle.style.background = '#00ff41';
                particle.style.borderRadius = '50%';
                particle.style.pointerEvents = 'none';
                particle.style.zIndex = '9999';
                particle.style.boxShadow = '0 0 15px #00ff41';
                
                document.body.appendChild(particle);
                
                const angle = (i / 12) * Math.PI * 2;
                const distance = 100;
                const endX = Math.cos(angle) * distance;
                const endY = Math.sin(angle) * distance;
                
                const animation = particle.animate([
                    { transform: 'translate(0, 0) scale(1)', opacity: 1 },
                    { transform: `translate(${endX}px, ${endY}px) scale(0)`, opacity: 0 }
                ], {
                    duration: 800,
                    easing: 'ease-out'
                });
                
                animation.onfinish = () => particle.remove();
            }, i * 50);
        }
    }
}

// Effetti aggiuntivi per l'UI
class UIEffects {
    constructor() {
        this.addTypingEffect();
        this.addGlowEffects();
        this.addScanlineEffect();
        this.addCounterAnimations();
    }
    
    addTypingEffect() {
        const titles = document.querySelectorAll('.page-title, .form-title, .detail-title');
        titles.forEach(title => {
            const text = title.textContent;
            const icon = title.querySelector('i');
            const originalText = text.replace(/\s+/g, ' ').trim();
            
            title.innerHTML = '';
            
            if (icon) {
                title.appendChild(icon);
                title.appendChild(document.createTextNode(' '));
            }
            
            const textSpan = document.createElement('span');
            title.appendChild(textSpan);
            
            let i = 0;
            const typeInterval = setInterval(() => {
                if (i < originalText.length) {
                    textSpan.textContent += originalText.charAt(i);
                    i++;
                } else {
                    clearInterval(typeInterval);
                }
            }, 50);
        });
    }
    
    addGlowEffects() {
        // Effetto glow sui pulsanti
        const buttons = document.querySelectorAll('.btn-primary');
        buttons.forEach(btn => {
            btn.addEventListener('mouseenter', () => {
                btn.style.animation = 'pulse-glow 1s infinite';
            });
            
            btn.addEventListener('mouseleave', () => {
                btn.style.animation = '';
            });
        });
        
        // Effetto glow sui link di navigazione
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            link.addEventListener('mouseenter', () => {
                link.style.textShadow = '0 0 10px #00ff41';
            });
            
            link.addEventListener('mouseleave', () => {
                if (!link.classList.contains('active')) {
                    link.style.textShadow = '';
                }
            });
        });
    }
    
    addScanlineEffect() {
        const scanline = document.createElement('div');
        scanline.style.position = 'fixed';
        scanline.style.top = '0';
        scanline.style.left = '0';
        scanline.style.width = '100%';
        scanline.style.height = '2px';
        scanline.style.background = 'linear-gradient(90deg, transparent, #00ff41, transparent)';
        scanline.style.pointerEvents = 'none';
        scanline.style.zIndex = '10000';
        scanline.style.opacity = '0.3';
        
        document.body.appendChild(scanline);
        
        // Animazione scanline
        scanline.animate([
            { transform: 'translateY(0)' },
            { transform: `translateY(${window.innerHeight}px)` }
        ], {
            duration: 3000,
            iterations: Infinity,
            easing: 'linear'
        });
    }
    
    addCounterAnimations() {
        // Contatore statistiche animate
        const statNumbers = document.querySelectorAll('.stat-number');
        statNumbers.forEach(stat => {
            const text = stat.textContent;
            const target = parseInt(text.replace(/\D/g, ''));
            
            if (target > 0) {
                let current = 0;
                const increment = target / 50;
                
                const timer = setInterval(() => {
                    current += increment;
                    if (current >= target) {
                        stat.textContent = text;
                        clearInterval(timer);
                    } else {
                        stat.textContent = text.replace(/\d+/, Math.floor(current));
                    }
                }, 50);
            }
        });
    }
}

// Audio Effects (opzionale)
class AudioEffects {
    constructor() {
        this.audioContext = null;
        this.initAudio();
    }
    
    initAudio() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.log('Audio context not supported');
        }
    }
    
    playBeep(frequency = 800, duration = 100) {
        if (!this.audioContext) return;
        
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = 'square';
        
        gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration / 1000);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration / 1000);
    }
    
    playHoverSound() {
        this.playBeep(1200, 50);
    }
    
    playClickSound() {
        this.playBeep(800, 100);
    }
    
    playSuccessSound() {
        this.playBeep(1000, 200);
        setTimeout(() => this.playBeep(1200, 200), 100);
    }
}

// Performance monitoring
class PerformanceMonitor {
    constructor() {
        this.fps = 0;
        this.lastTime = performance.now();
        this.frameCount = 0;
        
        this.monitor();
    }
    
    monitor() {
        const now = performance.now();
        this.frameCount++;
        
        if (now - this.lastTime >= 1000) {
            this.fps = this.frameCount;
            this.frameCount = 0;
            this.lastTime = now;
            
            // Aggiorna indicatore performance se presente
            const perfIndicator = document.getElementById('perf-indicator');
            if (perfIndicator) {
                perfIndicator.textContent = `${this.fps} FPS`;
                perfIndicator.style.color = this.fps > 30 ? '#00ff41' : '#ff4757';
            }
        }
        
        requestAnimationFrame(() => this.monitor());
    }
}

// Inizializzazione
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Matrix Fleet Manager - Inizializzazione effetti...');
    
    // Inizializza tutti gli effetti
    new MatrixEffect();
    new UIEffects();
    
    const audioEffects = new AudioEffects();
    
    // Aggiungi suoni ai click
    document.addEventListener('click', (e) => {
        if (e.target.matches('.btn, .nav-link, .btn-action')) {
            audioEffects.playClickSound();
        }
    });
    
    // Suoni hover
    document.addEventListener('mouseover', (e) => {
        if (e.target.matches('.btn-primary, .action-button')) {
            audioEffects.playHoverSound();
        }
    });
    
    // Suono successo per flash messages
    const successFlash = document.querySelector('.flash-success');
    if (successFlash) {
        audioEffects.playSuccessSound();
    }
    
    // Avvia monitoraggio performance
    new PerformanceMonitor();
    
    console.log('✅ Matrix Fleet Manager - Effetti caricati con successo!');
    console.log('🎮 Comandi disponibili:');
    console.log('   - Click: Effetti particellari');
    console.log('   - Hover: Glow effects');
    console.log('   - Audio: Suoni futuristici');
});

// Funzioni globali di utilità
window.MatrixFleet = {
    // Mostra notifica Matrix-style
    showNotification: function(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `matrix-notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-info-circle"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #161b22, #21262d);
            color: #00ff41;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            border: 1px solid #00ff41;
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
            z-index: 10000;
            animation: slideInRight 0.5s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.5s ease';
            setTimeout(() => notification.remove(), 500);
        }, 3000);
    },
    
    // Effetto digitazione
    typeText: function(element, text, speed = 50) {
        element.textContent = '';
        let i = 0;
        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
    },
    
    // Genera password Matrix-style
    generateMatrixCode: function(length = 10) {
        const chars = '0123456789ABCDEF';
        let result = '';
        for (let i = 0; i < length; i++) {
            result += chars.charAt(Math.floor(Math.random() * chars.length));
        }
        return result;
    }
};

// CSS per animazioni aggiuntive
const additionalStyles = `
@keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
}

@keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
}

@keyframes pulse-glow {
    0%, 100% { box-shadow: 0 4px 15px rgba(0, 255, 65, 0.3); }
    50% { box-shadow: 0 6px 25px rgba(0, 255, 65, 0.6); }
}
`;

// Inietta gli stili aggiuntivi
const styleSheet = document.createElement('style');
styleSheet.textContent = additionalStyles;
document.head.appendChild(styleSheet);

// Easter egg: Konami Code
let konamiCode = [];
const konamiSequence = [38, 38, 40, 40, 37, 39, 37, 39, 66, 65]; // ↑↑↓↓←→←→BA

document.addEventListener('keydown', (e) => {
    konamiCode.push(e.keyCode);
    if (konamiCode.length > konamiSequence.length) {
        konamiCode.shift();
    }
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
        // Attiva modalità "NEO"
        document.body.style.filter = 'hue-rotate(120deg) contrast(1.2)';
        window.MatrixFleet.showNotification('🕶️ Modalità NEO attivata! Benvenuto nella Matrix!', 'success');
        
        // Effetto temporaneo
        setTimeout(() => {
            document.body.style.filter = '';
        }, 10000);
        
        konamiCode = [];
    }
});