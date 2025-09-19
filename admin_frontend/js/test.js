const BASE_URL = 'https://csecl.zeabur.app';

function showResult(elementId, data, isSuccess = true) {
  const element = document.getElementById(elementId);
  element.textContent = JSON.stringify(data, null, 2);
  element.className = `result ${isSuccess ? 'success' : 'error'}`;
}

async function testConnection() {
  try {
    const response = await fetch(`${BASE_URL}/admin/`, { credentials: 'include' });
    const data = await response.json();
    showResult('connectionResult', { status: response.status, success: response.ok, data }, response.ok);
  } catch (error) {
    showResult('connectionResult', { error: error.message, message: '无法连接到后端服务器' }, false);
  }
}

async function testLogin() {
  try {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const response = await fetch(`${BASE_URL}/admin/auth/login/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, credentials: 'include', body: JSON.stringify({ username, password }) });
    const data = await response.json();
    showResult('loginResult', { status: response.status, success: response.ok, data }, response.ok);
  } catch (error) {
    showResult('loginResult', { error: error.message, message: '登录请求失败' }, false);
  }
}

async function testApplications() {
  try {
    const response = await fetch(`${BASE_URL}/admin/applications/`, { credentials: 'include' });
    const data = await response.json();
    showResult('applicationsResult', { status: response.status, success: response.ok, data }, response.ok);
  } catch (error) {
    showResult('applicationsResult', { error: error.message, message: '获取报名列表失败' }, false);
  }
}

async function testSearchByName() {
  try {
    const name = document.getElementById('searchName').value;
    const response = await fetch(`${BASE_URL}/admin/applications/by-name/?name=${name}`, { credentials: 'include' });
    const data = await response.json();
    showResult('searchResult', { status: response.status, success: response.ok, data }, response.ok);
  } catch (error) {
    showResult('searchResult', { error: error.message, message: '姓名搜索失败' }, false);
  }
}

async function testSearchByNumber() {
  try {
    const number = document.getElementById('searchNumber').value;
    const response = await fetch(`${BASE_URL}/admin/applications/result/?number=${number}`, { credentials: 'include' });
    const data = await response.json();
    showResult('numberResult', { status: response.status, success: response.ok, data }, response.ok);
  } catch (error) {
    showResult('numberResult', { error: error.message, message: '学号查询失败' }, false);
  }
}

window.addEventListener('load', testConnection);

