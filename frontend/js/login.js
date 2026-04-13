// 이메일/비밀번호 로그인
document.getElementById('login-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const errorMsg = document.getElementById('error-msg');
  errorMsg.classList.add('hidden');

  try { // api.js의 api() 반환값을 data에 저장
    const data = await api('/users/login', {
      method: 'POST',
      body: JSON.stringify({
        email: document.getElementById('email').value,
        password: document.getElementById('password').value,
      }),
    });
    
    // 토큰 꺼내서 저장
    saveToken(data.access_token);
    // 이후 메인(/)으로 이동. 실패하면 에러 메시지
    window.location.href = '/';
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  }
});
