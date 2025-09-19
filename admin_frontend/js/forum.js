let page = 1;

document.addEventListener('DOMContentLoaded', () => {
  load();
  document.getElementById('prevBtn').addEventListener('click', ()=>{ if(page>1){ page--; load(); }});
  document.getElementById('nextBtn').addEventListener('click', ()=>{ page++; load(); });
});

async function load(){
  try{
    const res = await fetch(`/admin/forum/posts/?page=${page}`, { credentials: 'include' });
    if(res.status===401){ window.location.href='index.html'; return; }
    const data = await res.json();
    if(!data.success){ show('error', data.message||'加载失败'); return; }
    render(data.data);
    updatePager(data.pagination);
  }catch(e){ show('error','网络错误'); }
}

function render(list){
  const tb = document.getElementById('postTable');
  if(!list || list.length===0){ tb.innerHTML = `<tr><td colspan="8" style="text-align:center; padding:40px; color:#999;">暂无数据</td></tr>`; return; }
  tb.innerHTML = list.map(p=>`
    <tr>
      <td>
        <div class="actions">
          <button class="btn btn-primary" onclick="pin(${p.id})" title="置顶/取消置顶"><i class="fas fa-thumbtack"></i></button>
          <button class="btn btn-success" onclick="feature(${p.id})" title="加精/取消加精"><i class="fas fa-star"></i></button>
          <button class="btn btn-danger" onclick="del(${p.id})" title="删除"><i class="fas fa-trash"></i></button>
        </div>
      </td>
      <td>${p.id}</td>
      <td>${escapeHtml(p.title)}</td>
      <td>${p.user_id||'-'}</td>
      <td>${p.is_sticky? '√':'-'}</td>
      <td>${p.is_featured? '√':'-'}</td>
      <td>${p.comment_count||0}</td>
      <td>${p.created_at||''}</td>
    </tr>
  `).join('');
}

async function pin(id){ await action(`/admin/forum/posts/${id}/pin/`); }
async function feature(id){ await action(`/admin/forum/posts/${id}/feature/`); }
async function del(id){ if(!confirm('确定删除该帖子吗？')) return; await action(`/admin/forum/posts/${id}/delete/`); }

async function action(url){
  try{
    const res = await fetch(url, { method:'POST', credentials:'include' });
    const data = await res.json();
    if(data.success){ show('success','操作成功'); load(); }
    else { show('error', data.message||'操作失败'); }
  }catch(e){ show('error','网络错误'); }
}

function updatePager(p){ const el=document.getElementById('pagination'); if(!p){ el.style.display='none'; return; } el.style.display='flex'; document.getElementById('pageInfo').textContent = `第 ${p.current_page} 页 / 共 ${p.total_pages} 页`; }

function show(type, text){ const box=document.getElementById('message'); box.className=`message ${type}`; box.textContent=text; box.style.display='block'; if(type!=='error'){ setTimeout(()=>box.style.display='none',2000);} }
function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[c])); }
