/**
 * システムプロンプト構築
 * lastResult からチャートデータを抽出し、AI占星術師用のプロンプトを生成
 */

/**
 * チャートデータからGemini systemInstruction を構築
 * @param {Object} lastResult - 計算結果オブジェクト
 * @returns {Object} Gemini systemInstruction 形式
 */
export function buildSystemPrompt(lastResult) {
  const { bodies, houses, aspects, dignities, lunarPhase, extraPoints } = lastResult;

  // --- 天体情報 ---
  const planetLines = [];
  const mainPlanets = ['sun', 'moon', 'mercury', 'venus', 'mars', 'jupiter', 'saturn', 'uranus', 'neptune', 'pluto', 'chiron'];
  for (const key of mainPlanets) {
    const b = bodies[key];
    if (!b) continue;
    const sign = b.sign?.nameJp || '不明';
    const deg = Math.floor(b.degreeInSign || 0);
    const house = b._house || '?';
    const retro = b.retrograde ? '（逆行中）' : '';
    planetLines.push(`${b.nameJp}: ${sign} ${deg}° / ${house}室${retro}`);
  }

  // --- ASC / MC ---
  const asc = houses?.angles?.ascendant;
  const mc = houses?.angles?.mc;
  const ascSign = asc?.sign?.nameJp || '不明';
  const mcSign = mc?.sign?.nameJp || '不明';

  // --- 主要アスペクト（オーブ5°以内に絞る）---
  const tightAspects = (aspects || [])
    .filter(a => a.orb <= 5)
    .sort((a, b) => a.orb - b.orb)
    .slice(0, 15);

  const aspectLines = tightAspects.map(a => {
    const b1 = a.body1?.nameJp || a.body1?.key;
    const b2 = a.body2?.nameJp || a.body2?.key;
    return `${b1} ${a.aspectNameJp || a.aspect} ${b2}（orb ${a.orb.toFixed(1)}°）`;
  });

  // --- 品位 ---
  const dignityLines = [];
  if (dignities) {
    for (const [key, d] of Object.entries(dignities)) {
      if (d.dignity !== 'none' && d.dignityJp) {
        const b = bodies[key];
        dignityLines.push(`${b?.nameJp || key}: ${d.dignityJp}`);
      }
    }
  }

  // --- 月相 ---
  const phase = lunarPhase?.nameJp || '不明';

  // --- プロンプト組み立て ---
  const prompt = `あなたは「星図鑑定師」です。西洋占星術の深い知識を持つプロフェッショナルな占星術師として、以下のネイタルチャートデータに基づいて鑑定を行ってください。

【ネイタルチャート】
ASC（上昇宮）: ${ascSign}
MC（天頂）: ${mcSign}

${planetLines.join('\n')}

【主要アスペクト】
${aspectLines.length > 0 ? aspectLines.join('\n') : 'なし'}

【品位】
${dignityLines.length > 0 ? dignityLines.join('\n') : '特になし'}

【月相】
${phase}

【鑑定ルール】
1. 初回は挨拶と共に、太陽・月・ASCの三大要素から全体像を読み解いてください
2. ユーザーの質問に応じて、関連するハウスや天体を具体的に引用してください
   - 恋愛 → 7室・金星・月を中心に
   - 仕事 → 10室・MC・土星を中心に
   - 金運 → 2室・8室・木星を中心に
   - 健康 → 6室・ASC・火星を中心に
3. 日本語で温かみのある、でも的確な口調で鑑定してください
4. 1回の回答は300〜500文字程度にしてください
5. 具体的な天体配置を根拠として示してください（「あなたの金星は○○座の△室にあるため〜」のように）
6. 占い師らしい表現を使いつつ、論理的な根拠も示してください`;

  return {
    parts: [{ text: prompt }],
  };
}
