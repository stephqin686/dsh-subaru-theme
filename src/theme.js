/* SUBARU AWA / BLUE HOUR — wallpaper engine (no dependencies) */
function swBoot(css) {
  var D = document;
  if (window.__SW_DISPOSE__) { try { window.__SW_DISPOSE__(); } catch (e) {} }
  if (!D.body) {
    D.addEventListener('DOMContentLoaded', function () { swBoot(css); }, { once: true });
    return;
  }

  var WALL_HTML = ''
    + '<div class="sw-photo-wrap"><div class="sw-photo"></div></div>'
    + '<div class="sw-grade"></div>'
    + '<div class="sw-halo"></div>'
    + '<div class="sw-beam"></div>'
    + '<canvas class="sw-canvas" id="sw-dust"></canvas>'
    + '<div class="sw-spot"></div>'
    + '<div class="sw-vignette"></div>'
    + '<div class="sw-halftone"></div>'
    + '<div class="sw-grain"></div>'
    + '<div class="sw-type">'
    +   '<div class="sw-spine">TOGENASHI TOGEARI</div>'
    +   '<div class="sw-brush">ここにいたい</div>'
    + '</div>'
    + '<div class="sw-edge"></div>';

  var PLAYER_HTML = ''
    + '<div class="sw-face"></div>'
    + '<div class="sw-meta"><b>安和すばる</b><span>名もなき何もかも</span></div>'
    + '<div class="sw-eq"><i></i><i></i><i></i><i></i></div>'
    + '<button class="sw-toggle" type="button" aria-label="暂停动态壁纸" aria-pressed="false">'
    +   '<svg class="sw-pause" viewBox="0 0 10 10" aria-hidden="true"><rect x="1" y="1" width="2.6" height="8" rx=".8" fill="currentColor"/><rect x="6.4" y="1" width="2.6" height="8" rx=".8" fill="currentColor"/></svg>'
    +   '<svg class="sw-play" viewBox="0 0 10 10" aria-hidden="true"><path d="M2 1.4 8.6 5 2 8.6Z" fill="currentColor"/></svg>'
    + '</button>';

  var style = D.createElement('style');
  style.id = 'sw-style';
  style.textContent = css;
  D.head.appendChild(style);

  var wall = D.createElement('div');
  wall.id = 'sw-wall';
  wall.className = 'sw-wall';
  wall.setAttribute('aria-hidden', 'true');
  wall.innerHTML = WALL_HTML;

  var player = D.createElement('div');
  player.id = 'sw-player';
  player.className = 'sw-player';
  player.setAttribute('role', 'group');
  player.setAttribute('aria-label', '安和昴动态壁纸');
  player.innerHTML = PLAYER_HTML;

  D.body.appendChild(wall);
  D.body.appendChild(player);

  var rootEl = D.documentElement;
  var body = D.body;

  /* ---- force the night palette ---- */
  var hadDark = body.hasAttribute('data-ds-dark-theme');
  if (!hadDark) body.setAttribute('data-ds-dark-theme', '');
  var darkObserver = new MutationObserver(function () {
    if (!body.hasAttribute('data-ds-dark-theme')) body.setAttribute('data-ds-dark-theme', '');
  });
  darkObserver.observe(body, { attributes: true, attributeFilter: ['data-ds-dark-theme'] });

  /* ---- pause state ---- */
  var reduce = false;
  try { reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) {}
  var stored = null;
  try { stored = window.localStorage.getItem('dsh-subaru-paused'); } catch (e) {}
  var paused = stored === null ? reduce : stored === '1';

  var toggle = player.querySelector('.sw-toggle');
  function syncToggle() {
    if (paused) rootEl.setAttribute('data-sw-paused', '');
    else rootEl.removeAttribute('data-sw-paused');
    toggle.setAttribute('aria-pressed', paused ? 'true' : 'false');
    var label = paused ? '播放动态壁纸' : '暂停动态壁纸';
    toggle.setAttribute('aria-label', label);
    toggle.title = label;
  }
  syncToggle();

  /* ---- canvas dust / bokeh ---- */
  var canvas = wall.querySelector('#sw-dust');
  var ctx = canvas.getContext('2d', { alpha: true });
  var DPR = Math.min(window.devicePixelRatio || 1, 1.5);
  var VW = 0, VH = 0;

  var BOKEH = [];
  var DUST = [];
  var COLORS = ['#9fe8ff', '#d6ff8f', '#ffd9a0', '#b9a6ff', '#bfffe0'];

  function rnd(a, b) { return a + Math.random() * (b - a); }

  function seed() {
    BOKEH = [];
    DUST = [];
    var i;
    for (i = 0; i < 26; i++) {
      BOKEH.push({
        x: Math.random(), y: Math.random(),
        r: rnd(2.2, 7.4), a: rnd(.035, .13),
        vy: rnd(.0018, .0055), drift: rnd(.0008, .0026),
        ph: rnd(0, 6.283), tw: rnd(.35, 1.1),
        s: rnd(.55, 1.35),
        c: COLORS[(Math.random() * COLORS.length) | 0]
      });
    }
    for (i = 0; i < 54; i++) {
      DUST.push({
        x: Math.random(), y: Math.random(),
        r: rnd(.5, 1.5), a: rnd(.08, .30),
        vy: rnd(.004, .012), drift: rnd(.002, .006),
        ph: rnd(0, 6.283), tw: rnd(.6, 2.2),
        c: Math.random() < .55 ? '#d8ffe8' : (Math.random() < .5 ? '#ffe2ad' : '#a9d8ff')
      });
    }
  }
  seed();

  function resize() {
    VW = window.innerWidth;
    VH = window.innerHeight;
    DPR = Math.min(window.devicePixelRatio || 1, 1.5);
    canvas.width = Math.max(1, Math.floor(VW * DPR));
    canvas.height = Math.max(1, Math.floor(VH * DPR));
    canvas.style.width = VW + 'px';
    canvas.style.height = VH + 'px';
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0);
  }
  resize();

  function draw(t, dt) {
    if (!VW || !VH) return;
    ctx.clearRect(0, 0, VW, VH);
    ctx.globalCompositeOperation = 'lighter';
    var i, p, x, y, a;

    for (i = 0; i < BOKEH.length; i++) {
      p = BOKEH[i];
      p.y -= p.vy * dt;
      p.x += Math.sin(t * .00016 * p.s + p.ph) * p.drift * dt;
      if (p.y < -.06) { p.y = 1.06; p.x = Math.random(); }
      if (p.x < -.06) p.x = 1.06;
      if (p.x > 1.06) p.x = -.06;
      x = p.x * VW; y = p.y * VH;
      a = p.a * (.62 + .38 * Math.sin(t * .001 * p.tw + p.ph));
      if (a <= .004) continue;
      ctx.globalAlpha = a;
      ctx.fillStyle = p.c;
      ctx.shadowColor = p.c;
      ctx.shadowBlur = 18 * p.s;
      ctx.beginPath();
      ctx.arc(x, y, p.r * p.s, 0, 6.2832);
      ctx.fill();
    }

    ctx.shadowBlur = 0;
    for (i = 0; i < DUST.length; i++) {
      p = DUST[i];
      p.y -= p.vy * dt;
      p.x += Math.sin(t * .00024 + p.ph) * p.drift * dt;
      if (p.y < -.03) { p.y = 1.03; p.x = Math.random(); }
      if (p.x < 0) p.x = 1;
      if (p.x > 1) p.x = 0;
      a = p.a * (.55 + .45 * Math.sin(t * .0013 * p.tw + p.ph));
      if (a <= .01) continue;
      ctx.globalAlpha = a;
      ctx.fillStyle = p.c;
      ctx.beginPath();
      ctx.arc(p.x * VW, p.y * VH, p.r, 0, 6.2832);
      ctx.fill();
    }

    ctx.globalAlpha = 1;
    ctx.globalCompositeOperation = 'source-over';
  }

  /* ---- pointer parallax + follow spot ---- */
  var px = 0, py = 0, tpx = 0, tpy = 0;
  var sx = VW * .64, sy = VH * .34, tsx = sx, tsy = sy;

  function onPointer(e) {
    var nx = e.clientX / Math.max(1, VW);
    var ny = e.clientY / Math.max(1, VH);
    tpx = (nx - .5) * 2;
    tpy = (ny - .5) * 2;
    tsx = e.clientX; tsy = e.clientY;
  }
  function onLeave() {
    tpx = 0; tpy = 0; tsx = VW * .64; tsy = VH * .34;
  }
  window.addEventListener('pointermove', onPointer, { passive: true });
  window.addEventListener('pointerleave', onLeave, { passive: true });

  /* ---- animation loop ---- */
  var raf = 0;
  var last = 0;
  var lastBeat = -1;
  var BPM = 104;

  function frame(now) {
    raf = 0;
    if (paused) return;
    if (!last) last = now;
    var dt = Math.min(48, now - last) / 16.667;
    last = now;

    px += (tpx - px) * .045;
    py += (tpy - py) * .045;
    sx += (tsx - sx) * .10;
    sy += (tsy - sy) * .10;

    if (Math.abs(px) > .001 || Math.abs(py) > .001) {
      rootEl.style.setProperty('--sw-px', px.toFixed(3));
      rootEl.style.setProperty('--sw-py', py.toFixed(3));
    }
    rootEl.style.setProperty('--sw-sx', sx.toFixed(1) + 'px');
    rootEl.style.setProperty('--sw-sy', sy.toFixed(1) + 'px');

    var beat = Math.pow(1 - ((now / 1000 * BPM / 60) % 1), 5);
    if (Math.abs(beat - lastBeat) > .015) {
      rootEl.style.setProperty('--sw-beat', beat.toFixed(3));
      lastBeat = beat;
    }

    draw(now, dt);
    raf = requestAnimationFrame(frame);
  }

  function start() {
    if (raf || paused) return;
    last = 0;
    raf = requestAnimationFrame(frame);
  }
  function stop() {
    if (raf) cancelAnimationFrame(raf);
    raf = 0;
  }

  toggle.addEventListener('click', function () {
    paused = !paused;
    try { window.localStorage.setItem('dsh-subaru-paused', paused ? '1' : '0'); } catch (e) {}
    syncToggle();
    if (paused) stop();
    else start();
  });

  var onResize = function () { resize(); if (paused) draw(performance.now(), 1); };
  window.addEventListener('resize', onResize, { passive: true });

  var onVis = function () {
    if (D.hidden) stop();
    else start();
  };
  D.addEventListener('visibilitychange', onVis);

  if (paused) draw(performance.now(), 1);
  else start();

  /* ---- cleanup ---- */
  function dispose() {
    stop();
    darkObserver.disconnect();
    window.removeEventListener('pointermove', onPointer);
    window.removeEventListener('pointerleave', onLeave);
    window.removeEventListener('resize', onResize);
    D.removeEventListener('visibilitychange', onVis);
    if (style.parentNode) style.parentNode.removeChild(style);
    if (wall.parentNode) wall.parentNode.removeChild(wall);
    if (player.parentNode) player.parentNode.removeChild(player);
    rootEl.removeAttribute('data-sw-paused');
    rootEl.style.removeProperty('--sw-px');
    rootEl.style.removeProperty('--sw-py');
    rootEl.style.removeProperty('--sw-sx');
    rootEl.style.removeProperty('--sw-sy');
    rootEl.style.removeProperty('--sw-beat');
    if (!hadDark && body.hasAttribute('data-ds-dark-theme')) body.removeAttribute('data-ds-dark-theme');
    window.__SW_DISPOSE__ = null;
  }
  window.__SW_DISPOSE__ = dispose;
  return dispose;
}
