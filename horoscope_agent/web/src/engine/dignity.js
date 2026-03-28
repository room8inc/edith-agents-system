/**
 * 品位計算（Essential Dignities）
 * 天体がどのサインで強い/弱いかを判定
 */

import { DOMICILE, DETRIMENT, EXALTATION, FALL } from './constants.js';

/**
 * 天体の品位を判定
 * @param {string} planetKey - 天体キー（'sun', 'moon', etc.）
 * @param {string} signKey - サインキー（'aries', 'taurus', etc.）
 * @returns {{ dignity: string, dignityJp: string, score: number }|null}
 */
export function getDignity(planetKey, signKey) {
  // ドミサイル（+5）
  if (DOMICILE[planetKey]?.includes(signKey)) {
    return { dignity: 'domicile', dignityJp: '支配（ドミサイル）', score: 5 };
  }

  // イグザルテーション（+4）
  if (EXALTATION[planetKey]?.sign === signKey) {
    return { dignity: 'exaltation', dignityJp: '高揚（イグザルテーション）', score: 4 };
  }

  // デトリメント（-5）
  if (DETRIMENT[planetKey]?.includes(signKey)) {
    return { dignity: 'detriment', dignityJp: '障害（デトリメント）', score: -5 };
  }

  // フォール（-4）
  if (FALL[planetKey]?.sign === signKey) {
    return { dignity: 'fall', dignityJp: '転落（フォール）', score: -4 };
  }

  // ペレグリン（品位なし）
  return null;
}

/**
 * 全天体の品位を一括判定
 * @param {Object} bodies - calculateAllBodies() の返り値
 * @returns {Object} key=天体キー, value=品位情報
 */
export function calculateAllDignities(bodies) {
  const dignities = {};

  for (const [key, body] of Object.entries(bodies)) {
    if (!body.sign) continue;
    const dignity = getDignity(key, body.sign.key);
    if (dignity) {
      dignities[key] = dignity;
    }
  }

  return dignities;
}
