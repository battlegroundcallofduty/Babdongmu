// 회원가입 직후 넘어온 경우 안내 메시지 표시
if (new URLSearchParams(window.location.search).get('registered') === '1') {
  document.getElementById('register-notice').classList.remove('hidden');
}

// 이메일/비밀번호 로그인
document.querySelector('#login-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const errorMsg = document.querySelector('#error-msg');
  errorMsg.classList.add('hidden');

  try {
    const data = await api('/users/login', {
      method: 'POST',
      body: JSON.stringify({
        email: document.querySelector('#email').value,
        password: document.querySelector('#password').value,
      }),
    });

    console.log('login response:', data);
    
    // access token 저장, 이전 세션 캐시 클리어
    saveToken(data.access_token);
    sessionStorage.removeItem('cachedUser');
    
    // 현재 로그인 사용자 정보 조회
    const user = await api('/users/me');
    
    // User_role 값 문자열화 + 소문자 변환 + 공백 제거 
    const normalizedRole = String(user.user_role ?? '').trim().toLowerCase();
    
    // authGuard.js가 쓰는 currentUser 저장
    localStorage.setItem(
      'currentUser',
      JSON.stringify({
        user_id: user.user_id,
        name: user.name,
        user_role: normalizedRole,
      }),
    );

    // cert_flag 미승인(guardian/volunteer)은 마이페이지로 — 서류 제출 필요
    if (normalizedRole !== 'admin' && user.cert_flag !== 'approved') {
      window.location.replace('/pages/mypage.html');
      return;
    }

    // 역할별 페이지 이동
    // 로그인 페이지를 히스토리에 남기지 않아서 뒤로가기 동작이 덜 꼬일 수 있음(replace)
    if (normalizedRole === 'admin') {
      window.location.replace('/pages/admin.html');
      return;
    }

    if (normalizedRole === 'guardian') {
      window.location.replace('/pages/guardian.html');
      return;
    }

    if (normalizedRole === 'volunteer') {
      window.location.replace('/pages/hosting-match.html');
      return;
    }

    throw new Error(`알 수 없는 user_role: ${user.user_role}`);
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  }
});