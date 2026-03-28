/**
 * チャットAPI通信・会話履歴管理
 */

import { buildSystemPrompt } from './chat-prompt.js';

/**
 * チャットセッションを初期化
 * @param {Object} lastResult - 計算結果
 * @returns {Object} セッションオブジェクト
 */
export function createChatSession(lastResult) {
  return {
    systemInstruction: buildSystemPrompt(lastResult),
    contents: [],
  };
}

/**
 * メッセージを送信し、AI応答を取得
 * @param {Object} session - セッションオブジェクト（変更される）
 * @param {string} userMessage - ユーザーのメッセージ
 * @returns {Promise<string>} AI応答テキスト
 */
export async function sendMessage(session, userMessage) {
  // ユーザーメッセージを履歴に追加
  session.contents.push({
    role: 'user',
    parts: [{ text: userMessage }],
  });

  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      systemInstruction: session.systemInstruction,
      contents: session.contents,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || `API error: ${res.status}`);
  }

  const data = await res.json();
  const text = data.text || '申し訳ございません。鑑定結果を取得できませんでした。';

  // AI応答を履歴に追加
  session.contents.push({
    role: 'model',
    parts: [{ text }],
  });

  return text;
}
