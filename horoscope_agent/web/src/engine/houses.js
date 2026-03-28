/**
 * ハウスカスプ計算（7システム対応）
 */

import { HOUSE_SYSTEMS, SIGNS } from './constants.js';
import { calcHouses } from './sweph.js';
import { getSign, getDegreeInSign } from './utils.js';

/**
 * ハウスカスプを計算
 * @param {number} jd - Julian Day (UT)
 * @param {number} lat - 地理的緯度
 * @param {number} lng - 地理的経度
 * @param {string} system - ハウスシステム文字（デフォルト: 'P' = Placidus）
 * @returns {{ cusps, angles, system, error }}
 */
export function calculateHouses(jd, lat, lng, system = 'P') {
  const result = calcHouses(jd, lat, lng, system);

  if (result.error) {
    return { cusps: [], angles: {}, system, error: result.error };
  }

  // カスプ情報を整形（1-12）
  const cusps = [];
  for (let i = 1; i <= 12; i++) {
    const lon = result.cusps[i];
    const sign = getSign(lon);
    cusps.push({
      house: i,
      longitude: lon,
      sign: sign,
      degreeInSign: getDegreeInSign(lon),
    });
  }

  // アングル（ASC, MC, Vertex 等）
  const ascmc = result.ascmc || [];
  const angles = {
    ascendant:  { longitude: ascmc[0], sign: getSign(ascmc[0] || 0), degreeInSign: getDegreeInSign(ascmc[0] || 0) },
    mc:         { longitude: ascmc[1], sign: getSign(ascmc[1] || 0), degreeInSign: getDegreeInSign(ascmc[1] || 0) },
    armc:       ascmc[2] || 0,
    vertex:     { longitude: ascmc[3], sign: getSign(ascmc[3] || 0), degreeInSign: getDegreeInSign(ascmc[3] || 0) },
    equatorialAsc: ascmc[4] || 0,
    coAscKoch:  ascmc[5] || 0,
    coAscMunkasey: ascmc[6] || 0,
    polarAsc:   ascmc[7] || 0,
  };

  return {
    cusps,
    rawCusps: result.cusps,  // findHouse() 用に生の配列も保持
    angles,
    system,
    systemName: HOUSE_SYSTEMS[system]?.nameJp || system,
    error: null,
  };
}
