/**
 * 入力フォーム処理
 */

import { CITIES, HOUSE_SYSTEMS } from '../engine/constants.js';

/**
 * 都市セレクトボックスを初期化
 */
export function initCitySelect() {
  const select = document.getElementById('city');
  if (!select) return;

  // 日本（47都道府県）と海外を分離
  const jpCities = [];
  const foreignGroups = {};

  for (const [name, data] of Object.entries(CITIES)) {
    if (data.country === 'JP') {
      jpCities.push({ name, ...data });
    } else {
      const country = data.country;
      if (!foreignGroups[country]) foreignGroups[country] = [];
      foreignGroups[country].push({ name, ...data });
    }
  }

  // 日本（optgroupなし、都道府県順でそのまま並ぶ）
  const jpGroup = document.createElement('optgroup');
  jpGroup.label = '日本';
  for (const city of jpCities) {
    const option = document.createElement('option');
    option.value = city.name;
    option.textContent = city.nameJp;
    option.dataset.lat = city.lat;
    option.dataset.lng = city.lng;
    option.dataset.tz = city.tz;
    jpGroup.appendChild(option);
  }
  select.appendChild(jpGroup);

  // 海外
  for (const country of Object.keys(foreignGroups).sort()) {
    const cities = foreignGroups[country];
    const optgroup = document.createElement('optgroup');
    optgroup.label = country;

    for (const city of cities) {
      const option = document.createElement('option');
      option.value = city.name;
      option.textContent = `${city.nameJp}`;
      option.dataset.lat = city.lat;
      option.dataset.lng = city.lng;
      option.dataset.tz = city.tz;
      optgroup.appendChild(option);
    }

    select.appendChild(optgroup);
  }

  // 都市選択時に緯度経度を自動入力
  select.addEventListener('change', () => {
    const selected = select.options[select.selectedIndex];
    if (selected && selected.dataset.lat) {
      document.getElementById('lat').value = selected.dataset.lat;
      document.getElementById('lng').value = selected.dataset.lng;
      document.getElementById('tz').value = selected.dataset.tz;
    }
  });

  // --- 住所・施設名ジオコーディング ---
  const geoBtn = document.getElementById('geo-search-btn');
  const geoInput = document.getElementById('geo-query');
  const geoResults = document.getElementById('geo-results');

  if (geoBtn && geoInput) {
    const doSearch = async () => {
      const query = geoInput.value.trim();
      if (!query) return;
      geoResults.textContent = '検索中...';
      try {
        const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=5&accept-language=ja`;
        const res = await fetch(url, { headers: { 'User-Agent': 'HoroscopeApp/1.0' } });
        const data = await res.json();
        if (!data.length) {
          geoResults.textContent = '見つかりませんでした';
          return;
        }
        geoResults.innerHTML = '';
        for (const item of data) {
          const link = document.createElement('a');
          link.href = '#';
          link.style.cssText = 'display:block; padding:3px 0; color:var(--color-accent, #6af); text-decoration:none;';
          link.textContent = item.display_name;
          link.addEventListener('click', (e) => {
            e.preventDefault();
            document.getElementById('lat').value = parseFloat(item.lat).toFixed(4);
            document.getElementById('lng').value = parseFloat(item.lon).toFixed(4);
            document.getElementById('tz').value = 9; // 日本デフォルト
            // セレクトをクリア（カスタム座標を使うので）
            select.value = '';
            geoResults.textContent = `✓ ${item.display_name}`;
          });
          geoResults.appendChild(link);
        }
      } catch (err) {
        geoResults.textContent = 'エラー: ' + err.message;
      }
    };
    geoBtn.addEventListener('click', doSearch);
    geoInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); doSearch(); }
    });
  }
}

/**
 * フォームから入力値を取得
 * @returns {Object|null} 入力値オブジェクト、バリデーションエラー時はnull
 */
export function getFormValues() {
  const name = document.getElementById('name').value.trim() || 'Chart';
  const year = parseInt(document.getElementById('year').value);
  const month = parseInt(document.getElementById('month').value);
  const day = parseInt(document.getElementById('day').value);
  const hour = parseInt(document.getElementById('hour').value);
  const minute = parseInt(document.getElementById('minute').value);
  const lat = parseFloat(document.getElementById('lat').value);
  const lng = parseFloat(document.getElementById('lng').value);
  const tz = parseFloat(document.getElementById('tz').value);
  const houseSystem = document.getElementById('house-system').value;

  // バリデーション
  if (isNaN(year) || year < 1800 || year > 2400) return null;
  if (isNaN(month) || month < 1 || month > 12) return null;
  if (isNaN(day) || day < 1 || day > 31) return null;
  if (isNaN(hour) || hour < 0 || hour > 23) return null;
  if (isNaN(minute) || minute < 0 || minute > 59) return null;
  if (isNaN(lat) || lat < -90 || lat > 90) return null;
  if (isNaN(lng) || lng < -180 || lng > 180) return null;
  if (isNaN(tz)) return null;

  return { name, year, month, day, hour, minute, lat, lng, tz, houseSystem };
}
