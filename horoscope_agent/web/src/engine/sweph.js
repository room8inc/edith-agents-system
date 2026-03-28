/**
 * Swiss Ephemeris WASM ラッパー
 * swisseph-wasm の初期化とローレベルAPIを薄くラップ
 */

import SwissEph from 'swisseph-wasm';

let _swe = null;
let _initPromise = null;

/**
 * SwissEph インスタンスを初期化して返す（シングルトン）
 */
export async function initSwe() {
  if (_swe) return _swe;
  if (_initPromise) return _initPromise;

  _initPromise = (async () => {
    const swe = new SwissEph();
    await swe.initSwissEph();
    _swe = swe;
    return swe;
  })();

  return _initPromise;
}

/**
 * SwissEph インスタンスを取得（初期化済み前提）
 */
export function getSwe() {
  if (!_swe) throw new Error('SwissEph not initialized. Call initSwe() first.');
  return _swe;
}

/**
 * ローカル日時からJulian Day (UT) を計算
 * @param {number} year
 * @param {number} month - 1-12
 * @param {number} day
 * @param {number} hour - ローカル時刻（時）
 * @param {number} minute - ローカル時刻（分）
 * @param {number} tzOffset - タイムゾーンオフセット（時間、例: JST=9）
 * @returns {number} Julian Day in UT
 */
export function calcJulDay(year, month, day, hour, minute, tzOffset) {
  const swe = getSwe();
  const utcHour = hour + minute / 60 - tzOffset;
  return swe.julday(year, month, day, utcHour);
}

/**
 * 天体の位置を計算
 * @param {number} jd - Julian Day (UT)
 * @param {number} planetId - Swiss Ephemeris 天体ID
 * @returns {{ longitude, latitude, distance, speed, error }}
 */
export function calcPlanet(jd, planetId) {
  const swe = getSwe();
  const flags = swe.SEFLG_SWIEPH | swe.SEFLG_SPEED;

  try {
    const result = swe.calc_ut(jd, planetId, flags);

    // calc_ut は配列を返す: [longitude, latitude, distance, lonSpeed, latSpeed, distSpeed]
    if (Array.isArray(result)) {
      return {
        longitude: result[0],
        latitude: result[1],
        distance: result[2],
        speed: result[3],       // longitude speed (deg/day)
        latSpeed: result[4],
        distSpeed: result[5],
        error: null,
      };
    }

    // オブジェクト形式の場合
    if (result && typeof result === 'object') {
      return {
        longitude: result.longitude ?? result[0],
        latitude: result.latitude ?? result[1],
        distance: result.distance ?? result[2],
        speed: result.longitudeSpeed ?? result[3],
        latSpeed: result.latitudeSpeed ?? result[4],
        distSpeed: result.distanceSpeed ?? result[5],
        error: null,
      };
    }

    return { longitude: 0, latitude: 0, distance: 0, speed: 0, latSpeed: 0, distSpeed: 0, error: 'Unexpected result format' };
  } catch (e) {
    return { longitude: 0, latitude: 0, distance: 0, speed: 0, latSpeed: 0, distSpeed: 0, error: e.message };
  }
}

/**
 * ハウスカスプを計算
 * @param {number} jd - Julian Day (UT)
 * @param {number} lat - 地理的緯度
 * @param {number} lng - 地理的経度
 * @param {string} system - ハウスシステム文字 ('P', 'K', 'O', etc.)
 * @returns {{ cusps: number[], ascmc: number[], error: string|null }}
 *   cusps[1..12] = ハウスカスプ（黄経）
 *   ascmc[0]=ASC, ascmc[1]=MC, ascmc[2]=ARMC, ascmc[3]=Vertex,
 *   ascmc[4]=Equatorial ASC, ascmc[5]=Co-ASC(Koch), ascmc[6]=Co-ASC(Munkasey), ascmc[7]=Polar ASC
 */
export function calcHouses(jd, lat, lng, system = 'P') {
  const swe = getSwe();

  try {
    const result = swe.houses(jd, lat, lng, system);

    // result の形式を正規化
    if (result && result.cusps) {
      return { cusps: result.cusps, ascmc: result.ascmc || result.asc_mc || [], error: null };
    }

    // 配列形式: houses() が cusps[13] + ascmc[8] を返す場合
    if (Array.isArray(result)) {
      return { cusps: result.slice(0, 13), ascmc: result.slice(13), error: null };
    }

    return { cusps: [], ascmc: [], error: 'Unexpected houses result format' };
  } catch (e) {
    return { cusps: [], ascmc: [], error: e.message };
  }
}

/**
 * 天体のハウス位置を計算
 * @param {number} jd - Julian Day (UT)
 * @param {number} lat - 緯度
 * @param {number} lng - 経度（未使用だがAPI互換性のため）
 * @param {string} system - ハウスシステム
 * @param {number} planetLon - 天体の黄経
 * @param {number} planetLat - 天体の黄緯
 * @returns {number} ハウス位置（小数）
 */
export function calcHousePos(jd, lat, lng, system, planetLon, planetLat) {
  const swe = getSwe();
  try {
    const armc = swe.sidtime(jd) * 15; // ARMC in degrees
    const obliquity = 23.44; // 黄道傾斜角（概算）
    return swe.house_pos(armc, lat, obliquity, system, planetLon, planetLat);
  } catch {
    return 0;
  }
}

/**
 * リソース解放
 */
export function closeSwe() {
  if (_swe) {
    _swe.close();
    _swe = null;
    _initPromise = null;
  }
}
