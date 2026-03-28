/**
 * ホロスコープ計算 ユーティリティ
 */

import { SIGNS, LUNAR_PHASES } from './constants.js';

/**
 * 角度を 0-360 に正規化
 */
export function normalizeDeg(deg) {
  let d = deg % 360;
  if (d < 0) d += 360;
  return d;
}

/**
 * 黄経（0-360）からサインインデックス（0-11）を取得
 */
export function getSignIndex(longitude) {
  return Math.floor(normalizeDeg(longitude) / 30);
}

/**
 * 黄経からサインオブジェクトを取得
 */
export function getSign(longitude) {
  return SIGNS[getSignIndex(longitude)];
}

/**
 * 黄経からサイン内度数を取得（0-30）
 */
export function getDegreeInSign(longitude) {
  return normalizeDeg(longitude) % 30;
}

/**
 * 度数を 度°分'秒" 形式に変換
 */
export function degToDMS(deg) {
  const absDeg = Math.abs(deg);
  const d = Math.floor(absDeg);
  const mFloat = (absDeg - d) * 60;
  const m = Math.floor(mFloat);
  const s = Math.round((mFloat - m) * 60);
  return { degrees: d, minutes: m, seconds: s, negative: deg < 0 };
}

/**
 * 度数を "DD°MM'" 形式の文字列に変換
 */
export function formatDegMin(deg) {
  const dms = degToDMS(deg);
  return `${dms.degrees}°${String(dms.minutes).padStart(2, '0')}'`;
}

/**
 * 度数を "DD°MM'SS\"" 形式の文字列に変換
 */
export function formatDMS(deg) {
  const dms = degToDMS(deg);
  return `${dms.degrees}°${String(dms.minutes).padStart(2, '0')}'${String(dms.seconds).padStart(2, '0')}"`;
}

/**
 * サイン内度数を "DD° サイン記号" で表示
 */
export function formatPosition(longitude) {
  const sign = getSign(longitude);
  const degInSign = getDegreeInSign(longitude);
  return `${formatDegMin(degInSign)} ${sign.symbol}`;
}

/**
 * 2つの黄経間の最短角度差（符号あり）
 * 正 = p2がp1より先（反時計回り）
 */
export function angleDiff(lon1, lon2) {
  let diff = normalizeDeg(lon2) - normalizeDeg(lon1);
  if (diff > 180) diff -= 360;
  if (diff < -180) diff += 360;
  return diff;
}

/**
 * 2つの黄経間の最短角度差（絶対値）
 */
export function angleDistance(lon1, lon2) {
  return Math.abs(angleDiff(lon1, lon2));
}

/**
 * ローカル時刻 + タイムゾーンオフセット → UTC の時/分
 * @param {number} hour - ローカル時
 * @param {number} minute - ローカル分
 * @param {number} tzOffset - タイムゾーンオフセット（時間、例: JST=+9）
 * @returns {{ year, month, day, hourDecimal }} 日を跨ぐ場合の処理は呼び出し側で
 */
export function localToUTCHour(hour, minute, tzOffset) {
  return hour + minute / 60 - tzOffset;
}

/**
 * 月の位相角（太陽-月の角度差）から月相を判定
 */
export function getLunarPhase(sunLon, moonLon) {
  const angle = normalizeDeg(moonLon - sunLon);
  for (const phase of LUNAR_PHASES) {
    if (angle >= phase.minAngle && angle < phase.maxAngle) {
      return { ...phase, angle: Math.round(angle * 100) / 100 };
    }
  }
  // 360° ≈ 0° → 新月
  return { ...LUNAR_PHASES[0], angle: Math.round(angle * 100) / 100 };
}

/**
 * 天体が逆行中かどうか（速度が負なら逆行）
 */
export function isRetrograde(speed) {
  return speed < 0;
}

/**
 * 天体がどのハウスに在るかを判定（カスプ配列から）
 * @param {number} longitude - 天体の黄経
 * @param {number[]} cusps - ハウスカスプ配列 [1-12]（0番は未使用、1始まり）
 * @returns {number} ハウス番号 1-12
 */
export function findHouse(longitude, cusps) {
  const lon = normalizeDeg(longitude);
  for (let i = 1; i <= 12; i++) {
    const cusp = normalizeDeg(cusps[i]);
    const nextCusp = normalizeDeg(cusps[i === 12 ? 1 : i + 1]);

    if (nextCusp > cusp) {
      // 通常ケース
      if (lon >= cusp && lon < nextCusp) return i;
    } else {
      // 0°を跨ぐケース（例: カスプが350°で次が20°）
      if (lon >= cusp || lon < nextCusp) return i;
    }
  }
  return 1; // フォールバック
}
