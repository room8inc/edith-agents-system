/**
 * 追加感受点の算出
 * サウスノードは planets.js で算出済み。ここではハウス関連の感受点を計算
 */

import { getSign, getDegreeInSign, normalizeDeg } from './utils.js';

/**
 * パート・オブ・フォーチュン（幸運の部分）を計算
 * 昼チャート: ASC + Moon - Sun
 * 夜チャート: ASC + Sun - Moon
 * @param {number} ascLon - アセンダントの黄経
 * @param {number} sunLon - 太陽の黄経
 * @param {number} moonLon - 月の黄経
 * @param {boolean} isDaytime - 昼チャートかどうか
 * @returns {Object}
 */
export function calcPartOfFortune(ascLon, sunLon, moonLon, isDaytime) {
  let lon;
  if (isDaytime) {
    lon = normalizeDeg(ascLon + moonLon - sunLon);
  } else {
    lon = normalizeDeg(ascLon + sunLon - moonLon);
  }
  const sign = getSign(lon);
  return {
    key: 'part_of_fortune',
    name: 'Part of Fortune',
    nameJp: 'パート・オブ・フォーチュン',
    symbol: '⊕',
    longitude: lon,
    sign,
    degreeInSign: getDegreeInSign(lon),
  };
}

/**
 * パート・オブ・スピリット（精神の部分）を計算
 * 昼チャート: ASC + Sun - Moon
 * 夜チャート: ASC + Moon - Sun
 * （フォーチュンの逆）
 */
export function calcPartOfSpirit(ascLon, sunLon, moonLon, isDaytime) {
  let lon;
  if (isDaytime) {
    lon = normalizeDeg(ascLon + sunLon - moonLon);
  } else {
    lon = normalizeDeg(ascLon + moonLon - sunLon);
  }
  const sign = getSign(lon);
  return {
    key: 'part_of_spirit',
    name: 'Part of Spirit',
    nameJp: 'パート・オブ・スピリット',
    symbol: '⊗',
    longitude: lon,
    sign,
    degreeInSign: getDegreeInSign(lon),
  };
}

/**
 * 太陽が地平線上にあるかどうか（昼/夜判定）
 * 太陽が第7-12ハウスにあれば昼（地平線上）
 * @param {number} sunLon - 太陽の黄経
 * @param {number} ascLon - アセンダントの黄経
 * @returns {boolean}
 */
export function isDaytimeChart(sunLon, ascLon) {
  // 太陽がASC（東の地平線）からDSC（西の地平線）の間にあれば昼
  // つまり ASC から時計回りに180°の範囲
  const diff = normalizeDeg(sunLon - ascLon);
  return diff >= 180; // 7-12ハウス側 = 地平線上
}

/**
 * Vertex情報をフォーマット（houses計算で得られたものを整形）
 */
export function formatVertex(vertexLon) {
  if (!vertexLon) return null;
  const sign = getSign(vertexLon);
  return {
    key: 'vertex',
    name: 'Vertex',
    nameJp: 'バーテックス',
    symbol: 'Vx',
    longitude: vertexLon,
    sign,
    degreeInSign: getDegreeInSign(vertexLon),
  };
}

/**
 * 全追加感受点を一括計算
 */
export function calculateExtraPoints(bodies, angles) {
  const points = {};

  const sunLon = bodies.sun?.longitude;
  const moonLon = bodies.moon?.longitude;
  const ascLon = angles.ascendant?.longitude;

  if (sunLon != null && moonLon != null && ascLon != null) {
    const daytime = isDaytimeChart(sunLon, ascLon);

    points.part_of_fortune = calcPartOfFortune(ascLon, sunLon, moonLon, daytime);
    points.part_of_spirit = calcPartOfSpirit(ascLon, sunLon, moonLon, daytime);
    points.is_daytime = daytime;
  }

  if (angles.vertex?.longitude) {
    points.vertex = formatVertex(angles.vertex.longitude);
  }

  return points;
}
