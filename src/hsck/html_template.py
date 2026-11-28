"""独立 HTML 视频站模板（all.html）。

仅一个 HTML 文件、不依赖任何本地 js/css：框架（Vue3 / hls.js）通过 CDN 引入，
全部视频数据由生成器内联注入到 __APP_DATA__ 占位符处，可直接用 file:// 打开。
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light dark">
<title>Hsck 视频库 · 离线内置数据</title>
<script>
(function () {
  try {
    var t = localStorage.getItem('hsck-theme') || 'auto';
    if (t === 'light' || t === 'dark') document.documentElement.setAttribute('data-theme', t);
  } catch (e) {}
})();
</script>
<style>
:root{
  --bg:#f4f5f7; --panel:#ffffff; --panel-2:#eef0f3; --card:#ffffff;
  --text:#1f2329; --muted:#8a9099; --border:rgba(128,128,128,.18);
  --accent:#3b82f6; --accent-soft:rgba(59,130,246,.12);
  --shadow:0 1px 3px rgba(0,0,0,.08); --ov-bg:rgba(0,0,0,.5);
  --chip:#eef0f3; --skeleton:#e9ebef;
}
@media (prefers-color-scheme: dark){
  :root{
    --bg:#0e1014; --panel:#161a21; --panel-2:#1d222b; --card:#191e26;
    --text:#e7e9ec; --muted:#8b929c; --border:rgba(255,255,255,.12);
    --accent:#4b9bff; --accent-soft:rgba(75,155,255,.16);
    --shadow:0 1px 4px rgba(0,0,0,.5); --ov-bg:rgba(0,0,0,.72);
    --chip:#222831; --skeleton:#222831;
  }
}
:root[data-theme="light"]{
  --bg:#f4f5f7; --panel:#ffffff; --panel-2:#eef0f3; --card:#ffffff;
  --text:#1f2329; --muted:#8a9099; --border:rgba(128,128,128,.18);
  --accent:#3b82f6; --accent-soft:rgba(59,130,246,.12);
  --shadow:0 1px 3px rgba(0,0,0,.08); --ov-bg:rgba(0,0,0,.5);
  --chip:#eef0f3; --skeleton:#e9ebef;
}
:root[data-theme="dark"]{
  --bg:#0e1014; --panel:#161a21; --panel-2:#1d222b; --card:#191e26;
  --text:#e7e9ec; --muted:#8b929c; --border:rgba(255,255,255,.12);
  --accent:#4b9bff; --accent-soft:rgba(75,155,255,.16);
  --shadow:0 1px 4px rgba(0,0,0,.5); --ov-bg:rgba(0,0,0,.72);
  --chip:#222831; --skeleton:#222831;
}
*{box-sizing:border-box;}
html,body{margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.5;}
[v-cloak]{display:none;}
.header{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--panel);border-bottom:1px solid var(--border);box-shadow:var(--shadow);}
.brand{display:flex;flex-direction:column;justify-content:center;gap:1px;flex:none;line-height:1.2;}
.brand-title{font-weight:700;font-size:18px;}
.brand-sub{font-size:12px;color:var(--muted);}
.search{flex:1;display:flex;align-items:center;background:var(--panel-2);border:1px solid var(--border);border-radius:999px;padding:6px 14px;min-width:120px;}
.search input{flex:1;border:none;background:transparent;color:var(--text);outline:none;font-size:14px;}
.search .ic{color:var(--muted);margin-right:8px;}
.theme-seg{display:flex;border:1px solid var(--border);border-radius:8px;overflow:hidden;flex:none;}
.theme-seg button{background:transparent;border:none;color:var(--muted);padding:7px 10px;cursor:pointer;font-size:14px;}
.theme-seg button.active{background:var(--accent-soft);color:var(--accent);}
.layout{display:flex;align-items:flex-start;max-width:1400px;margin:0 auto;}
.sidebar{position:sticky;top:62px;width:200px;flex:none;padding:14px 10px;max-height:calc(100vh - 62px);overflow:auto;}
.cat{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:8px 12px;border-radius:8px;cursor:pointer;font-size:14px;color:var(--text);}
.cat:hover{background:var(--panel-2);}
.cat.active{background:var(--accent-soft);color:var(--accent);font-weight:600;}
.cat .cnt{font-size:12px;color:var(--muted);background:var(--chip);border-radius:999px;padding:1px 8px;}
.main{flex:1;min-width:0;padding:14px 16px 40px;}
.toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px;color:var(--muted);font-size:13px;flex-wrap:wrap;}
.grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:14px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;cursor:pointer;transition:transform .12s ease,box-shadow .12s ease;}
.card:hover{transform:translateY(-3px);box-shadow:var(--shadow);}
.thumb{position:relative;width:100%;aspect-ratio:16/10;background:var(--skeleton);overflow:hidden;}
.thumb img{width:100%;height:100%;object-fit:cover;display:block;}
.thumb .dur{position:absolute;right:6px;bottom:6px;background:rgba(0,0,0,.7);color:#fff;font-size:11px;padding:1px 5px;border-radius:4px;}
.thumb .badge-up{position:absolute;left:6px;bottom:6px;background:rgba(0,0,0,.7);color:#fff;font-size:11px;padding:1px 5px;border-radius:4px;}
.card .body{padding:8px 10px;}
.card .title{font-size:13px;font-weight:600;margin:0 0 6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:36px;}
.card .meta{display:flex;justify-content:space-between;align-items:center;font-size:12px;color:var(--muted);}
.card .meta .m-right{display:flex;gap:8px;align-items:center;}
.pager{display:flex;align-items:center;justify-content:center;gap:10px;margin-top:22px;flex-wrap:wrap;}
.pager button{background:var(--panel);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:7px 16px;cursor:pointer;}
.pager button:disabled{opacity:.4;cursor:not-allowed;}
.pager .pgin{display:flex;align-items:center;gap:6px;}
.pager input{width:70px;background:var(--panel-2);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:6px 8px;text-align:center;}
.pager .go{background:var(--accent);color:#fff;border:1px solid var(--accent);border-radius:8px;padding:6px 12px;cursor:pointer;}
.pager .go:hover{opacity:.9;}
.pager .pginfo{color:var(--muted);font-size:13px;min-width:96px;text-align:center;}
.empty{text-align:center;color:var(--muted);padding:60px 20px;}
.foot-note{text-align:center;color:var(--muted);font-size:12px;padding:14px 20px 4px;}
.player-modal{position:fixed;inset:0;z-index:50;background:var(--ov-bg);display:flex;align-items:center;justify-content:center;padding:24px;}
.player-box{width:min(1100px,96vw);background:var(--panel);border:1px solid var(--border);border-radius:12px;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.5);display:flex;flex-direction:column;}
.player-modal.web-full .player-box{width:100vw;height:100vh;border-radius:0;}
.p-head{display:flex;align-items:center;gap:10px;padding:10px 14px;border-bottom:1px solid var(--border);}
.p-head .t{font-weight:600;font-size:14px;flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.icon-btn{background:var(--panel-2);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:6px 10px;cursor:pointer;font-size:13px;flex:none;}
.icon-btn:hover{background:var(--accent-soft);color:var(--accent);}
.video-wrap{position:relative;background:#000;width:100%;aspect-ratio:16/9;}
.player-modal.web-full .video-wrap{aspect-ratio:auto;height:calc(100vh - 112px);}
.video-wrap video{width:100%;height:100%;display:block;background:#000;}
.loading{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;background:rgba(0,0,0,.45);font-size:14px;}
.p-ctrl{display:flex;align-items:center;gap:10px;padding:10px 14px;flex-wrap:wrap;}
.spd-row{display:flex;align-items:center;gap:6px;flex-wrap:wrap;}
.spd-label{font-size:13px;color:var(--muted);margin-right:2px;}
.spd{background:var(--panel-2);border:1px solid var(--border);color:var(--text);border-radius:8px;padding:5px 10px;cursor:pointer;font-size:13px;min-width:44px;text-align:center;}
.spd:hover{background:var(--accent-soft);color:var(--accent);}
.spd.active{background:var(--accent);color:#fff;border-color:var(--accent);}
.p-ctrl .sp{font-size:13px;color:var(--muted);}
.p-ctrl .grow{flex:1;}
@media (max-width:1100px){
  .grid{grid-template-columns:repeat(3,minmax(0,1fr));}
}
@media (max-width:760px){
  .sidebar{position:static;width:100%;max-height:none;display:flex;gap:8px;overflow-x:auto;padding:10px;}
  .layout{flex-direction:column;}
  .brand-sub{display:none;}
  .grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;}
}
</style>
</head>
<body>
<div id="app" v-cloak>
  <header class="header">
    <div class="brand">
      <div class="brand-title">Hsck 视频库</div>
      <div class="brand-sub">离线内置数据 · 共 {{ totalCount }} 条</div>
    </div>
    <div class="search">
      <span class="ic">🔍</span>
      <input v-model="query" @input="onSearch" placeholder="搜索视频标题…" autocomplete="off">
    </div>
    <div class="theme-seg">
      <button :class="{active:theme==='auto'}" @click="setTheme('auto')" title="跟随系统">🌗</button>
      <button :class="{active:theme==='light'}" @click="setTheme('light')" title="浅色">☀️</button>
      <button :class="{active:theme==='dark'}" @click="setTheme('dark')" title="深色">🌙</button>
    </div>
  </header>

  <div class="layout">
    <aside class="sidebar">
      <div class="cat" :class="{active:activeCat==='all'}" @click="selectCat('all')">
        <span>全部</span><span class="cnt">{{ totalCount }}</span>
      </div>
      <div class="cat" v-for="c in categories" :key="c.name" :class="{active:activeCat===c.name}" @click="selectCat(c.name)">
        <span>{{ c.name }}</span><span class="cnt">{{ c.count }}</span>
      </div>
    </aside>

    <main class="main">
      <div class="toolbar">
        <span>当前分类：<b>{{ activeCat==='all' ? '全部' : activeCat }}</b> · 共 {{ filtered.length }} 条</span>
        <span>第 {{ page }} / {{ totalPages }} 页</span>
      </div>

      <div class="grid" v-if="pageItems.length">
        <div class="card" v-for="it in pageItems" :key="it.vod_id" @click="goPlay(it)">
          <div class="thumb">
            <img :src="it.thumd" :alt="it.title" loading="lazy" @error="imgError">
            <span class="dur" v-if="it.time">{{ it.time }}</span>
            <span class="badge-up" v-if="activeCat==='all' && it.uptime">{{ it.uptime }}</span>
          </div>
          <div class="body">
            <p class="title">{{ it.title }}</p>
            <div class="meta">
              <span v-if="activeCat==='all'">{{ it.vod_type_name }}</span>
              <span v-else-if="it.uptime">🕒 {{ it.uptime }}</span>
              <span class="m-right">
                <span v-if="it.eye">👁 {{ fmtNum(it.eye) }}</span>
                <span v-if="it.heart">❤ {{ fmtNum(it.heart) }}</span>
              </span>
            </div>
          </div>
        </div>
      </div>
      <div class="empty" v-else>没有匹配的结果</div>

      <div class="pager" v-if="totalPages>1">
        <button @click="prev" :disabled="page<=1">上一页</button>
        <div class="pgin">
          <input type="number" v-model.number="jumpPage" min="1" :max="totalPages" @keyup.enter="gotoPage">
          <span style="color:var(--muted);font-size:13px;">/ {{ totalPages }}</span>
          <button class="go" @click="gotoPage">跳转</button>
        </div>
        <button @click="next" :disabled="page>=totalPages">下一页</button>
      </div>

      <div class="foot-note">生成于 {{ generated }} 共 {{ totalCount }} 条数据</div>
    </main>
  </div>

  <div class="player-modal" :class="{ 'web-full': webFull }" v-if="playing" @click.self="closePlayer">
    <div class="player-box">
      <div class="p-head">
        <div class="t">{{ playing.title }}</div>
        <button class="icon-btn" @click="toggleWebFull">{{ webFull ? '退出网页全屏' : '网页全屏' }}</button>
        <button class="icon-btn" @click="toggleOsFull">系统全屏</button>
        <button class="icon-btn" @click="closePlayer">关闭 ✕</button>
      </div>
      <div class="video-wrap">
        <video ref="video" controls playsinline @loadeddata="loading=false" @error="loading=false"></video>
        <div class="loading" v-if="loading">加载中…</div>
      </div>
      <div class="p-ctrl">
        <div class="spd-row">
          <span class="spd-label">倍速</span>
          <button class="spd" v-for="s in speeds" :key="s" :class="{active:speed===s}" @click="setSpeed(s)">{{ s }}x</button>
        </div>
        <span class="grow"></span>
        <span class="sp" v-if="playing.eye">👁 {{ fmtNum(playing.eye) }}</span>
        <span class="sp" v-if="playing.heart">❤ {{ fmtNum(playing.heart) }}</span>
        <span class="sp" v-if="playing.uptime">🕒 {{ playing.uptime }}</span>
      </div>
    </div>
  </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.prod.js"></script>
<script src="https://cdn.jsdelivr.net/npm/hls.js@1/dist/hls.min.js"></script>
<script>
if (typeof Vue === 'undefined') {
  document.getElementById('app').innerHTML =
    '<p style="padding:48px;text-align:center;color:#888">界面框架加载失败，请检查网络（需要能访问 cdn.jsdelivr.net）。</p>';
} else {
  const APP_DATA = __APP_DATA__;
  const GENERATED = "__GENERATED__";
  const { createApp } = Vue;

  const categoriesMap = {};
  for (const it of APP_DATA) {
    const t = it.vod_type_name || '未分类';
    categoriesMap[t] = (categoriesMap[t] || 0) + 1;
  }
  const categories = Object.keys(categoriesMap).map(t => ({ name: t, count: categoriesMap[t] }));

  createApp({
    data() {
      return {
        query: '',
        activeCat: 'all',
        page: 1,
        jumpPage: 1,
        perPage: 30,
        theme: document.documentElement.getAttribute('data-theme') || 'auto',
        playing: null,
        webFull: false,
        loading: true,
        speed: 1,
        speeds: [0.5, 0.75, 1, 1.25, 1.5, 2, 3],
        hls: null,
        categories,
        generated: GENERATED,
      };
    },
    computed: {
      totalCount() { return APP_DATA.length; },
      filtered() {
        let list = this.activeCat === 'all'
          ? APP_DATA
          : APP_DATA.filter(i => (i.vod_type_name || '未分类') === this.activeCat);
        const q = this.query.trim().toLowerCase();
        if (q) list = list.filter(i => (i.title || '').toLowerCase().includes(q));
        return list;
      },
      totalPages() { return Math.max(1, Math.ceil(this.filtered.length / this.perPage)); },
      pageItems() {
        const start = (this.page - 1) * this.perPage;
        return this.filtered.slice(start, start + this.perPage);
      },
    },
    watch: {
      filtered() { if (this.page > this.totalPages) this.page = this.totalPages; },
      playing(v) {
        document.body.style.overflow = v ? 'hidden' : '';
        if (!v) this.webFull = false;
      },
    },
    methods: {
      selectCat(c) { this.activeCat = c; this.page = 1; this.jumpPage = 1; },
      onSearch() { this.page = 1; this.jumpPage = 1; },
      gotoPage() {
        let p = Math.floor(Number(this.jumpPage) || 1);
        if (p < 1) p = 1;
        if (p > this.totalPages) p = this.totalPages;
        this.page = p;
        this.jumpPage = p;
        window.scrollTo({ top: 0, behavior: 'smooth' });
      },
      prev() { if (this.page > 1) { this.page--; this.jumpPage = this.page; } },
      next() { if (this.page < this.totalPages) { this.page++; this.jumpPage = this.page; } },
      setTheme(t) {
        this.theme = t;
        if (t === 'auto') document.documentElement.removeAttribute('data-theme');
        else document.documentElement.setAttribute('data-theme', t);
        try { localStorage.setItem('hsck-theme', t); } catch (e) {}
      },
      fmtNum(n) {
        n = Number(n) || 0;
        if (n >= 10000) return (n / 10000).toFixed(1) + '万';
        return String(n);
      },
      imgError(e) { e.target.style.visibility = 'hidden'; },
      goPlay(it) {
        if (this.hls) { this.hls.destroy(); this.hls = null; }
        this.loading = true;
        this.playing = it;
        this.speed = 1;
        this.$nextTick(() => {
          const v = this.$refs.video;
          if (!v) return;
          v.playbackRate = 1;
          const url = it.media;
          if (v.canPlayType('application/vnd.apple.mpegurl')) {
            v.src = url;
            v.play().catch(() => {});
          } else if (window.Hls && window.Hls.isSupported()) {
            this.hls = new window.Hls();
            this.hls.loadSource(url);
            this.hls.attachMedia(v);
            this.hls.on(window.Hls.Events.MANIFEST_PARSED, () => { v.play().catch(() => {}); });
            this.hls.on(window.Hls.Events.ERROR, (e, d) => { if (d && d.fatal) this.loading = false; });
          } else {
            v.src = url;
            v.play().catch(() => {});
          }
        });
      },
      closePlayer() {
        const v = this.$refs.video;
        if (v) v.pause();
        if (this.hls) { this.hls.destroy(); this.hls = null; }
        this.playing = null;
      },
      setSpeed(s) {
        this.speed = s;
        if (this.$refs.video) this.$refs.video.playbackRate = s;
      },
      toggleWebFull() { this.webFull = !this.webFull; },
      toggleOsFull() {
        const el = this.$refs.video;
        if (!document.fullscreenElement) { if (el.requestFullscreen) el.requestFullscreen(); }
        else { document.exitFullscreen(); }
      },
      onKey(e) {
        if (!this.playing) return;
        if (e.key === 'Escape') this.closePlayer();
        else if (e.key === ' ') { e.preventDefault(); const v = this.$refs.video; if (v) { v.paused ? v.play() : v.pause(); } }
        else if (e.key === 'f' || e.key === 'F') this.toggleWebFull();
        else if (e.key === 'm' || e.key === 'M') { const v = this.$refs.video; if (v) v.muted = !v.muted; }
      },
    },
    mounted() { window.addEventListener('keydown', this.onKey); },
    beforeUnmount() { window.removeEventListener('keydown', this.onKey); },
  }).mount('#app');
}
</script>
</body>
</html>
"""
