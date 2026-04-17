// 보호자 서류 종류 셀렉트 변경 시 파일 업로드 라벨 동기화
document.querySelector('#doc-guardian-type')?.addEventListener('change', (e) => {
  const label = document.querySelector('#doc-family-label');
  label.textContent = e.target.options[e.target.selectedIndex].text;
});

// 봉사자, 보호자 탭 전환 및 서류 필드 토글
document.querySelectorAll('.tab[data-role]').forEach(tab => {
  tab.addEventListener('click', () => {
    // 모든 탭에서 active 클래스 제거
    document.querySelectorAll('.tab[data-role]').forEach(t => t.classList.remove('active'));
    // 클릭한 탭에만 active 추가
    tab.classList.add('active');
    // 'role' 입력칸에 tab에 있는 role값 넣기
    document.querySelector('#role').value = tab.dataset.role;

    const selectedRole = tab.dataset.role;
    document.querySelectorAll('[data-role-doc]').forEach(el => {
      el.classList.toggle('hidden', el.dataset.roleDoc !== selectedRole);
    });  // 서류 칸들 중 선택된 역할과 다른건 hidden
  });
});

// 회원가입 폼 제출
document.querySelector('#register-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();  // 원래 submit 하면 새로고침하는데 직접 fetch할거니까 막기

  const password = document.querySelector('#password').value;
  const passwordConfirm = document.querySelector('#password-confirm').value;
  const errorMsg = document.querySelector('#error-msg');
  // 백엔드 요청 보내기 전에 걸러주는것(1차 ux). schemas로 백엔드에서 한번 더 검증(2차 보안).
  if (password !== passwordConfirm) {
    errorMsg.textContent = '비밀번호가 일치하지 않습니다.';
    errorMsg.classList.remove('hidden');
    return;
  }

  errorMsg.classList.add('hidden');

  try {  // api.js의 api() 함수 호출
    await api('/users/register', {
      method: 'POST',
      // html inpust 값들을 json 변환해서 백엔드에 전송
      body: JSON.stringify({
        email: document.querySelector('#email').value,
        password,
        password_confirm: passwordConfirm,
        name: document.querySelector('#name').value,
        phone_number: document.querySelector('#phone').value,
        user_role: document.querySelector('#role').value,
        address: document.querySelector('#district').value,
      }),
    });

    // 성공하면 login.html로 이동
    window.location.href = '/pages/login.html';
  } catch (err) {  // 실패하면 에러 메시지
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  }
});
