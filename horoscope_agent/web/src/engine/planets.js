/**
 * 全天体の位置計算
 */

import { ALL_BODIES, DERIVED_POINTS } from './constants.js';
import { calcPlanet } from './sweph.js';
import { normalizeDeg, getSign, getDegreeInSign, isRetrograde } from './utils.js';

/**
 * 全天体+感受点の位置を一括計算
 * @param {number} jd - Julian Day (UT)
 * @returns {Object} key=天体キー, value=位置情報オブジェクト
 */
export function calculateAllBodies(jd) {
  const results = {};

  // Swiss Ephemeris で計算する天体
  for (const body of ALL_BODIES) {
    const pos = calcPlanet(jd, body.id);
    if (pos.error) {
      console.warn(`Calculation error for ${body.name}: ${pos.error}`);
      continue;
    }

    const sign = getSign(pos.longitude);
    results[body.key] = {
      ...body,
      longitude: pos.longitude,
      latitude: pos.latitude,
      distance: pos.distance,
      speed: pos.speed,
      retrograde: isRetrograde(pos.speed),
      sign: sign,
      degreeInSign: getDegreeInSign(pos.longitude),
    };
  }

  // サウスノード（180°反転で算出）
  for (const dp of Object.values(DERIVED_POINTS)) {
    const source = results[dp.derivedFrom];
    if (source) {
      const lon = normalizeDeg(source.longitude + 180);
      const sign = getSign(lon);
      results[dp.key] = {
        ...dp,
        id: null,
        longitude: lon,
        latitude: -source.latitude,
        distance: source.distance,
        speed: source.speed,
        retrograde: source.retrograde,
        sign: sign,
        degreeInSign: getDegreeInSign(lon),
      };
    }
  }

  return results;
}
