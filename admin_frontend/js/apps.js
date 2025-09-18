// 同源部署：使用相对路径，无需 BASE_URL
let currentPage = 1;
let currentAppId = null;
let currentData = [];

document.addEventListener('DOMContentLoaded', function() {
  checkLoginStatus();
  bindEvents();
});

async function checkLoginStatus() {
  try {
    const response = await fetch(`/admin/applications/`, { credentials: 'include' });
    if (response.status === 401) { window.location.href = 'index.html'; return; }
    if (response.ok) { loadData(); } else { showMessage('服务器错误，请稍后重试', 'error'); }
  } catch (e) {
    showMessage('网络连接失败，请检查网络', 'error');
  }
}

function bindEvents() {
  document.getElementById('searchBtn').addEventListener('click', () => { currentPage = 1; loadData(); });
  document.getElementById('addBtn').addEventListener('click', () => { openEditModal(); });
  document.getElementById('logout').addEventListener('click', logout);
  document.getElementById('prevBtn').addEventListener('click', () => { if (currentPage > 1) { currentPage--; loadData(); } });
  document.getElementById('nextBtn').addEventListener('click', () => { currentPage++; loadData(); });
  document.getElementById('saveScoreBtn').addEventListener('click', saveScore);
  document.getElementById('saveRemarkBtn').addEventListener('click', saveRemark);
}

async function loadData() {
  try {
    showMessage('加载中...', 'info');
    const params = new URLSearchParams({ page: currentPage, page_size: 10 });
    const searchNumber = document.getElementById('searchNumber').value.trim();
    const searchName = document.getElementById('searchName').value.trim();
    const direction = document.getElementById('directionFilter').value;
    const grade = document.getElementById('gradeFilter').value;

    if (searchNumber) {
      const response = await fetch(`/admin/applications/result/?number=${searchNumber}`, { credentials: 'include' });
      const data = await response.json();
      if (data.success) { showMessage(`查询结果: ${data.message}`, 'success'); } else { showMessage(data.message, 'error'); }
      return;
    }

    if (searchName) {
      const response = await fetch(`/admin/applications/by-name/?name=${searchName}`, { credentials: 'include' });
      const data = await response.json();
      if (data.success) { currentData = data.data; renderTable(data.data); updateStats(data.data); clearMessage(); } else { showMessage(data.message, 'error'); }
      return;
    }

    if (direction) params.append('direction', direction);
    if (grade) params.append('grade', grade);

    const response = await fetch(`/admin/applications/?${params}`, { credentials: 'include' });
    if (response.status === 401) { showMessage('登录已过期，请重新登录', 'error'); setTimeout(() => { window.location.href = 'index.html'; }, 2000); return; }
    const data = await response.json();
    if (data.success) { currentData = data.data; renderTable(data.data); updatePagination(data.pagination); updateStats(data.data); clearMessage(); } else { showMessage(data.message || '加载失败', 'error'); }
  } catch (e) {
    showMessage('网络错误，请重试', 'error');
  }
}

function renderTable(data) {
  const tbody = document.getElementById('dataTable');
  if (data.length === 0) {
    tbody.innerHTML = `<tr><td colspan="9" style="text-align: center; padding: 40px; color: #999;"><i class="fas fa-inbox"></i> 暂无数据</td></tr>`;
    return;
  }
  tbody.innerHTML = data.map(app => `
    <tr>
      <td>${app.id}</td>
      <td>${app.name || '-'}</td>
      <td>${app.number || '-'}</td>
      <td>${app.grade || '-'}</td>
      <td>${app.major || '-'}</td>
      <td>
        <div class="actions">
          <a class="btn btn-primary" href="detail.html?id=${app.id}" title="查看详情"><i class="fas fa-eye"></i></a>
          <button class="btn btn-danger" onclick="deleteApp(${app.id})" title="删除"><i class="fas fa-trash"></i></button>
        </div>
      </td>
    </tr>`).join('');
}

function updatePagination(pagination) {
  const paginationEl = document.getElementById('pagination');
  const pageInfo = document.getElementById('pageInfo');
  const prevBtn = document.getElementById('prevBtn');
  const nextBtn = document.getElementById('nextBtn');
  if (pagination.total_pages <= 1) { paginationEl.style.display = 'none'; return; }
  paginationEl.style.display = 'flex';
  pageInfo.textContent = `第 ${pagination.current_page} 页，共 ${pagination.total_pages} 页`;
  prevBtn.disabled = pagination.current_page <= 1;
  nextBtn.disabled = pagination.current_page >= pagination.total_pages;
}

function updateStats(data) {
  const total = data.length;
  const scored = data.filter(app => app.value).length;
  const passed = data.filter(app => app.value && parseInt(app.value) >= 85).length;
  document.getElementById('totalCount').textContent = total;
  document.getElementById('scoredCount').textContent = scored;
  document.getElementById('passedCount').textContent = passed;
}

function openScoreModal(appId) { /* deprecated in slim table */ }
function openRemarkModal(appId) { /* deprecated in slim table */ }

async function saveScore() { /* deprecated in slim table */ }
async function saveRemark() { /* deprecated in slim table */ }

async function deleteApp(appId) {
  if (!confirm('确定要删除这条记录吗？')) return;
  try {
    const response = await fetch(`/admin/applications/${appId}/delete/`, { method: 'POST', credentials: 'include' });
    const data = await response.json();
    if (data.success) { showMessage('删除成功', 'success'); loadData(); } else { showMessage(data.message || '删除失败', 'error'); }
  } catch (e) { showMessage('网络错误', 'error'); }
}

async function logout() { try { await fetch(`/admin/auth/logout/`, { method: 'POST', credentials: 'include' }); window.location.href = 'index.html'; } catch (e) { window.location.href = 'index.html'; } }
function closeModal(modalId) { document.getElementById(modalId).classList.remove('show'); }
function showMessage(text, type = 'error') { const messageEl = document.getElementById('message'); messageEl.textContent = text; messageEl.className = `message ${type}`; messageEl.style.display = 'block'; if (type === 'success' || type === 'info') { setTimeout(() => { messageEl.style.display = 'none'; }, 3000); } }
function clearMessage() { document.getElementById('message').style.display = 'none'; }
document.addEventListener('click', function(e) { if (e.target.classList.contains('modal')) { e.target.classList.remove('show'); } });

