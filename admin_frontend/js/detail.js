// 同源相对路径
function qs(key) { const u = new URL(window.location.href); return u.searchParams.get(key); }

document.addEventListener('DOMContentLoaded', async function() {
  const id = qs('id');
  if (!id) { show('error','缺少参数 id'); return; }
  await loadDetail(id);
  document.getElementById('saveScoreBtn').addEventListener('click', () => saveScore(id));
  document.getElementById('saveRemarkBtn').addEventListener('click', () => saveRemark(id));
  document.getElementById('logout').addEventListener('click', logout);
});

async function loadDetail(id) {
  try {
    const res = await fetch(`/admin/applications/${id}/`, { credentials: 'include' });
    if (res.status === 401) { window.location.href = 'index.html'; return; }
    const data = await res.json();
    if (!data.success) { show('error', data.message || '加载失败'); return; }
    render(data.data || data);
  } catch (e) {
    show('error', '网络错误');
  }
}

function render(obj) {
  const d = document.getElementById('detail');
  d.innerHTML = `
    <div class="section">
      <h3>个人基本信息</h3>
      <div class="grid-2">
        ${tile('姓名', obj.name)}
        ${tile('学号', obj.number)}
        ${tile('专业班级', obj.major)}
        ${tile('年级', obj.grade)}
        ${tile('手机号', obj.phone_number)}
        ${tile('邮箱', obj.email)}
        ${tile('报名时间', obj.created_at)}
      </div>
    </div>

    <div class="section">
      <h3>成绩与特长</h3>
      <table class="kv-table">
        <tr><th>高考数学成绩</th><td>${nv(obj.gaokao_math)}</td></tr>
        <tr><th>高考英语成绩</th><td>${nv(obj.gaokao_english)}</td></tr>
        <tr><th>擅长领域</th><td>${nv(obj.good_at)}</td></tr>
        <tr><th>意向方向</th><td>${nv(obj.follow_direction)}</td></tr>
        <tr><th>项目经历</th><td>${br(nv(obj.experience))}</td></tr>
        <tr><th>当前分数</th><td>${obj.value ? `${obj.value}分` : '未评分'}</td></tr>
      </table>
    </div>

    <div class="section">
      <h3>详细说明</h3>
      <table class="kv-table">
        <tr><th>报名原因</th><td>${br(nv(obj.reason))}</td></tr>
        <tr><th>其他实验室报名情况</th><td>${br(nv(obj.other_lab))}</td></tr>
        <tr><th>未来发展</th><td>${br(nv(obj.future))}</td></tr>
        <tr><th>当前备注</th><td>${br(nv(obj.admin_remark))}</td></tr>
      </table>
    </div>
  `;
}

function tile(label, value){ return `<div class="tile"><div class="label">${label}</div><div class="value">${nv(value)}</div></div>`; }
function nv(v){ return (v===undefined || v===null || v==='') ? '-' : v; }
function br(t){ return String(t).replace(/\n/g,'<br>'); }

async function saveScore(id) {
  const score = parseInt(document.getElementById('scoreInput').value || '');
  if (!score || score < 1 || score > 100) { show('error','请输入 1-100 的分数'); return; }
  try {
    const res = await fetch(`/admin/applications/${id}/score/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ score })
    });
    const data = await res.json();
    if (data.success) { show('success','评分成功'); loadDetail(id); }
    else { show('error', data.message || '评分失败'); }
  } catch (e) { show('error','网络错误'); }
}

async function saveRemark(id) {
  const remark = (document.getElementById('remarkInput').value || '').trim();
  try {
    const res = await fetch(`/admin/applications/${id}/remark/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ remark })
    });
    const data = await res.json();
    if (data.success) { show('success','备注已保存'); }
    else { show('error', data.message || '保存失败'); }
  } catch (e) { show('error','网络错误'); }
}

async function logout(e) { e?.preventDefault?.(); try { await fetch(`/admin/auth/logout/`, { method:'POST', credentials:'include' }); window.location.href='index.html'; } catch { window.location.href='index.html'; } }

function show(type, text){ const box = document.getElementById('message'); box.className = `message ${type}`; box.textContent = text; box.style.display = 'block'; if(type!=='error'){ setTimeout(()=>box.style.display='none', 2000); } }
