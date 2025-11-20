const steps = document.querySelectorAll('.step');
const validateForm = document.getElementById('validate-form');
const tokenForm = document.getElementById('token-form');
const resultEl = document.getElementById('result');
const cardInput = document.getElementById('card-input');
const tokenInput = document.getElementById('token-input');
const validateHint = document.getElementById('validate-hint');
const issueForm = document.getElementById('issue-form');
const cardsList = document.getElementById('cards-list');
const refreshButton = document.getElementById('refresh-cards');

let currentCardKey = '';

function setStep(activeIndex) {
  steps.forEach((step, index) => {
    step.classList.toggle('step-active', index === activeIndex);
  });
}

function showMessage(message, type = 'success') {
  resultEl.textContent = message;
  resultEl.className = `result ${type}`;
}

async function postJSON(url, payload) {
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || '请求失败');
  }
  return data;
}

validateForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const cardKey = cardInput.value.trim();
  if (!cardKey) return;

  validateHint.textContent = '正在验证，请稍候...';
  showMessage('');

  try {
    const data = await postJSON('/api/validate', { cardKey });
    if (!data.valid) {
      validateHint.textContent = data.message || '验证失败';
      setStep(0);
      tokenForm.classList.add('hidden');
      showMessage(data.message || '卡密不可用', 'error');
      return;
    }
    currentCardKey = cardKey;
    tokenForm.classList.remove('hidden');
    tokenInput.focus();
    setStep(1);
    validateHint.textContent = '验证通过，继续录入 Token。';
    showMessage('卡密验证成功，请继续录入 Token。', 'success');
  } catch (error) {
    validateHint.textContent = error.message;
    showMessage(error.message, 'error');
  }
});

tokenForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const token = tokenInput.value.trim();
  if (!currentCardKey) {
    showMessage('请先验证卡密', 'error');
    return;
  }
  if (!token) {
    showMessage('请输入 token 内容', 'error');
    return;
  }

  showMessage('正在提交...');

  try {
    await postJSON('/api/tokens', { cardKey: currentCardKey, token });
    setStep(2);
    tokenForm.reset();
    validateForm.reset();
    tokenForm.classList.add('hidden');
    showMessage('Token 已收录，流程完成。', 'success');
  } catch (error) {
    showMessage(error.message, 'error');
  }
});

issueForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const prefix = document.getElementById('issue-prefix').value.trim() || 'VIP';
  const count = Number(document.getElementById('issue-count').value) || 1;
  const validDays = Number(document.getElementById('issue-days').value) || 30;

  const submitBtn = issueForm.querySelector('button[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = '生成中...';

  try {
    const data = await postJSON('/api/cards', { prefix, count, valid_days: validDays });
    renderNewKeys(data.keys || []);
    await fetchCards();
  } catch (error) {
    alert(error.message);
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = '生成卡密';
  }
});

refreshButton.addEventListener('click', async () => {
  refreshButton.disabled = true;
  refreshButton.textContent = '刷新中...';
  await fetchCards();
  refreshButton.disabled = false;
  refreshButton.textContent = '刷新列表';
});

async function fetchCards() {
  try {
    const res = await fetch('/api/cards');
    const data = await res.json();
    renderCardList(data.cards || []);
  } catch (error) {
    console.error('加载卡密列表失败', error);
  }
}

function renderCardList(cards) {
  if (!cards.length) {
    cardsList.innerHTML = '<div class="muted">暂无卡密，请先生成。</div>';
    return;
  }

  cardsList.innerHTML = cards
    .slice()
    .reverse()
    .map((card) => {
      const status = card.status === 'used' ? '已使用' : '未使用';
      const badgeClass = card.status === 'used' ? 'warn' : 'success';
      const expires = card.expires_at ? `有效期至 ${card.expires_at.split('T')[0]}` : '不限期';
      return `<div class="card-item">\
        <div>\
          <div class="card-key">${card.key}</div>\
          <div class="card-status">${expires}</div>\
        </div>\
        <div class="badge ${badgeClass}">${status}</div>\
      </div>`;
    })
    .join('');
}

function renderNewKeys(keys) {
  if (!keys.length) return;
  const items = keys.map((key) => `<div class="badge success">${key}</div>`).join('');
  showMessage(`生成成功：${items}`, 'success');
}

fetchCards();
