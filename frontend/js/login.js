// 회원가입 직후 넘어온 경우 안내 메시지 표시
if (new URLSearchParams(window.location.search).get('registered') === '1') {
  document.getElementById('register-notice').classList.remove('hidden');
}

// 이메일/비밀번호 로그인
document.querySelector('#login-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const errorMsg = document.querySelector('#error-msg');
  errorMsg.classList.add('hidden');

  try { // api.js의 api() 반환값을 data에 저장
    const data = await api('/users/login', {
      method: 'POST',
      body: JSON.stringify({
        email: document.querySelector('#email').value,
        password: document.querySelector('#password').value,
      }),
    });

    // 토큰 꺼내서 저장
    saveToken(data.access_token);

    // 유저 role 조회 후 페이지 이동
    const user = await api('/users/me');
    if (user.user_role === 'admin') {
      window.location.href = '/pages/admin.html';
    } else if (user.user_role === 'guardian') {
      window.location.href = '/pages/guardian.html';
    } else {
      window.location.href = '/pages/hostings.html';
    }
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  }
});
