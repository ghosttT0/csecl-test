// 同源部署：使用相对路径，无需 BASE_URL
const messageEl = document.getElementById('message');
const loginBtn = document.getElementById('loginBtn');
const loginForm = document.getElementById('loginForm');

function showMessage(text, type = 'error') {
  messageEl.textContent = text;
  messageEl.className = `message ${type}`;
}

function clearMessage() {
  messageEl.textContent = '';
  messageEl.className = 'message';
}

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();

  const username = document.getElementById('username').value.trim();
  const password = document.getElementById('password').value;

  if (!username || !password) {
    showMessage('请输入用户名和密码');
    return;
  }

  clearMessage();
  loginBtn.disabled = true;
  loginBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 登录中...';

  try {
    const response = await fetch(`/admin/auth/login/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ username, password })
    });

    const data = await response.json();
    if (response.ok && data.success) {
      showMessage('登录成功，正在跳转...', 'success');
      setTimeout(() => { window.location.href = 'apps.html'; }, 1000);
    } else {
      showMessage(data.message || `登录失败 (${response.status})`);
    }
  } catch (error) {
    console.error('Login error:', error);
    showMessage('网络连接错误，请检查网络后重试');
  } finally {
    loginBtn.disabled = false;
    loginBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> 登录';
  }
});

document.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') {
    loginForm.dispatchEvent(new Event('submit'));
  }
});

// removed Liquid Ether effect per request
