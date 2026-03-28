/**
 * 結果表示
 */

import { ELEMENTS, QUALITIES, PLANETS, POINTS, DERIVED_POINTS } from '../engine/constants.js';
import { formatDegMin, formatPosition, getLunarPhase } from '../engine/utils.js';

/**
 * サマリーグリッドを表示
 */
export function renderSummary(bodies, houseData, lunarPhase) {
  const grid = document.getElementById('summary-grid');
  if (!grid) return;

  const items = [
    { label: '太陽', value: `${bodies.sun?.sign?.symbol || ''} ${bodies.sun?.sign?.nameJp || ''}` },
    { label: '月', value: `${bodies.moon?.sign?.symbol || ''} ${bodies.moon?.sign?.nameJp || ''}` },
    { label: 'ASC', value: `${houseData.angles?.ascendant?.sign?.symbol || ''} ${houseData.angles?.ascendant?.sign?.nameJp || ''}` },
    { label: 'MC', value: `${houseData.angles?.mc?.sign?.symbol || ''} ${houseData.angles?.mc?.sign?.nameJp || ''}` },
    { label: '月相', value: lunarPhase?.nameJp || '' },
  ];

  grid.innerHTML = items.map(item => `
    <div class="summary-item">
      <div class="label">${item.label}</div>
      <div class="value">${item.value}</div>
    </div>
  `).join('');
}

/**
 * 天体テーブルを表示
 */
export function renderPlanets(bodies, houseData, dignities) {
  const tbody = document.querySelector('#planets-table tbody');
  if (!tbody) return;

  // 表示順序: 主要天体 → 小惑星 → ノード/リリス → 派生
  const order = [
    'sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn',
    'uranus', 'neptune', 'pluto', 'chiron',
    'ceres', 'pallas', 'juno', 'vesta',
    'mean_node', 'true_node', 'mean_south_node', 'true_south_node',
    'mean_lilith', 'true_lilith',
  ];

  const rows = [];
  for (const key of order) {
    const b = bodies[key];
    if (!b) continue;

    const house = b._house || '';
    const dignity = dignities[key];
    const dignityHtml = dignity
      ? `<span class="${dignity.score > 0 ? 'dignity-positive' : 'dignity-negative'}">${dignity.dignityJp}</span>`
      : '';

    rows.push(`
      <tr>
        <td>${b.symbol || ''}</td>
        <td>${b.nameJp || b.name}</td>
        <td>${b.sign?.symbol || ''} ${b.sign?.nameJp || ''}</td>
        <td>${formatDegMin(b.degreeInSign)}</td>
        <td>${house}</td>
        <td class="${b.retrograde ? 'retrograde' : ''}">${
          b.speed != null ? (b.retrograde ? 'R ' : '') + (Math.abs(b.speed)).toFixed(2) + '°/d' : ''
        }</td>
        <td>${dignityHtml}</td>
      </tr>
    `);
  }

  tbody.innerHTML = rows.join('');
}

/**
 * ハウステーブルを表示
 */
export function renderHouses(houseData) {
  const tbody = document.querySelector('#houses-table tbody');
  if (!tbody) return;

  const rows = houseData.cusps.map(c => `
    <tr>
      <td>${c.house}${c.house === 1 ? ' (ASC)' : c.house === 10 ? ' (MC)' : ''}</td>
      <td>${c.sign?.symbol || ''} ${c.sign?.nameJp || ''}</td>
      <td>${formatDegMin(c.degreeInSign)}</td>
    </tr>
  `);

  tbody.innerHTML = rows.join('');
}

/**
 * アスペクトテーブルを表示
 */
export function renderAspects(aspects) {
  const tbody = document.querySelector('#aspects-table tbody');
  if (!tbody) return;

  const rows = aspects.map(a => {
    const orbClass = a.orb < 1 ? 'style="color:var(--accent)"' : a.orb < 3 ? '' : 'style="color:var(--text-dim)"';
    const movementJp = a.movement === 'applying' ? '接近' : a.movement === 'separating' ? '分離' : '静止';
    return `
      <tr>
        <td>${a.body1.nameJp || a.body1.name}</td>
        <td>${a.symbol} ${a.aspectNameJp} (${a.angle}°)</td>
        <td>${a.body2.nameJp || a.body2.name}</td>
        <td ${orbClass}>${a.orb}°</td>
        <td>${movementJp}</td>
      </tr>
    `;
  });

  tbody.innerHTML = rows.join('');
}

/**
 * エレメント・クオリティバランスを表示
 */
export function renderBalance(bodies) {
  const section = document.getElementById('balance-section');
  if (!section) return;

  // 主要10天体のみカウント
  const mainKeys = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto'];
  const elementCount = { fire: 0, earth: 0, air: 0, water: 0 };
  const qualityCount = { cardinal: 0, fixed: 0, mutable: 0 };

  for (const key of mainKeys) {
    const b = bodies[key];
    if (!b?.sign) continue;
    const el = b.sign.element;
    const qu = b.sign.quality;
    if (el in elementCount) elementCount[el]++;
    if (qu in qualityCount) qualityCount[qu]++;
  }

  const total = mainKeys.length;

  let html = '<div style="margin-bottom:12px"><strong style="font-size:0.75rem;color:var(--text-dim)">ELEMENTS</strong></div>';
  for (const [key, count] of Object.entries(elementCount)) {
    const pct = (count / total * 100).toFixed(0);
    html += `
      <div class="balance-row">
        <div class="balance-label">${ELEMENTS[key].nameJp}</div>
        <div class="balance-bar"><div class="balance-fill ${key}" style="width:${pct}%"></div></div>
        <div class="balance-count">${count}</div>
      </div>
    `;
  }

  html += '<div style="margin:12px 0 12px"><strong style="font-size:0.75rem;color:var(--text-dim)">QUALITIES</strong></div>';
  for (const [key, count] of Object.entries(qualityCount)) {
    const pct = (count / total * 100).toFixed(0);
    html += `
      <div class="balance-row">
        <div class="balance-label">${QUALITIES[key].nameJp}</div>
        <div class="balance-bar"><div class="balance-fill ${key}" style="width:${pct}%"></div></div>
        <div class="balance-count">${count}</div>
      </div>
    `;
  }

  section.innerHTML = html;
}

/**
 * 月相を表示
 */
export function renderLunarPhase(lunarPhase) {
  const section = document.getElementById('lunar-section');
  if (!section) return;

  const moonEmoji = {
    new_moon: '🌑', waxing_crescent: '🌒', first_quarter: '🌓',
    waxing_gibbous: '🌔', full_moon: '🌕', waning_gibbous: '🌖',
    last_quarter: '🌗', waning_crescent: '🌘',
  };

  section.innerHTML = `
    <div style="text-align:center;padding:8px">
      <div style="font-size:2rem">${moonEmoji[lunarPhase.key] || '🌙'}</div>
      <div style="margin-top:4px">${lunarPhase.nameJp}</div>
      <div style="font-size:0.75rem;color:var(--text-dim)">Sun-Moon angle: ${lunarPhase.angle}°</div>
    </div>
  `;
}

/**
 * 追加感受点テーブルを表示
 */
export function renderExtraPoints(extraPoints) {
  const tbody = document.querySelector('#extra-table tbody');
  if (!tbody) return;

  const rows = [];
  for (const [key, p] of Object.entries(extraPoints)) {
    if (key === 'is_daytime') continue;
    if (!p || !p.sign) continue;
    rows.push(`
      <tr>
        <td>${p.symbol || ''}</td>
        <td>${p.nameJp || p.name}</td>
        <td>${p.sign?.symbol || ''} ${p.sign?.nameJp || ''}</td>
        <td>${formatDegMin(p.degreeInSign)}</td>
      </tr>
    `);
  }

  tbody.innerHTML = rows.join('');
}

/**
 * JSONを表示
 */
export function renderJSON(data) {
  const output = document.getElementById('json-output');
  if (!output) return;
  output.textContent = JSON.stringify(data, null, 2);
}
