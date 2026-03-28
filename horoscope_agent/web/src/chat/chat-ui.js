/**
 * チャットUI — DOM生成・イベント処理
 */

import { createChatSession, sendMessage } from './chat-api.js';

let session = null;
let aiResponseCount = 0;

/**
 * チャットUIを初期化・表示
 * @param {Object} lastResult - 計算結果
 */
export function initChatUI(lastResult) {
  // 既にチャットパネルがあれば表示するだけ
  const existing = document.getElementById('chat-panel');
  if (existing) {
    existing.style.display = 'block';
    return;
  }

  session = createChatSession(lastResult);
  aiResponseCount = 0;

  const panel = buildChatPanel();
  const chartSection = document.getElementById('chart-section');
  chartSection.parentElement.after(panel);

  // 初回メッセージを自動送信
  handleSend('この星図を鑑定してください');
}

function buildChatPanel() {
  const panel = document.createElement('div');
  panel.id = 'chat-panel';
  panel.className = 'section';
  panel.innerHTML = `
    <div class="section-header">AI 星図鑑定</div>
    <div class="section-body" style="padding: 0;">
      <div id="chat-messages" style="
        height: 400px;
        overflow-y: auto;
        padding: 16px;
        display: flex;
        flex-direction: column;
        gap: 12px;
      "></div>

      <div id="chat-quick-replies" style="
        display: flex;
        gap: 8px;
        padding: 8px 16px;
        flex-wrap: wrap;
      ">
        <button class="chat-quick-btn" data-msg="恋愛運について教えてください">恋愛運</button>
        <button class="chat-quick-btn" data-msg="仕事運について教えてください">仕事運</button>
        <button class="chat-quick-btn" data-msg="金運について教えてください">金運</button>
        <button class="chat-quick-btn" data-msg="健康運について教えてください">健康運</button>
        <button class="chat-quick-btn" data-msg="総合的なアドバイスをお願いします">総合運</button>
      </div>

      <div style="display: flex; gap: 8px; padding: 12px 16px; border-top: 1px solid rgba(255,255,255,0.1);">
        <input type="text" id="chat-input" placeholder="質問を入力..." style="
          flex: 1;
          background: rgba(255,255,255,0.05);
          border: 1px solid rgba(255,255,255,0.15);
          border-radius: 6px;
          padding: 8px 12px;
          color: var(--color-text, #e0e0e0);
          font-size: 14px;
        ">
        <button id="chat-send-btn" style="
          padding: 8px 20px;
          white-space: nowrap;
        ">送信</button>
      </div>

      <div id="chat-pdf-area" style="display: none; padding: 12px 16px; text-align: center;">
        <button id="chat-pdf-btn" class="btn-primary" style="width: 100%;">診断書を発行する（PDF）</button>
      </div>
    </div>
  `;

  // イベント設定
  const sendBtn = panel.querySelector('#chat-send-btn');
  const input = panel.querySelector('#chat-input');

  sendBtn.addEventListener('click', () => {
    const text = input.value.trim();
    if (text) {
      input.value = '';
      handleSend(text);
    }
  });

  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.isComposing) {
      e.preventDefault();
      const text = input.value.trim();
      if (text) {
        input.value = '';
        handleSend(text);
      }
    }
  });

  // クイック返信ボタン
  for (const btn of panel.querySelectorAll('.chat-quick-btn')) {
    btn.addEventListener('click', () => {
      handleSend(btn.dataset.msg);
    });
  }

  return panel;
}

async function handleSend(text) {
  const messages = document.getElementById('chat-messages');
  const sendBtn = document.getElementById('chat-send-btn');
  const input = document.getElementById('chat-input');

  // ユーザーメッセージ表示（初回自動メッセージは表示しない）
  if (aiResponseCount > 0 || text !== 'この星図を鑑定してください') {
    appendMessage(messages, 'user', text);
  }

  // タイピングインジケーター
  const typing = document.createElement('div');
  typing.className = 'chat-msg chat-msg--ai';
  typing.textContent = '鑑定中...';
  typing.style.opacity = '0.5';
  messages.appendChild(typing);
  messages.scrollTop = messages.scrollHeight;

  // 入力を無効化
  sendBtn.disabled = true;
  input.disabled = true;

  try {
    const response = await sendMessage(session, text);
    typing.remove();
    appendMessage(messages, 'ai', response);
    aiResponseCount++;

    // 2回目以降のAI応答でPDFボタンを表示
    if (aiResponseCount >= 2) {
      const pdfArea = document.getElementById('chat-pdf-area');
      if (pdfArea) pdfArea.style.display = 'block';
    }
  } catch (err) {
    typing.remove();
    appendMessage(messages, 'ai', `エラーが発生しました: ${err.message}`);
  }

  sendBtn.disabled = false;
  input.disabled = false;
  input.focus();
}

function appendMessage(container, role, text) {
  const div = document.createElement('div');
  div.className = `chat-msg chat-msg--${role}`;

  if (role === 'ai') {
    // 改行をbrに変換、段落分け
    div.innerHTML = text
      .split('\n\n')
      .map(p => `<p style="margin: 0 0 8px 0;">${p.replace(/\n/g, '<br>')}</p>`)
      .join('');
  } else {
    div.textContent = text;
  }

  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

/**
 * チャットの会話履歴を取得（PDF生成用）
 * @returns {Array} 会話履歴
 */
export function getChatHistory() {
  return session ? session.contents : [];
}
