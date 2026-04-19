// 페이지 진입 시 유저 정보 (일반/카카오 로그인별 비밀번호 변경폼 노출 여부)
(async () => {
  try {
    const me = await api('/users/me');
    if (me.is_social_login) {
      document.querySelector('.detail-section:has(#password-form)')?.remove();
    }
  } catch {
    // 토큰 없거나 만료되면 비밀번호 변경폼 그냥 표시
  }
})();

// 비밀번호 변경폼 제출 처리
// password-form 제출되면 이 함수 실행
document.querySelector('#password-form')?.addEventListener('submit', async (e) => {
  e.preventDefault(); // preventDefault: 페이지 새로고침 막기, ?: null이면 뒤를 실행하지 않고 넘어감

  const errorMsg = document.querySelector('#password-error');
  const successMsg = document.querySelector('#password-success');
  errorMsg.classList.add('hidden');
  successMsg.classList.add('hidden');
  // 제출할때마다 이전에 떠있던 알림창 먼저 숨기기

  // 3개의 input 값들
  const currentPassword = document.querySelector('#current-password').value;
  const newPassword = document.querySelector('#new-password').value;
  const newPasswordConfirm = document.querySelector('#new-password-confirm').value;

  // 현재 비밀번호와 새 비밀번호가 같으면 경고 알림창
  if (currentPassword === newPassword) {
    errorMsg.textContent = '새 비밀번호가 현재 비밀번호와 같습니다.';
    errorMsg.classList.remove('hidden');
    return;
  }

  // 새 비밀번호 일치 확인 (클라이언트 검증 = js 브라우저 검증)
  if (newPassword !== newPasswordConfirm) {
    errorMsg.textContent = '새 비밀번호가 일치하지 않습니다.';
    errorMsg.classList.remove('hidden');
    return;  // 함수 즉시 종료
  }

  try {  // api() 호출(jwt 토큰 자동)
    await api('/users/me/password', {
      method: 'PATCH',  // PATCH: 일부 수정(지금 비밀번호 변경처럼 바꿀 필드만 보냄)
      body: JSON.stringify({
        current_password: currentPassword,
        new_password: newPassword,
        new_password_confirm: newPasswordConfirm,
      }),
    });

    successMsg.textContent = '비밀번호가 변경되었어요.';
    successMsg.classList.remove('hidden');
    e.target.reset(); // 성공하면 초록알림창과 함께 폼 초기화
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  }  // 실패하면 빨간알림창(api.js꺼 갖다써서 에러메시지 파싱 잘됨)
});

// 로그아웃 버튼 클릭
document.querySelector('#logout-btn')?.addEventListener('click', () => {
  logout();  // logout도 api.js에 있음(토큰 삭제후 로그인 페이지 이동)
});

// 회원 탈퇴 버튼 클릭
document.querySelector('#delete-btn')?.addEventListener('click', async () => {
  if (!confirm('정말 탈퇴하시겠어요? 모든 정보가 삭제되며 복구할 수 없습니다.')) return;
  try {
    await api('/users/me', { method: 'DELETE' });
    localStorage.removeItem('access_token');
    window.location.href = '/pages/login.html';
  } catch (err) {
    alert(err.message);
  }
});