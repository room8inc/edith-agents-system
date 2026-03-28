/**
 * SVG ホロスコープチャート描画 v3
 */

import { SIGNS } from '../engine/constants.js';
import { normalizeDeg } from '../engine/utils.js';

const SVG_NS = 'http://www.w3.org/2000/svg';
const SIZE = 780;
const CX = SIZE / 2;
const CY = SIZE / 2;

// レイヤー半径
const R_OUTER = 330;        // 最外円
const R_SIGN_INNER = 290;   // サイン帯の内側
const R_SIGN_MID = 310;     // サイン記号
const R_PLANET = 245;       // 天体配置
const R_HOUSE_NUM = 170;    // ハウス番号
const R_ASPECT = 130;       // アスペクト線
const R_CENTER = 55;        // 中心円

const COLORS = {
  bg: '#0a0e1e',
  chartInner: '#101428',           // チャート内部（bgより少し明るい）
  signBand: 'rgba(180, 160, 100, 0.10)',   // サイン帯 — はっきり見える
  signBandAlt: 'rgba(100, 130, 200, 0.08)',
  ringStroke: 'rgba(220, 200, 140, 0.4)',  // 外円 — くっきり
  ringInner: 'rgba(220, 200, 140, 0.25)',
  signDivider: 'rgba(220, 200, 140, 0.25)',
  houseLine: 'rgba(220, 200, 140, 0.2)',        // 通常ハウス線 — 見える
  houseAngleLine: 'rgba(220, 200, 140, 0.6)',  // ASC/MC軸 — 目立つ
  houseNum: 'rgba(220, 200, 140, 0.7)',        // ハウス番号 — しっかり見える
  text: '#e8e0d0',
  textBright: '#f5f0e5',
  planetBg: '#0a0e1e',
  planetStroke: 'rgba(220, 200, 140, 0.5)',    // 天体枠 — 目立つ
  fire: '#f0a070',        // 彩度UP
  earth: '#b0d068',
  air: '#80d0e0',
  water: '#a0a0f0',
  conjunction: '#e0d098',
  opposition: '#f09090',
  trine: '#90e090',
  square: '#f09090',
  sextile: '#80d0e0',
  quincunx: '#c098e0',
  semi_square: '#e0b070',
  semi_sextile: '#70d0b0',
  dim: 'rgba(220, 200, 140, 0.25)',
};

function astroToSvgAngle(deg, ascLon) {
  return 180 + (normalizeDeg(deg) - normalizeDeg(ascLon));
}

function polarToXY(angleDeg, radius) {
  const rad = (angleDeg * Math.PI) / 180;
  return {
    x: CX + radius * Math.cos(rad),
    y: CY - radius * Math.sin(rad),
  };
}

function el(tag, attrs = {}, text = null) {
  const elem = document.createElementNS(SVG_NS, tag);
  for (const [k, v] of Object.entries(attrs)) elem.setAttribute(k, v);
  if (text) elem.textContent = text;
  return elem;
}

/**
 * 円弧パスを生成（サイン帯の背景用）
 */
function arcPath(cx, cy, rOuter, rInner, startAngle, endAngle) {
  const toRad = (d) => (d * Math.PI) / 180;
  const s = toRad(startAngle);
  const e = toRad(endAngle);
  const x1o = cx + rOuter * Math.cos(s);
  const y1o = cy - rOuter * Math.sin(s);
  const x2o = cx + rOuter * Math.cos(e);
  const y2o = cy - rOuter * Math.sin(e);
  const x2i = cx + rInner * Math.cos(e);
  const y2i = cy - rInner * Math.sin(e);
  const x1i = cx + rInner * Math.cos(s);
  const y1i = cy - rInner * Math.sin(s);
  return `M ${x1o} ${y1o} A ${rOuter} ${rOuter} 0 0 0 ${x2o} ${y2o} L ${x2i} ${y2i} A ${rInner} ${rInner} 0 0 1 ${x1i} ${y1i} Z`;
}

const CHART_PLANETS = [
  'sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn',
  'uranus', 'neptune', 'pluto', 'chiron', 'mean_node',
];

const ASPECT_PLANETS = new Set([
  'sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn',
  'uranus', 'neptune', 'pluto', 'chiron',
]);

const MAJOR_ASPECTS = new Set(['conjunction', 'opposition', 'trine', 'square', 'sextile']);

// 天体の短縮日本語ラベル
const PLANET_LABEL_JP = {
  sun: '太', moon: '月', mercury: '水', venus: '金', mars: '火',
  jupiter: '木', saturn: '土', uranus: '天', neptune: '海', pluto: '冥',
  chiron: 'キ', mean_node: '竜',
};

// サインの漢字表示（絵文字を使わない）
const SIGN_LABEL_JP = [
  '牡羊', '牡牛', '双子', '蟹', '獅子', '乙女',
  '天秤', '蠍', '射手', '山羊', '水瓶', '魚',
];

export function drawChart(bodies, houseData, aspects, options = {}) {
  const { maxAspectOrb = 5, enabledAspects = null } = options;
  const ascLon = houseData.angles?.ascendant?.longitude || 0;

  const svg = el('svg', {
    xmlns: SVG_NS,
    viewBox: `0 0 ${SIZE} ${SIZE}`,
    width: SIZE,
    height: SIZE,
  });

  // 背景
  svg.appendChild(el('rect', { x: 0, y: 0, width: SIZE, height: SIZE, fill: COLORS.bg }));

  // チャート内部の背景円（サイン帯との差を出す）
  svg.appendChild(el('circle', { cx: CX, cy: CY, r: R_SIGN_INNER, fill: COLORS.chartInner }));

  // --- サイン帯（交互に色付き背景） ---
  for (let i = 0; i < 12; i++) {
    const startLon = i * 30;
    const endLon = (i + 1) * 30;
    const startAngle = astroToSvgAngle(startLon, ascLon);
    const endAngle = astroToSvgAngle(endLon, ascLon);
    const fill = i % 2 === 0 ? COLORS.signBand : COLORS.signBandAlt;
    svg.appendChild(el('path', {
      d: arcPath(CX, CY, R_OUTER, R_SIGN_INNER, startAngle, endAngle),
      fill,
      stroke: 'none',
    }));
  }

  // --- 円 ---
  svg.appendChild(el('circle', { cx: CX, cy: CY, r: R_OUTER, fill: 'none', stroke: COLORS.ringStroke, 'stroke-width': 1.5 }));
  svg.appendChild(el('circle', { cx: CX, cy: CY, r: R_SIGN_INNER, fill: 'none', stroke: COLORS.ringInner, 'stroke-width': 1 }));
  svg.appendChild(el('circle', { cx: CX, cy: CY, r: R_CENTER, fill: 'none', stroke: COLORS.ringInner, 'stroke-width': 0.5 }));

  // --- サイン分割線 ---
  for (let i = 0; i < 12; i++) {
    const angle = astroToSvgAngle(i * 30, ascLon);
    const p1 = polarToXY(angle, R_SIGN_INNER);
    const p2 = polarToXY(angle, R_OUTER);
    svg.appendChild(el('line', {
      x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
      stroke: COLORS.signDivider, 'stroke-width': 0.8,
    }));
  }

  // --- サイン表示（記号+漢字 横並び） ---
  for (let i = 0; i < 12; i++) {
    const angle = astroToSvgAngle(i * 30 + 15, ascLon);
    const pos = polarToXY(angle, R_SIGN_MID);
    const sign = SIGNS[i];
    const label = SIGN_LABEL_JP[i];
    const color = COLORS[sign.element] || COLORS.text;

    svg.appendChild(el('text', {
      x: pos.x, y: pos.y,
      fill: color,
      'font-size': '13',
      'font-weight': '400',
      'text-anchor': 'middle',
      'dominant-baseline': 'central',
      'font-family': "'IBM Plex Sans JP', 'Segoe UI Symbol', sans-serif",
    }, sign.symbol + '\uFE0E' + label));
  }

  // --- ハウスカスプ線 ---
  if (houseData.cusps) {
    for (let i = 0; i < 12; i++) {
      const cusp = houseData.cusps[i];
      if (!cusp) continue;
      const angle = astroToSvgAngle(cusp.longitude, ascLon);
      const isCardinal = (i === 0 || i === 3 || i === 6 || i === 9);

      // アングル軸は太く目立つ線
      if (isCardinal) {
        const p1 = polarToXY(angle, R_CENTER);
        const p2 = polarToXY(angle, R_SIGN_INNER);
        svg.appendChild(el('line', {
          x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
          stroke: COLORS.houseAngleLine, 'stroke-width': 1.5,
        }));
      } else {
        const p1 = polarToXY(angle, R_CENTER);
        const p2 = polarToXY(angle, R_SIGN_INNER);
        svg.appendChild(el('line', {
          x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
          stroke: COLORS.houseLine, 'stroke-width': 0.8,
          'stroke-dasharray': '6,4',
        }));
      }

      // ハウス番号
      const next = houseData.cusps[(i + 1) % 12];
      if (next) {
        const midAngle = astroToSvgAngle(
          cusp.longitude + normalizeDeg(next.longitude - cusp.longitude) / 2,
          ascLon
        );
        const numPos = polarToXY(midAngle, R_HOUSE_NUM);
        svg.appendChild(el('text', {
          x: numPos.x, y: numPos.y,
          fill: COLORS.houseNum,
          'font-size': '16',
          'font-family': "'Cormorant Garamond', serif",
          'font-weight': '600',
          'text-anchor': 'middle',
          'dominant-baseline': 'central',
        }, String(i + 1)));
      }
    }
  }

  // --- ASC / MC / DSC / IC ラベル ---
  const angleLabels = [
    { label: 'ASC', lon: ascLon },
    { label: 'DSC', lon: normalizeDeg(ascLon + 180) },
  ];
  if (houseData.angles?.mc?.longitude != null) {
    angleLabels.push({ label: 'MC', lon: houseData.angles.mc.longitude });
    angleLabels.push({ label: 'IC', lon: normalizeDeg(houseData.angles.mc.longitude + 180) });
  }

  for (const { label, lon } of angleLabels) {
    const angle = astroToSvgAngle(lon, ascLon);
    const pos = polarToXY(angle, R_OUTER + 18);
    svg.appendChild(el('text', {
      x: pos.x, y: pos.y,
      fill: COLORS.textBright,
      'font-size': '13',
      'font-weight': 'bold',
      'font-family': 'sans-serif',
      'letter-spacing': '0.05em',
      'text-anchor': 'middle',
      'dominant-baseline': 'central',
    }, label));
  }

  // --- アスペクト線（コンジャンクションは線で表現できないので除外） ---
  const aspectFilter = enabledAspects || MAJOR_ASPECTS;
  const chartAspects = aspects.filter(a =>
    a.aspect !== 'conjunction' &&
    aspectFilter.has(a.aspect) &&
    ASPECT_PLANETS.has(a.body1.key) &&
    ASPECT_PLANETS.has(a.body2.key) &&
    a.orb <= maxAspectOrb
  );

  for (const a of chartAspects) {
    const b1 = bodies[a.body1.key];
    const b2 = bodies[a.body2.key];
    if (!b1 || !b2) continue;

    const p1 = polarToXY(astroToSvgAngle(b1.longitude, ascLon), R_ASPECT);
    const p2 = polarToXY(astroToSvgAngle(b2.longitude, ascLon), R_ASPECT);

    const color = COLORS[a.aspect] || COLORS.dim;
    const opacity = a.orb < 1 ? 0.9 : a.orb < 3 ? 0.6 : 0.35;
    const width = a.orb < 1 ? 2.5 : a.orb < 3 ? 1.5 : 0.8;

    svg.appendChild(el('line', {
      x1: p1.x, y1: p1.y, x2: p2.x, y2: p2.y,
      stroke: color,
      'stroke-width': width,
      'stroke-opacity': opacity,
    }));
  }

  // --- 天体プロット ---
  const plotData = [];
  for (const key of CHART_PLANETS) {
    const b = bodies[key];
    if (!b) continue;
    plotData.push({
      key,
      angle: astroToSvgAngle(b.longitude, ascLon),
      body: b,
      radius: R_PLANET,
    });
  }

  plotData.sort((a, b) => a.angle - b.angle);

  // 重なり回避（3段階）
  const MIN_GAP = 11;
  for (let i = 1; i < plotData.length; i++) {
    let diff = plotData[i].angle - plotData[i - 1].angle;
    if (diff < 0) diff += 360;
    if (diff < MIN_GAP) {
      const prev = plotData[i - 1].radius;
      plotData[i].radius = prev === R_PLANET ? R_PLANET + 24
        : prev === R_PLANET + 24 ? R_PLANET - 20
        : R_PLANET + 24;
    }
  }

  for (const pd of plotData) {
    const pos = polarToXY(pd.angle, pd.radius);
    const b = pd.body;
    const elemColor = b.sign ? (COLORS[b.sign.element] || COLORS.text) : COLORS.text;

    // 天体記号（大きめ表示）
    svg.appendChild(el('text', {
      x: pos.x, y: pos.y - 2,
      fill: elemColor,
      'font-size': '22',
      'font-weight': 'bold',
      'text-anchor': 'middle',
      'dominant-baseline': 'central',
    }, b.symbol || pd.key.charAt(0).toUpperCase()));

    // 漢字ラベル（記号の下）
    const jpLabel = PLANET_LABEL_JP[pd.key];
    if (jpLabel) {
      svg.appendChild(el('text', {
        x: pos.x, y: pos.y + 13,
        fill: elemColor,
        'font-size': '9',
        'font-weight': '400',
        'text-anchor': 'middle',
        'dominant-baseline': 'central',
        'font-family': "'IBM Plex Sans JP', sans-serif",
        'opacity': '0.7',
      }, jpLabel));
    }

    // 逆行マーク
    if (b.retrograde) {
      svg.appendChild(el('text', {
        x: pos.x + 14, y: pos.y - 12,
        fill: COLORS.fire,
        'font-size': '10',
        'font-weight': 'bold',
        'text-anchor': 'middle',
      }, 'R'));
    }
  }

  // --- コンジャンクション表示（線ではなく天体間に☌マーク） ---
  if (aspectFilter.has('conjunction')) {
    const conjunctions = aspects.filter(a =>
      a.aspect === 'conjunction' &&
      ASPECT_PLANETS.has(a.body1.key) &&
      ASPECT_PLANETS.has(a.body2.key) &&
      a.orb <= maxAspectOrb
    );
    for (const conj of conjunctions) {
      const pd1 = plotData.find(p => p.key === conj.body1.key);
      const pd2 = plotData.find(p => p.key === conj.body2.key);
      if (!pd1 || !pd2) continue;
      // 2天体の中間位置の外側に☌マークを配置
      const midAngle = (pd1.angle + pd2.angle) / 2;
      const outerR = Math.max(pd1.radius, pd2.radius) + 20;
      const pos = polarToXY(midAngle, outerR);
      svg.appendChild(el('text', {
        x: pos.x, y: pos.y,
        fill: COLORS.conjunction,
        'font-size': '14',
        'text-anchor': 'middle',
        'dominant-baseline': 'central',
        'opacity': '0.8',
      }, '☌'));
    }
  }

  return svg;
}
