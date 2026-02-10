class UltraDashboard {
  constructor() {
    this.ownerId = 8496419402; // YOUR TELEGRAM ID
    this.ws = null;
    this.charts = {};
    this.particles = [];
    this.currentBg = "";
    this.init();
  }

  async init() {
    await this.initAnimations();
    await this.loadAnimeBackground();
    await this.initCharts();
    await this.connectWebSocket();
    await this.loadInitialData();
    this.startParticleSystem();
    this.hideLoading();
  }

  async initAnimations() {
    gsap.registerPlugin(ScrollTrigger);

    // Hero animations
    gsap.from(".stat-card", {
      y: 100,
      opacity: 0,
      duration: 1,
      stagger: 0.1,
      ease: "back.out(1.7)",
    });

    // Continuous floating
    gsap.to(".stat-card", {
      y: -10,
      rotation: 1,
      duration: 4,
      repeat: -1,
      yoyo: true,
      ease: "sine.inOut",
      stagger: {
        amount: 1.5,
      },
    });

    // Navbar shine effect
    gsap.to(".glass-nav", {
      scale: 1.02,
      duration: 2,
      repeat: -1,
      yoyo: true,
      ease: "none",
    });
  }

  async loadAnimeBackground() {
    try {
      const res = await fetch("/api/background");
      const { url } = await res.json();
      const bg = document.getElementById("anime-bg");
      bg.style.backgroundImage = `url(${url})`;
      bg.style.backgroundSize = "cover";
      bg.style.backgroundPosition = "center";
      this.currentBg = url;
    } catch (e) {
      console.log("Background fallback");
    }
  }

  startParticleSystem() {
    const canvas = document.getElementById("particles");
    const ctx = canvas.getContext("2d");
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    for (let i = 0; i < 120; i++) {
      this.particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.8,
        vy: (Math.random() - 0.5) * 0.8,
        radius: Math.random() * 3 + 1,
        hue: Math.random() * 60 + 240, // Purple-blue spectrum
        alpha: Math.random() * 0.5 + 0.2,
      });
    }

    function animate() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      this.particles.forEach((p) => {
        p.x += p.vx;
        p.y += p.vy;
        p.alpha += (Math.random() - 0.5) * 0.02;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.save();
        ctx.globalAlpha = Math.max(0.1, p.alpha);
        ctx.translate(p.x, p.y);
        ctx.fillStyle = `hsla(${p.hue}, 70%, 60%, 0.6)`;
        ctx.shadowColor = `hsla(${p.hue}, 70%, 50%, 0.8)`;
        ctx.shadowBlur = 10;
        ctx.beginPath();
        ctx.arc(0, 0, p.radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      });

      requestAnimationFrame(() => animate.call(this));
    }
    animate.call(this);
  }

  async initCharts() {
    const ctx = document.getElementById("reactionsChart")?.getContext("2d");
    if (!ctx) return;

    this.charts.reactions = new Chart(ctx, {
      type: "line",
      data: {
        labels: Array(24)
          .fill()
          .map((_, i) => `${i}h`),
        datasets: [
          {
            label: "Reactions",
            data: Array(24).fill(0),
            borderColor: "#a855f7",
            backgroundColor: "rgba(168, 85, 247, 0.2)",
            tension: 0.4,
            fill: true,
            pointBackgroundColor: "#ffffff",
            pointBorderColor: "#a855f7",
            pointRadius: 6,
            pointHoverRadius: 8,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            backgroundColor: "rgba(0,0,0,0.9)",
            titleColor: "white",
            bodyColor: "white",
            borderColor: "#a855f7",
            borderWidth: 1,
          },
        },
        scales: {
          y: {
            beginAtZero: true,
            grid: { color: "rgba(255,255,255,0.08)" },
            ticks: { color: "rgba(255,255,255,0.7)" },
          },
          x: {
            grid: { color: "rgba(255,255,255,0.08)" },
            ticks: { color: "rgba(255,255,255,0.7)" },
          },
        },
        animation: {
          duration: 2000,
          easing: "easeInOutQuart",
        },
      },
    });
  }

  async connectWebSocket() {
    this.ws = new WebSocket(`wss://${window.location.host}/api/ws/stats`);

    this.ws.onmessage = (event) => {
      const stats = JSON.parse(event.data);
      this.updateStats(stats);
      this.updateCharts(stats);
      this.renderTopEmojis(stats.top_emojis);
      this.renderChatControls(stats.recent_chats);
      this.renderActivity(stats.recent_logs);
    };

    this.ws.onclose = () => {
      setTimeout(() => this.connectWebSocket(), 3000);
    };
  }

  async loadInitialData() {
    const res = await fetch(`/api/stats?owner_id=${this.ownerId}`);
    const stats = await res.json();
    this.updateStats(stats);
  }

  animateCounter(element, target, suffix = "") {
    const el =
      document.querySelector(`[data-target="${element}"]`) ||
      document.getElementById(element);
    if (!el) return;

    const start = parseInt(el.textContent) || 0;
    const duration = 2000;
    const startTime = performance.now();

    const update = (time) => {
      const elapsed = time - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easeProgress = 1 - Math.pow(1 - progress, 3);
      el.textContent =
        Math.floor(easeProgress * target).toLocaleString() + suffix;

      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  }

  updateStats(stats) {
    this.animateCounter("total_reactions", stats.total_reactions);
    this.animateCounter("active_chats", stats.active_chats);
    this.animateCounter("uptime", stats.uptime, "%");

    document.querySelector('[data-rate="reactions"]').textContent =
      `${(stats.total_reactions / 3600).toFixed(1)}/sec`;
    document.querySelector('[data-rate="chats"]').textContent =
      `+${stats.active_chats} active`;
  }

  renderTopEmojis(emojis) {
    const container = document.getElementById("topEmojis");
    container.innerHTML = Object.entries(emojis)
      .slice(0, 12)
      .map(
        ([emoji, count], i) => `
            <div class="emoji-item group relative p-6 rounded-3xl backdrop-blur-xl bg-white/10 border border-white/20 hover:bg-white/20 transition-all cursor-pointer hover:scale-110 hover:-rotate-3" 
                 style="animation-delay: ${i * 50}ms">
                <div class="text-5xl mb-4 group-hover:scale-110 transition-transform">${emoji}</div>
                <div class="text-2xl font-black text-white drop-shadow-lg">${count}</div>
                <div class="absolute -inset-2 bg-gradient-to-r from-purple-500/30 to-pink-500/30 rounded-3xl -z-10 opacity-0 group-hover:opacity-100 transition-all blur-xl"></div>
            </div>
        `,
      )
      .join("");
  }

  renderChatControls(chats) {
    const container = document.getElementById("chatControls");
    container.innerHTML =
      chats
        .slice(0, 8)
        .map(
          (chat) => `
            <div class="chat-control flex items-center justify-between p-6 rounded-3xl backdrop-blur-xl bg-white/5 hover:bg-white/10 border border-white/15 transition-all group">
                <div class="flex items-center space-x-4">
                    <div class="w-14 h-14 rounded-2xl flex items-center justify-center text-2xl font-bold ${
                      chat.enabled
                        ? "bg-gradient-to-r from-emerald-500 to-teal-500 text-white"
                        : "bg-gradient-to-r from-gray-600 to-gray-800 text-gray-400"
                    }">
                        ${chat.enabled ? "✓" : "⏸"}
                    </div>
                    <div>
                        <p class="font-bold text-lg">${chat.chat_id > 0 ? "📢" : "💬"} Chat ${chat.chat_id}</p>
                        <p class="text-gray-400 text-sm">${chat.emojis?.slice(0, 3).join(" ")}${chat.emojis?.length > 3 ? "..." : ""}</p>
                    </div>
                </div>
                <button class="px-6 py-3 rounded-2xl font-bold text-sm transition-all ${
                  chat.enabled
                    ? "bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 text-white shadow-lg hover:shadow-xl"
                    : "bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 text-white shadow-lg hover:shadow-xl"
                }" onclick="dashboard.toggleChat(${chat.chat_id}, ${!chat.enabled})">
                    ${chat.enabled ? "PAUSE" : "RESUME"}
                </button>
            </div>
        `,
        )
        .join("") ||
      '<p class="text-gray-500 text-center py-12">No chats yet 🚀</p>';
  }

  renderActivity(logs) {
    const container = document.getElementById("recentActivity");
    container.innerHTML =
      logs
        .slice(0, 12)
        .map((log) => {
          const time = new Date(log.timestamp * 1000).toLocaleTimeString();
          const icon =
            log.type === "reaction" ? "emoji_emotions" : "error_outline";
          const color =
            log.type === "reaction" ? "text-emerald-400" : "text-red-400";

          return `
                <div class="activity-item flex items-center space-x-4 p-4 rounded-2xl backdrop-blur-sm bg-white/5 border-l-4 border-emerald-400 hover:bg-white/10 transition-all">
                    <div class="w-10 h-10 rounded-2xl bg-gradient-to-r from-emerald-500/20 to-teal-500/20 flex items-center justify-center flex-shrink-0">
                        <i class="material-icons-outlined text-emerald-400 text-lg">${icon}</i>
                    </div>
                    <div class="flex-1 min-w-0">
                        <p class="font-medium truncate text-white">${log.error || `Reacted with ${log.emojis?.join(", ") || "👍"}`}</p>
                        <p class="text-xs text-gray-400 mt-1 flex items-center justify-between">
                            <span>${time}</span>
                            <span>Chat ${log.chat_id || "N/A"}</span>
                        </p>
                    </div>
                </div>
            `;
        })
        .join("") ||
      '<p class="text-gray-500 text-center py-12">No recent activity</p>';
  }

  async toggleChat(chatId, enable) {
    await fetch(`/api/chat/${chatId}/toggle?owner_id=${this.ownerId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ enabled: enable }),
    });
    // Refresh data
    this.loadInitialData();
  }

  updateCharts(stats) {
    if (!this.charts.reactions) return;

    const now = new Date();
    this.charts.reactions.data.labels.push(now.toLocaleTimeString());
    this.charts.reactions.data.datasets[0].data.push(stats.total_reactions);

    if (this.charts.reactions.data.labels.length > 24) {
      this.charts.reactions.data.labels.shift();
      this.charts.reactions.data.datasets[0].data.shift();
    }

    this.charts.reactions.update("none");
  }

  hideLoading() {
    gsap.to("#loading", {
      opacity: 0,
      scale: 0.95,
      duration: 0.8,
      ease: "power3.inOut",
      onComplete: () => {
        document.getElementById("loading").style.display = "none";
      },
    });
  }
}

// Global dashboard instance
const dashboard = new UltraDashboard();

// Refresh button
document.getElementById("refresh-btn").addEventListener("click", () => {
  dashboard.loadInitialData();
  gsap.from(".stat-card", {
    scale: 0.95,
    opacity: 0.8,
    duration: 0.5,
    stagger: 0.1,
  });
});

// Resize handler
window.addEventListener("resize", () => {
  const canvas = document.getElementById("particles");
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});
