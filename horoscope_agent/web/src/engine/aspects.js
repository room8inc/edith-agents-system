/**
 * アスペクト計算
 */

import { ASPECTS, MAJOR_ASPECT_KEYS } from './constants.js';
import { angleDistance } from './utils.js';

/**
 * 2天体間のアスペクトを検出
 * @param {number} lon1 - 天体1の黄経
 * @param {number} lon2 - 天体2の黄経
 * @param {Object} [orbOverrides] - アスペクトごとのオーブ上書き { conjunction: 10, ... }
 * @returns {{ aspect, orb, exact }|null} マッチしたアスペクト or null
 */
export function detectAspect(lon1, lon2, orbOverrides = {}) {
  const dist = angleDistance(lon1, lon2);

  let bestMatch = null;
  let bestOrb = Infinity;

  for (const aspect of ASPECTS) {
    const maxOrb = orbOverrides[aspect.key] ?? aspect.defaultOrb;
    const orb = Math.abs(dist - aspect.angle);

    if (orb <= maxOrb && orb < bestOrb) {
      bestOrb = orb;
      bestMatch = {
        ...aspect,
        orb: Math.round(orb * 100) / 100,
        exact: orb < 0.5,
      };
    }
  }

  return bestMatch;
}

/**
 * アスペクトの適用/分離判定
 * @param {number} speed1 - 天体1の速度
 * @param {number} speed2 - 天体2の速度
 * @param {number} lon1 - 天体1の黄経
 * @param {number} lon2 - 天体2の黄経
 * @param {number} aspectAngle - アスペクトの角度
 * @returns {'applying'|'separating'|'stationary'}
 */
export function getAspectMovement(speed1, speed2, lon1, lon2, aspectAngle) {
  // 速度差がほぼゼロなら stationary
  if (Math.abs(speed1 - speed2) < 0.001) return 'stationary';

  // 現在の実際の角度差
  const currentDist = angleDistance(lon1, lon2);

  // 微小時間後の角度差（速度を使って予測）
  const dt = 0.01; // 0.01日後
  const futureDist = angleDistance(lon1 + speed1 * dt, lon2 + speed2 * dt);

  // アスペクト角度との差が縮まっていれば applying
  const currentOrb = Math.abs(currentDist - aspectAngle);
  const futureOrb = Math.abs(futureDist - aspectAngle);

  if (futureOrb < currentOrb) return 'applying';
  return 'separating';
}

/**
 * 全天体ペアのアスペクトを一括計算
 * @param {Object} bodies - calculateAllBodies() の返り値
 * @param {Object} [options]
 * @param {string[]} [options.bodyKeys] - 計算対象の天体キー（省略で全天体）
 * @param {boolean} [options.majorOnly=false] - メジャーアスペクトのみ
 * @param {Object} [options.orbOverrides] - オーブ上書き
 * @returns {Array} アスペクト配列
 */
export function calculateAllAspects(bodies, options = {}) {
  const {
    bodyKeys = null,
    majorOnly = false,
    orbOverrides = {},
  } = options;

  const keys = bodyKeys || Object.keys(bodies);
  const aspects = [];

  // 有効なオーブ設定（majorOnly なら minor のオーブを0にする）
  const effectiveOrbs = { ...orbOverrides };
  if (majorOnly) {
    for (const a of ASPECTS) {
      if (!MAJOR_ASPECT_KEYS.includes(a.key)) {
        effectiveOrbs[a.key] = 0;
      }
    }
  }

  // ノード同士の自明なペアを除外（ヘッド-テイルは常に180°で無意味）
  const SKIP_PAIRS = new Set([
    'mean_node:mean_south_node',
    'true_node:true_south_node',
    'mean_node:true_south_node',
    'true_node:mean_south_node',
    'mean_node:true_node',
    'mean_south_node:true_south_node',
  ]);

  for (let i = 0; i < keys.length; i++) {
    for (let j = i + 1; j < keys.length; j++) {
      const b1 = bodies[keys[i]];
      const b2 = bodies[keys[j]];
      if (!b1 || !b2) continue;

      // 自明ペアをスキップ
      const pairKey = `${keys[i]}:${keys[j]}`;
      if (SKIP_PAIRS.has(pairKey)) continue;

      const aspect = detectAspect(b1.longitude, b2.longitude, effectiveOrbs);
      if (!aspect) continue;

      const movement = getAspectMovement(
        b1.speed || 0, b2.speed || 0,
        b1.longitude, b2.longitude,
        aspect.angle
      );

      aspects.push({
        body1: { key: keys[i], name: b1.name, nameJp: b1.nameJp },
        body2: { key: keys[j], name: b2.name, nameJp: b2.nameJp },
        aspect: aspect.key,
        aspectName: aspect.name,
        aspectNameJp: aspect.nameJp,
        symbol: aspect.symbol,
        angle: aspect.angle,
        orb: aspect.orb,
        exact: aspect.exact,
        movement,
      });
    }
  }

  // オーブが小さい順にソート
  aspects.sort((a, b) => a.orb - b.orb);

  return aspects;
}
