/**
 * ホロスコープ計算 定数定義
 * Swiss Ephemeris の天体ID・サイン・アスペクト・品位テーブル等
 */

// ============================================================
// 天体ID（Swiss Ephemeris 定数）
// ============================================================
export const PLANETS = {
  SUN:        { id: 0,  key: 'sun',        name: 'Sun',     nameJp: '太陽',     symbol: '☉' },
  MOON:       { id: 1,  key: 'moon',       name: 'Moon',    nameJp: '月',       symbol: '☽' },
  MERCURY:    { id: 2,  key: 'mercury',    name: 'Mercury', nameJp: '水星',     symbol: '☿' },
  VENUS:      { id: 3,  key: 'venus',      name: 'Venus',   nameJp: '金星',     symbol: '♀' },
  MARS:       { id: 4,  key: 'mars',       name: 'Mars',    nameJp: '火星',     symbol: '♂' },
  JUPITER:    { id: 5,  key: 'jupiter',    name: 'Jupiter', nameJp: '木星',     symbol: '♃' },
  SATURN:     { id: 6,  key: 'saturn',     name: 'Saturn',  nameJp: '土星',     symbol: '♄' },
  URANUS:     { id: 7,  key: 'uranus',     name: 'Uranus',  nameJp: '天王星',   symbol: '♅' },
  NEPTUNE:    { id: 8,  key: 'neptune',    name: 'Neptune', nameJp: '海王星',   symbol: '♆' },
  PLUTO:      { id: 9,  key: 'pluto',      name: 'Pluto',   nameJp: '冥王星',   symbol: '♇' },
  CHIRON:     { id: 15, key: 'chiron',     name: 'Chiron',  nameJp: 'カイロン', symbol: '⚷' },
  CERES:      { id: 17, key: 'ceres',      name: 'Ceres',   nameJp: 'ケレス',   symbol: '⚳' },
  PALLAS:     { id: 18, key: 'pallas',     name: 'Pallas',  nameJp: 'パラス',   symbol: '⚴' },
  JUNO:       { id: 19, key: 'juno',       name: 'Juno',    nameJp: 'ジュノー', symbol: '⚵' },
  VESTA:      { id: 20, key: 'vesta',      name: 'Vesta',   nameJp: 'ベスタ',   symbol: '⚶' },
};

// 感受点（ノード・リリス）
export const POINTS = {
  MEAN_NODE:  { id: 10, key: 'mean_node',  name: 'Mean Node',     nameJp: '平均ドラゴンヘッド', symbol: '☊' },
  TRUE_NODE:  { id: 11, key: 'true_node',  name: 'True Node',     nameJp: '真ドラゴンヘッド',   symbol: '☊' },
  MEAN_LILITH:{ id: 12, key: 'mean_lilith',name: 'Mean Lilith',   nameJp: '平均リリス',         symbol: '⚸' },
  TRUE_LILITH:{ id: 13, key: 'true_lilith',name: 'True Lilith',   nameJp: '真リリス',           symbol: '⚸' },
};

// サウスノードは計算で出す（+180°）ので定数だけ定義
export const DERIVED_POINTS = {
  MEAN_SOUTH_NODE: { key: 'mean_south_node', name: 'Mean South Node', nameJp: '平均ドラゴンテイル', symbol: '☋', derivedFrom: 'mean_node' },
  TRUE_SOUTH_NODE: { key: 'true_south_node', name: 'True South Node', nameJp: '真ドラゴンテイル',   symbol: '☋', derivedFrom: 'true_node' },
};

// 全天体リスト（calc_ut で計算するもの）
export const ALL_BODIES = [
  ...Object.values(PLANETS),
  ...Object.values(POINTS),
];

// ============================================================
// 12サイン（黄道十二宮）
// ============================================================
export const SIGNS = [
  { index: 0,  key: 'aries',       name: 'Aries',       nameJp: '牡羊座',   symbol: '♈', element: 'fire',  quality: 'cardinal', ruler: 'mars' },
  { index: 1,  key: 'taurus',      name: 'Taurus',      nameJp: '牡牛座',   symbol: '♉', element: 'earth', quality: 'fixed',    ruler: 'venus' },
  { index: 2,  key: 'gemini',      name: 'Gemini',      nameJp: '双子座',   symbol: '♊', element: 'air',   quality: 'mutable',  ruler: 'mercury' },
  { index: 3,  key: 'cancer',      name: 'Cancer',      nameJp: '蟹座',     symbol: '♋', element: 'water', quality: 'cardinal', ruler: 'moon' },
  { index: 4,  key: 'leo',         name: 'Leo',         nameJp: '獅子座',   symbol: '♌', element: 'fire',  quality: 'fixed',    ruler: 'sun' },
  { index: 5,  key: 'virgo',       name: 'Virgo',       nameJp: '乙女座',   symbol: '♍', element: 'earth', quality: 'mutable',  ruler: 'mercury' },
  { index: 6,  key: 'libra',       name: 'Libra',       nameJp: '天秤座',   symbol: '♎', element: 'air',   quality: 'cardinal', ruler: 'venus' },
  { index: 7,  key: 'scorpio',     name: 'Scorpio',     nameJp: '蠍座',     symbol: '♏', element: 'water', quality: 'fixed',    ruler: 'pluto' },
  { index: 8,  key: 'sagittarius', name: 'Sagittarius', nameJp: '射手座',   symbol: '♐', element: 'fire',  quality: 'mutable',  ruler: 'jupiter' },
  { index: 9,  key: 'capricorn',   name: 'Capricorn',   nameJp: '山羊座',   symbol: '♑', element: 'earth', quality: 'cardinal', ruler: 'saturn' },
  { index: 10, key: 'aquarius',    name: 'Aquarius',    nameJp: '水瓶座',   symbol: '♒', element: 'air',   quality: 'fixed',    ruler: 'uranus' },
  { index: 11, key: 'pisces',      name: 'Pisces',      nameJp: '魚座',     symbol: '♓', element: 'water', quality: 'mutable',  ruler: 'neptune' },
];

// ============================================================
// エレメント・クオリティ
// ============================================================
export const ELEMENTS = {
  fire:  { name: 'Fire',  nameJp: '火', signs: ['aries', 'leo', 'sagittarius'] },
  earth: { name: 'Earth', nameJp: '地', signs: ['taurus', 'virgo', 'capricorn'] },
  air:   { name: 'Air',   nameJp: '風', signs: ['gemini', 'libra', 'aquarius'] },
  water: { name: 'Water', nameJp: '水', signs: ['cancer', 'scorpio', 'pisces'] },
};

export const QUALITIES = {
  cardinal: { name: 'Cardinal', nameJp: '活動宮', signs: ['aries', 'cancer', 'libra', 'capricorn'] },
  fixed:    { name: 'Fixed',    nameJp: '固定宮', signs: ['taurus', 'leo', 'scorpio', 'aquarius'] },
  mutable:  { name: 'Mutable',  nameJp: '柔軟宮', signs: ['gemini', 'virgo', 'sagittarius', 'pisces'] },
};

// ============================================================
// アスペクト定義
// ============================================================
export const ASPECTS = [
  { key: 'conjunction',    name: 'Conjunction',    nameJp: 'コンジャンクション', symbol: '☌', angle: 0,   defaultOrb: 8 },
  { key: 'opposition',     name: 'Opposition',     nameJp: 'オポジション',       symbol: '☍', angle: 180, defaultOrb: 8 },
  { key: 'trine',          name: 'Trine',          nameJp: 'トライン',       symbol: '△', angle: 120, defaultOrb: 8 },
  { key: 'square',         name: 'Square',         nameJp: 'スクエア',       symbol: '□', angle: 90,  defaultOrb: 7 },
  { key: 'sextile',        name: 'Sextile',        nameJp: 'セクスタイル',   symbol: '⚹', angle: 60,  defaultOrb: 6 },
  { key: 'quincunx',       name: 'Quincunx',       nameJp: 'クインカンクス', symbol: '⚻', angle: 150, defaultOrb: 3 },
  { key: 'semi_square',    name: 'Semi-square',    nameJp: 'セミスクエア',   symbol: '∠', angle: 45,  defaultOrb: 2 },
  { key: 'sesquiquadrate', name: 'Sesquiquadrate', nameJp: 'セスキコードレイト', symbol: '⚼', angle: 135, defaultOrb: 2 },
  { key: 'semi_sextile',   name: 'Semi-sextile',   nameJp: 'セミセクスタイル', symbol: '⚺', angle: 30,  defaultOrb: 2 },
  { key: 'quintile',       name: 'Quintile',       nameJp: 'クインタイル',   symbol: 'Q',  angle: 72,  defaultOrb: 2 },
  { key: 'bi_quintile',    name: 'Bi-quintile',    nameJp: 'バイクインタイル', symbol: 'bQ', angle: 144, defaultOrb: 2 },
];

// メジャーアスペクトのキー（表示のフィルタ用）
export const MAJOR_ASPECT_KEYS = ['conjunction', 'opposition', 'trine', 'square', 'sextile'];

// ============================================================
// ハウスシステム
// ============================================================
export const HOUSE_SYSTEMS = {
  P: { name: 'Placidus',       nameJp: 'プラシーダス' },
  K: { name: 'Koch',           nameJp: 'コッホ' },
  O: { name: 'Porphyrius',     nameJp: 'ポーフィリー' },
  R: { name: 'Regiomontanus',  nameJp: 'レジオモンタナス' },
  C: { name: 'Campanus',       nameJp: 'カンパヌス' },
  E: { name: 'Equal',          nameJp: 'イコール' },
  W: { name: 'Whole Sign',     nameJp: 'ホールサイン' },
};

// ============================================================
// 品位テーブル（Essential Dignities）
// ============================================================
// ドミサイル（支配星）
export const DOMICILE = {
  sun:     ['leo'],
  moon:    ['cancer'],
  mercury: ['gemini', 'virgo'],
  venus:   ['taurus', 'libra'],
  mars:    ['aries', 'scorpio'],
  jupiter: ['sagittarius', 'pisces'],
  saturn:  ['capricorn', 'aquarius'],
  uranus:  ['aquarius'],
  neptune: ['pisces'],
  pluto:   ['scorpio'],
};

// デトリメント（障害）= ドミサイルの反対サイン
export const DETRIMENT = {
  sun:     ['aquarius'],
  moon:    ['capricorn'],
  mercury: ['sagittarius', 'pisces'],
  venus:   ['aries', 'scorpio'],
  mars:    ['taurus', 'libra'],
  jupiter: ['gemini', 'virgo'],
  saturn:  ['cancer', 'leo'],
  uranus:  ['leo'],
  neptune: ['virgo'],
  pluto:   ['taurus'],
};

// イグザルテーション（高揚）
export const EXALTATION = {
  sun:     { sign: 'aries',       degree: 19 },
  moon:    { sign: 'taurus',      degree: 3 },
  mercury: { sign: 'virgo',       degree: 15 },
  venus:   { sign: 'pisces',      degree: 27 },
  mars:    { sign: 'capricorn',   degree: 28 },
  jupiter: { sign: 'cancer',      degree: 15 },
  saturn:  { sign: 'libra',       degree: 21 },
  uranus:  { sign: 'scorpio',     degree: null },
  neptune: { sign: 'cancer',      degree: null },
  pluto:   { sign: 'leo',         degree: null },
};

// フォール（転落）= イグザルテーションの反対サイン
export const FALL = {
  sun:     { sign: 'libra' },
  moon:    { sign: 'scorpio' },
  mercury: { sign: 'pisces' },
  venus:   { sign: 'virgo' },
  mars:    { sign: 'cancer' },
  jupiter: { sign: 'capricorn' },
  saturn:  { sign: 'aries' },
  uranus:  { sign: 'taurus' },
  neptune: { sign: 'capricorn' },
  pluto:   { sign: 'aquarius' },
};

// ============================================================
// 月相
// ============================================================
export const LUNAR_PHASES = [
  { key: 'new_moon',        nameJp: '新月',       minAngle: 0,   maxAngle: 45 },
  { key: 'waxing_crescent', nameJp: '三日月',     minAngle: 45,  maxAngle: 90 },
  { key: 'first_quarter',   nameJp: '上弦の月',   minAngle: 90,  maxAngle: 135 },
  { key: 'waxing_gibbous',  nameJp: '十三夜月',   minAngle: 135, maxAngle: 180 },
  { key: 'full_moon',       nameJp: '満月',       minAngle: 180, maxAngle: 225 },
  { key: 'waning_gibbous',  nameJp: '十八夜月',   minAngle: 225, maxAngle: 270 },
  { key: 'last_quarter',    nameJp: '下弦の月',   minAngle: 270, maxAngle: 315 },
  { key: 'waning_crescent', nameJp: '二十六夜月', minAngle: 315, maxAngle: 360 },
];

// ============================================================
// 都市ルックアップ（緯度経度）
// ============================================================
export const CITIES = {
  // 日本 — 47都道府県庁所在地（北→南順）
  'Sapporo':     { lat: 43.0621, lng: 141.3544, tz: 9, country: 'JP', nameJp: '北海道 札幌' },
  'Aomori':      { lat: 40.8246, lng: 140.7400, tz: 9, country: 'JP', nameJp: '青森' },
  'Morioka':     { lat: 39.7036, lng: 141.1527, tz: 9, country: 'JP', nameJp: '岩手 盛岡' },
  'Sendai':      { lat: 38.2682, lng: 140.8694, tz: 9, country: 'JP', nameJp: '宮城 仙台' },
  'Akita':       { lat: 39.7200, lng: 140.1025, tz: 9, country: 'JP', nameJp: '秋田' },
  'Yamagata':    { lat: 38.2405, lng: 140.3633, tz: 9, country: 'JP', nameJp: '山形' },
  'Fukushima':   { lat: 37.7503, lng: 140.4676, tz: 9, country: 'JP', nameJp: '福島' },
  'Mito':        { lat: 36.3418, lng: 140.4468, tz: 9, country: 'JP', nameJp: '茨城 水戸' },
  'Utsunomiya':  { lat: 36.5551, lng: 139.8836, tz: 9, country: 'JP', nameJp: '栃木 宇都宮' },
  'Maebashi':    { lat: 36.3912, lng: 139.0608, tz: 9, country: 'JP', nameJp: '群馬 前橋' },
  'Saitama':     { lat: 35.8617, lng: 139.6455, tz: 9, country: 'JP', nameJp: '埼玉 さいたま' },
  'Chiba':       { lat: 35.6047, lng: 140.1233, tz: 9, country: 'JP', nameJp: '千葉' },
  'Tokyo':       { lat: 35.6762, lng: 139.6503, tz: 9, country: 'JP', nameJp: '東京' },
  'Yokohama':    { lat: 35.4437, lng: 139.6380, tz: 9, country: 'JP', nameJp: '神奈川 横浜' },
  'Niigata':     { lat: 37.9026, lng: 139.0236, tz: 9, country: 'JP', nameJp: '新潟' },
  'Toyama':      { lat: 36.6953, lng: 137.2113, tz: 9, country: 'JP', nameJp: '富山' },
  'Kanazawa':    { lat: 36.5613, lng: 136.6562, tz: 9, country: 'JP', nameJp: '石川 金沢' },
  'Fukui':       { lat: 36.0652, lng: 136.2216, tz: 9, country: 'JP', nameJp: '福井' },
  'Kofu':        { lat: 35.6642, lng: 138.5684, tz: 9, country: 'JP', nameJp: '山梨 甲府' },
  'Nagano':      { lat: 36.2378, lng: 138.1812, tz: 9, country: 'JP', nameJp: '長野' },
  'Gifu':        { lat: 35.3912, lng: 136.7223, tz: 9, country: 'JP', nameJp: '岐阜' },
  'Shizuoka':    { lat: 34.9756, lng: 138.3828, tz: 9, country: 'JP', nameJp: '静岡' },
  'Nagoya':      { lat: 35.1815, lng: 136.9066, tz: 9, country: 'JP', nameJp: '愛知 名古屋' },
  'Tsu':         { lat: 34.7303, lng: 136.5086, tz: 9, country: 'JP', nameJp: '三重 津' },
  'Otsu':        { lat: 35.0045, lng: 135.8686, tz: 9, country: 'JP', nameJp: '滋賀 大津' },
  'Kyoto':       { lat: 35.0116, lng: 135.7681, tz: 9, country: 'JP', nameJp: '京都' },
  'Osaka':       { lat: 34.6937, lng: 135.5023, tz: 9, country: 'JP', nameJp: '大阪' },
  'Kobe':        { lat: 34.6901, lng: 135.1956, tz: 9, country: 'JP', nameJp: '兵庫 神戸' },
  'Nara':        { lat: 34.6851, lng: 135.8050, tz: 9, country: 'JP', nameJp: '奈良' },
  'Wakayama':    { lat: 34.2260, lng: 135.1675, tz: 9, country: 'JP', nameJp: '和歌山' },
  'Tottori':     { lat: 35.5039, lng: 134.2381, tz: 9, country: 'JP', nameJp: '鳥取' },
  'Matsue':      { lat: 35.4723, lng: 133.0505, tz: 9, country: 'JP', nameJp: '島根 松江' },
  'Okayama':     { lat: 34.6617, lng: 133.9350, tz: 9, country: 'JP', nameJp: '岡山' },
  'Hiroshima':   { lat: 34.3853, lng: 132.4553, tz: 9, country: 'JP', nameJp: '広島' },
  'Yamaguchi':   { lat: 34.1861, lng: 131.4706, tz: 9, country: 'JP', nameJp: '山口' },
  'Tokushima':   { lat: 34.0658, lng: 134.5593, tz: 9, country: 'JP', nameJp: '徳島' },
  'Takamatsu':   { lat: 34.3401, lng: 134.0434, tz: 9, country: 'JP', nameJp: '香川 高松' },
  'Matsuyama':   { lat: 33.8416, lng: 132.7657, tz: 9, country: 'JP', nameJp: '愛媛 松山' },
  'Kochi':       { lat: 33.5597, lng: 133.5311, tz: 9, country: 'JP', nameJp: '高知' },
  'Fukuoka':     { lat: 33.5904, lng: 130.4017, tz: 9, country: 'JP', nameJp: '福岡' },
  'Saga':        { lat: 33.2494, lng: 130.2988, tz: 9, country: 'JP', nameJp: '佐賀' },
  'Nagasaki':    { lat: 32.7503, lng: 129.8779, tz: 9, country: 'JP', nameJp: '長崎' },
  'Kumamoto':    { lat: 32.7898, lng: 130.7417, tz: 9, country: 'JP', nameJp: '熊本' },
  'Oita':        { lat: 33.2382, lng: 131.6126, tz: 9, country: 'JP', nameJp: '大分' },
  'Miyazaki':    { lat: 31.9111, lng: 131.4239, tz: 9, country: 'JP', nameJp: '宮崎' },
  'Kagoshima':   { lat: 31.5966, lng: 130.5571, tz: 9, country: 'JP', nameJp: '鹿児島' },
  'Naha':        { lat: 26.2124, lng: 127.6809, tz: 9, country: 'JP', nameJp: '沖縄 那覇' },

  // アジア
  'Seoul':      { lat: 37.5665, lng: 126.9780, tz: 9,   country: 'KR', nameJp: 'ソウル' },
  'Beijing':    { lat: 39.9042, lng: 116.4074, tz: 8,   country: 'CN', nameJp: '北京' },
  'Shanghai':   { lat: 31.2304, lng: 121.4737, tz: 8,   country: 'CN', nameJp: '上海' },
  'Hong Kong':  { lat: 22.3193, lng: 114.1694, tz: 8,   country: 'HK', nameJp: '香港' },
  'Taipei':     { lat: 25.0330, lng: 121.5654, tz: 8,   country: 'TW', nameJp: '台北' },
  'Bangkok':    { lat: 13.7563, lng: 100.5018, tz: 7,   country: 'TH', nameJp: 'バンコク' },
  'Singapore':  { lat: 1.3521,  lng: 103.8198, tz: 8,   country: 'SG', nameJp: 'シンガポール' },
  'Mumbai':     { lat: 19.0760, lng: 72.8777,  tz: 5.5, country: 'IN', nameJp: 'ムンバイ' },
  'Delhi':      { lat: 28.7041, lng: 77.1025,  tz: 5.5, country: 'IN', nameJp: 'デリー' },

  // ヨーロッパ
  'London':     { lat: 51.5074, lng: -0.1278,  tz: 0,   country: 'GB', nameJp: 'ロンドン' },
  'Paris':      { lat: 48.8566, lng: 2.3522,   tz: 1,   country: 'FR', nameJp: 'パリ' },
  'Berlin':     { lat: 52.5200, lng: 13.4050,  tz: 1,   country: 'DE', nameJp: 'ベルリン' },
  'Rome':       { lat: 41.9028, lng: 12.4964,  tz: 1,   country: 'IT', nameJp: 'ローマ' },
  'Madrid':     { lat: 40.4168, lng: -3.7038,  tz: 1,   country: 'ES', nameJp: 'マドリード' },
  'Moscow':     { lat: 55.7558, lng: 37.6173,  tz: 3,   country: 'RU', nameJp: 'モスクワ' },

  // 北米
  'New York':   { lat: 40.7128, lng: -74.0060, tz: -5,  country: 'US', nameJp: 'ニューヨーク' },
  'Los Angeles':{ lat: 34.0522, lng: -118.2437,tz: -8,  country: 'US', nameJp: 'ロサンゼルス' },
  'Chicago':    { lat: 41.8781, lng: -87.6298, tz: -6,  country: 'US', nameJp: 'シカゴ' },
  'San Francisco':{ lat: 37.7749, lng: -122.4194, tz: -8, country: 'US', nameJp: 'サンフランシスコ' },
  'Toronto':    { lat: 43.6532, lng: -79.3832, tz: -5,  country: 'CA', nameJp: 'トロント' },

  // オセアニア
  'Sydney':     { lat: -33.8688, lng: 151.2093, tz: 10, country: 'AU', nameJp: 'シドニー' },
  'Melbourne':  { lat: -37.8136, lng: 144.9631, tz: 10, country: 'AU', nameJp: 'メルボルン' },
  'Auckland':   { lat: -36.8485, lng: 174.7633, tz: 12, country: 'NZ', nameJp: 'オークランド' },

  // 南米
  'Sao Paulo':  { lat: -23.5505, lng: -46.6333, tz: -3, country: 'BR', nameJp: 'サンパウロ' },
  'Buenos Aires':{ lat: -34.6037, lng: -58.3816, tz: -3, country: 'AR', nameJp: 'ブエノスアイレス' },

  // アフリカ・中東
  'Cairo':      { lat: 30.0444, lng: 31.2357,  tz: 2,   country: 'EG', nameJp: 'カイロ' },
  'Dubai':      { lat: 25.2048, lng: 55.2708,  tz: 4,   country: 'AE', nameJp: 'ドバイ' },
  'Johannesburg':{ lat: -26.2041, lng: 28.0473, tz: 2,  country: 'ZA', nameJp: 'ヨハネスブルグ' },
};
