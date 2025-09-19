// 同源部署：使用相对路径，无需 BASE_URL

document.addEventListener('DOMContentLoaded', function() {
  bindEvents();
  loadHistory();
});

function bindEvents() {
  document.getElementById('announceForm').addEventListener('submit', handleSubmit);
  document.getElementById('previewBtn').addEventListener('click', showPreview);
  document.getElementById('logout').addEventListener('click', logout);
  document.getElementById('releaseResultsBtn').addEventListener('click', releaseResults);
  document.getElementById('hideResultsBtn').addEventListener('click', hideResults);
  document.getElementById('message').addEventListener('input', function() {
    if (this.value.trim()) { showPreview(); } else { hidePreview(); }
  });
}

function selectRecipient(value) {
  document.querySelectorAll('.recipient-option').forEach(option => { option.classList.remove('selected'); });
  event.currentTarget.classList.add('selected');
  document.getElementById(value).checked = true;
}

function showPreview() {
  const message = document.getElementById('message').value.trim();
  if (!message) { hidePreview(); return; }
  const preview = document.getElementById('preview');
  const previewContent = document.getElementById('previewContent');
  previewContent.innerHTML = `
    <div style="margin-bottom: 10px;">
      <strong>📢 系统公告</strong>
      <span style="color: #666; font-size: 12px; margin-left: 10px;">${new Date().toLocaleString()}</span>
    </div>
    <div>${message.replace(/\n/g, '<br>')}</div>
  `;
  preview.style.display = 'block';
}

function hidePreview() { document.getElementById('preview').style.display = 'none'; }

async function handleSubmit(e) {
  e.preventDefault();
  const message = document.getElementById('message').value.trim();
  const recipient = document.querySelector('input[name="recipient"]:checked').value;
  const customRecipients = document.getElementById('customRecipients').value.trim();
  if (!message) { showMessage('请输入公告内容', 'error'); return; }
  const submitBtn = document.getElementById('submitBtn');
  submitBtn.disabled = true; submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发布中...';
  try {
    let recipientUserIds = null;
    if (customRecipients) { recipientUserIds = customRecipients.split(',').map(id => id.trim()).filter(id => id); }
    const response = await fetch(`/admin/announcements/`, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include',
      body: JSON.stringify({ message, recipient_user_ids: recipientUserIds, recipient_type: recipient })
    });
    const data = await response.json();
    if (data.success) { showMessage('公告发布成功！', 'success'); document.getElementById('announceForm').reset(); hidePreview(); loadHistory(); }
    else { showMessage(data.message || '发布失败', 'error'); }
  } catch (e) {
    showMessage('网络错误，请重试', 'error');
  } finally {
    submitBtn.disabled = false; submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> 发布公告';
  }
}

async function loadHistory() {
  try {
    const historyList = document.getElementById('historyList');
    historyList.innerHTML = `<div style="text-align: center; padding: 40px; color: #999;"><i class=\"fas fa-spinner fa-spin\"></i> 加载中...</div>`;
    const resp = await fetch('/admin/announcements/list/', { credentials: 'include' });
    if (resp.status === 401) { historyList.innerHTML = '<div style="text-align:center;padding:40px;color:#999;">请先登录</div>'; return; }
    const data = await resp.json();
    if (!data.success || !Array.isArray(data.data) || data.data.length === 0) {
      historyList.innerHTML = `<div style="text-align: center; padding: 40px; color: #999;"><i class=\"fas fa-info-circle\"></i> 暂无历史公告</div>`;
      return;
    }
    historyList.innerHTML = data.data.map(item => `
      <div class="history-item">
        <h4>📢 系统公告</h4>
        <div class="meta">${new Date(item.created_at).toLocaleString()}${item.recipient_user_id ? ` · 定向用户 ${item.recipient_user_id}` : ' · 广播'} </div>
        <div class="content">${String(item.message || '').replace(/\n/g,'<br>')}</div>
      </div>
    `).join('');
  } catch (e) { const historyList = document.getElementById('historyList'); historyList.innerHTML = `<div style="text-align:center;padding:40px;color:#999;">加载失败</div>`; }
}

async function releaseResults() {
  if (!confirm('确定要发布面试结果吗？发布后学生可以查询成绩。')) return;
  try {
    const response = await fetch('/admin/results/release/', { method: 'POST', credentials: 'include' });
    const data = await response.json();
    if (data.success) { showMessage(data.message, 'success'); } else { showMessage(data.message, 'error'); }
  } catch (e) { showMessage('网络错误', 'error'); }
}

async function hideResults() {
  if (!confirm('确定要隐藏面试结果吗？隐藏后学生无法查询成绩。')) return;
  try {
    const response = await fetch('/admin/results/hide/', { method: 'POST', credentials: 'include' });
    const data = await response.json();
    if (data.success) { showMessage(data.message, 'success'); } else { showMessage(data.message, 'error'); }
  } catch (e) { showMessage('网络错误', 'error'); }
}

async function logout() { try { await fetch(`/admin/auth/logout/`, { method: 'POST', credentials: 'include' }); window.location.href = 'index.html'; } catch (e) { window.location.href = 'index.html'; } }
function showMessage(text, type = 'error') { const messageEl = document.getElementById('message'); messageEl.textContent = text; messageEl.className = `message ${type}`; messageEl.style.display = 'block'; if (type === 'success') { setTimeout(() => { messageEl.style.display = 'none'; }, 3000); } }

