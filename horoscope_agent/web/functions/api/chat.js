/**
 * Cloudflare Pages Function: Gemini API プロキシ
 * POST /api/chat
 */

const CORS_HEADERS = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

export async function onRequestOptions() {
  return new Response(null, { headers: CORS_HEADERS });
}

export async function onRequestPost(context) {
  const { env, request } = context;

  try {
    const body = await request.json();
    const { systemInstruction, contents } = body;

    if (!contents || !Array.isArray(contents)) {
      return jsonResponse({ error: 'contents array is required' }, 400);
    }

    // メッセージ数制限（乱用防止）
    if (contents.length > 30) {
      return jsonResponse({ error: 'Too many messages (max 30)' }, 400);
    }

    const model = env.GEMINI_MODEL || 'gemini-3.1-flash-lite-preview';
    const apiKey = env.GEMINI_API_KEY;

    if (!apiKey) {
      return jsonResponse({ error: 'API key not configured' }, 500);
    }

    const geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;

    const geminiBody = {
      contents,
      generationConfig: {
        maxOutputTokens: 2048,
        temperature: 0.9,
      },
    };

    if (systemInstruction) {
      geminiBody.systemInstruction = systemInstruction;
    }

    const geminiRes = await fetch(geminiUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(geminiBody),
    });

    const geminiData = await geminiRes.json();

    if (!geminiRes.ok) {
      return jsonResponse({ error: 'Gemini API error', detail: geminiData }, geminiRes.status);
    }

    // レスポンスからテキストを抽出
    const text = geminiData?.candidates?.[0]?.content?.parts?.[0]?.text || '';

    return jsonResponse({ text });
  } catch (err) {
    return jsonResponse({ error: err.message }, 500);
  }
}

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: {
      'Content-Type': 'application/json',
      ...CORS_HEADERS,
    },
  });
}
