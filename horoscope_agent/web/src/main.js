/**
 * メインエントリポイント
 * WASM初期化 → フォーム → 計算 → 表示
 */

import { initSwe, calcJulDay, closeSwe } from './engine/sweph.js';
import { calculateAllBodies } from './engine/planets.js';
import { calculateHouses } from './engine/houses.js';
import { calculateAllAspects } from './engine/aspects.js';
import { calculateExtraPoints } from './engine/points.js';
import { calculateAllDignities } from './engine/dignity.js';
import { findHouse, getLunarPhase } from './engine/utils.js';
import { initCitySelect, getFormValues } from './ui/form.js';
import { initChatUI } from './chat/chat-ui.js';
import {
  renderSummary, renderPlanets, renderHouses,
  renderAspects, renderBalance, renderLunarPhase,
  renderExtraPoints, renderJSON,
} from './ui/display.js';
import { drawChart } from './chart/svg.js';

// --- 状態管理 ---
let lastResult = null;

function setStatus(msg, type = 'loading') {
  const el = document.getElementById('status');
  el.textContent = msg;
  el.className = type;
}

function clearStatus() {
  const el = document.getElementById('status');
  el.className = '';
  el.style.display = 'none';
}

// --- メイン計算 ---
async function calculate() {
  const values = getFormValues();
  if (!values) {
    setStatus('入力値を確認してください', 'error');
    return;
  }

  const btn = document.getElementById('calc-btn');
  btn.disabled = true;
  setStatus('計算中...', 'loading');

  try {
    // Julian Day
    const jd = calcJulDay(values.year, values.month, values.day, values.hour, values.minute, values.tz);

    // 全天体位置
    const bodies = calculateAllBodies(jd);

    // ハウス
    const houseData = calculateHouses(jd, values.lat, values.lng, values.houseSystem);
    if (houseData.error) {
      setStatus(`ハウス計算エラー: ${houseData.error}`, 'error');
      btn.disabled = false;
      return;
    }

    // 天体にハウス情報を付与
    for (const [key, body] of Object.entries(bodies)) {
      if (houseData.rawCusps) {
        body._house = findHouse(body.longitude, houseData.rawCusps);
      }
    }

    // アスペクト
    const aspects = calculateAllAspects(bodies);

    // 追加感受点
    const extraPoints = calculateExtraPoints(bodies, houseData.angles);

    // 品位
    const dignities = calculateAllDignities(bodies);

    // 月相
    const lunarPhase = getLunarPhase(bodies.sun?.longitude || 0, bodies.moon?.longitude || 0);

    // 結果保存
    lastResult = {
      input: values,
      julianDay: jd,
      bodies,
      houses: houseData,
      aspects,
      extraPoints,
      dignities,
      lunarPhase,
    };

    // --- 描画 ---
    renderSummary(bodies, houseData, lunarPhase);
    renderPlanets(bodies, houseData, dignities);
    renderHouses(houseData);
    renderAspects(aspects);
    renderBalance(bodies);
    renderLunarPhase(lunarPhase);
    renderExtraPoints(extraPoints);

    // SVGチャート（フィルター付き）
    redrawChart();

    // 表示
    document.getElementById('results').classList.add('visible');
    document.getElementById('export-btn').style.display = 'inline-block';
    document.getElementById('copy-btn').style.display = 'inline-block';
    document.getElementById('share-panel').classList.add('visible');

    // AI鑑定ボタンを表示
    document.getElementById('chat-start-area').style.display = 'block';

    setStatus(`完了 — JD ${jd.toFixed(6)}`, 'success');
    setTimeout(clearStatus, 3000);

  } catch (e) {
    console.error(e);
    setStatus(`エラー: ${e.message}`, 'error');
  } finally {
    btn.disabled = false;
  }
}

// --- チャートフィルター & 再描画 ---
function getChartFilterOptions() {
  const enabled = new Set();
  document.querySelectorAll('#chart-filters input[data-aspect]').forEach(cb => {
    if (cb.checked) enabled.add(cb.dataset.aspect);
  });
  const maxOrb = parseInt(document.getElementById('orb-range')?.value || '5');
  return { enabledAspects: enabled, maxAspectOrb: maxOrb };
}

function redrawChart() {
  if (!lastResult) return;
  const chartContainer = document.getElementById('chart-container');
  chartContainer.innerHTML = '';
  const opts = getChartFilterOptions();
  const svgEl = drawChart(lastResult.bodies, lastResult.houses, lastResult.aspects, opts);
  chartContainer.appendChild(svgEl);
}

function initChartFilters() {
  // アスペクトチェックボックス
  document.querySelectorAll('#chart-filters input[data-aspect]').forEach(cb => {
    cb.addEventListener('change', redrawChart);
  });
  // オーブスライダー
  const orbRange = document.getElementById('orb-range');
  const orbValue = document.getElementById('orb-value');
  if (orbRange) {
    orbRange.addEventListener('input', () => {
      orbValue.textContent = orbRange.value + '°';
      redrawChart();
    });
  }
}

// --- セクション折りたたみ ---
function initCollapsible() {
  document.querySelectorAll('.section-header').forEach(header => {
    header.addEventListener('click', () => {
      const body = header.nextElementSibling;
      if (body) body.classList.toggle('collapsed');
    });
  });
}

// --- JSON エクスポート ---
function getCleanJSON() {
  if (!lastResult) return null;
  return JSON.parse(JSON.stringify(lastResult, (key, val) => {
    if (key === '_house') return val;
    return val;
  }));
}

function exportJSON() {
  const clean = getCleanJSON();
  if (!clean) return;

  const jsonSection = document.getElementById('json-section');
  if (jsonSection.style.display === 'none') {
    jsonSection.style.display = 'block';
    renderJSON(clean);
  } else {
    jsonSection.style.display = 'none';
  }
}

async function copyJSON() {
  const clean = getCleanJSON();
  if (!clean) return;

  const text = JSON.stringify(clean, null, 2);
  try {
    await navigator.clipboard.writeText(text);
    const btn = document.getElementById('copy-btn');
    const orig = btn.textContent;
    btn.textContent = 'コピーしました';
    setTimeout(() => { btn.textContent = orig; }, 1500);
  } catch {
    // fallback
    const ta = document.createElement('textarea');
    ta.value = JSON.stringify(clean, null, 2);
    document.body.appendChild(ta);
    ta.select();
    document.execCommand('copy');
    document.body.removeChild(ta);
  }
}

// --- データ保存 (localStorage) ---
const STORAGE_KEY = 'horoscope_saved_charts';

function getSavedCharts() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
  } catch { return []; }
}

function saveChart() {
  if (!lastResult) return;

  const consent = document.getElementById('share-consent').checked;
  const input = lastResult.input;
  const bodies = lastResult.bodies;

  const entry = {
    id: Date.now(),
    name: input.name || 'Chart',
    year: input.year,
    month: input.month,
    day: input.day,
    hour: input.hour,
    minute: input.minute,
    city: document.getElementById('city').value,
    lat: input.lat,
    lng: input.lng,
    tz: input.tz,
    houseSystem: input.houseSystem,
    sunSign: bodies.sun?.sign?.nameJp || '',
    moonSign: bodies.moon?.sign?.nameJp || '',
    ascSign: lastResult.houses?.angles?.ascendant?.sign?.nameJp || '',
    youtubeConsent: consent,
    savedAt: new Date().toISOString(),
  };

  const charts = getSavedCharts();
  charts.unshift(entry);
  // 最大50件
  if (charts.length > 50) charts.length = 50;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(charts));

  const status = document.getElementById('save-status');
  status.textContent = '保存しました';
  setTimeout(() => { status.textContent = ''; }, 2000);

  renderSavedList();
}

function loadChart(entry) {
  document.getElementById('name').value = entry.name || '';
  document.getElementById('year').value = entry.year;
  document.getElementById('month').value = entry.month;
  document.getElementById('day').value = entry.day;
  document.getElementById('hour').value = entry.hour;
  document.getElementById('minute').value = entry.minute;
  document.getElementById('lat').value = entry.lat;
  document.getElementById('lng').value = entry.lng;
  document.getElementById('tz').value = entry.tz;
  if (entry.city) document.getElementById('city').value = entry.city;
  if (entry.houseSystem) document.getElementById('house-system').value = entry.houseSystem;
  document.getElementById('share-consent').checked = entry.youtubeConsent || false;

  // 自動計算
  calculate();
}

function deleteChart(id) {
  const charts = getSavedCharts().filter(c => c.id !== id);
  localStorage.setItem(STORAGE_KEY, JSON.stringify(charts));
  renderSavedList();
}

function renderSavedList() {
  const container = document.getElementById('saved-list');
  if (!container) return;

  const charts = getSavedCharts();
  if (charts.length === 0) {
    container.innerHTML = '';
    return;
  }

  let html = '<div class="saved-list-title">保存済みデータ</div>';
  for (const c of charts) {
    const label = c.youtubeConsent ? ' ▶' : '';
    html += `
      <div class="saved-item" data-id="${c.id}">
        <span class="saved-name" data-action="load">${c.name}${label}</span>
        <span class="saved-sign">${c.sunSign} / ${c.moonSign} / ASC ${c.ascSign}</span>
        <span class="saved-delete" data-action="delete" title="削除">&times;</span>
      </div>
    `;
  }
  container.innerHTML = html;

  // イベント
  container.querySelectorAll('.saved-item').forEach(item => {
    const id = parseInt(item.dataset.id);
    item.querySelector('[data-action="load"]')?.addEventListener('click', () => {
      const chart = getSavedCharts().find(c => c.id === id);
      if (chart) loadChart(chart);
    });
    item.querySelector('[data-action="delete"]')?.addEventListener('click', (e) => {
      e.stopPropagation();
      deleteChart(id);
    });
  });
}

// --- 初期化 ---
async function init() {
  setStatus('Swiss Ephemeris 読込中...', 'loading');

  try {
    await initSwe();
    setStatus('準備完了', 'success');
    setTimeout(clearStatus, 2000);

    // フォーム初期化
    initCitySelect();
    initCollapsible();
    initChartFilters();

    // ボタン有効化
    const calcBtn = document.getElementById('calc-btn');
    calcBtn.disabled = false;
    calcBtn.addEventListener('click', calculate);

    document.getElementById('export-btn').addEventListener('click', exportJSON);
    document.getElementById('copy-btn').addEventListener('click', copyJSON);
    document.getElementById('save-btn').addEventListener('click', saveChart);

    // AI鑑定ボタン
    document.getElementById('chat-start-btn').addEventListener('click', () => {
      if (lastResult) initChatUI(lastResult);
    });

    // 保存済みリスト表示
    renderSavedList();

    // Enterキーで計算
    document.getElementById('birth-form').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') calculate();
    });

  } catch (e) {
    console.error(e);
    setStatus(`Swiss Ephemeris 読込失敗: ${e.message}`, 'error');
  }
}

init();
