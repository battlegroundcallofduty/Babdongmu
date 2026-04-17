// 보호자 서류 종류 셀렉트 변경 시 파일 업로드 라벨 동기화
document.querySelector('#doc-guardian-type')?.addEventListener('change', (e) => {
  const label = document.querySelector('#doc-family-label');
  label.textContent = e.target.options[e.target.selectedIndex].text;
});

// 봉사자, 보호자 탭 전환 및 서류 필드 토글
document.querySelectorAll('.tab[data-role]').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab[data-role]').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.querySelector('#role').value = tab.dataset.role;

    const selectedRole = tab.dataset.role;
    document.querySelectorAll('[data-role-doc]').forEach(el => {
      el.classList.toggle('hidden', el.dataset.roleDoc !== selectedRole);
    });
  });
});

// 파일 선택 시 파일명 표시
document.querySelectorAll('input[type="file"]').forEach(input => {
  input.addEventListener('change', () => {
    const span = input.closest('label').querySelector('.doc-upload-text');
    span.textContent = input.files[0] ? input.files[0].name : '파일 선택';
  });
});

// 파일 업로드 함수
// 파일은 바이너리라 json에 못담아서 multipart 씀
async function uploadDocument(token, documentType, file) {
  const formData = new FormData();  // FormData: multipart 요청 만들어줌
  formData.append('document_type', documentType); // 텍스트 필드 -> Form(...)
  formData.append('file', file);                  // 파일 필드 -> File(...)

  // api() 대신 fetch 직접 사용
  // api(): content-type json 강제로 붙임. boundary 값 못 넣음
  // fetch: content-type 자동 설정, boundary값 같이 들어감 -> multipart 요청은 파싱 때문에 파일경계값 필요
  const response = await fetch('/api/v1/users/me/documents', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` },  // 토큰만 직접 설정
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: '서류 업로드에 실패했어요.' }));
    const detail = error.detail;
    // api() 에러 처리 그대로 가져옴
    const message = Array.isArray(detail)
      ? detail.map(d => d.msg.replace(/^Value error,\s*/i, '')).join(', ')
      : (detail || '서류 업로드에 실패했어요.');
    throw new Error(message);
  }
  return response.json();
}

// 회원가입 폼 제출
document.querySelector('#register-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const password = document.querySelector('#password').value;
  const passwordConfirm = document.querySelector('#password-confirm').value;
  const errorMsg = document.querySelector('#error-msg');

  if (password.length < 8) {
    errorMsg.textContent = '비밀번호는 8자 이상이어야 합니다.';
    errorMsg.classList.remove('hidden');
    return;
  }

  if (password !== passwordConfirm) {
    errorMsg.textContent = '비밀번호가 일치하지 않습니다.';
    errorMsg.classList.remove('hidden');
    return;
  }

  // 신분증 사본을 필수로 체크해서 제출서류 0개 방지하도록
  const idFile = document.querySelector('#doc-id').files[0];
  if (!idFile) {  // 파일 안 골랐다면(undefined)
    errorMsg.textContent = '신분증 사본은 필수입니다.';
    errorMsg.classList.remove('hidden');
    return;  // 제출 막고 함수 종료
  }

  errorMsg.classList.add('hidden');

  try {
    // 1) 회원가입 → 유저 정보 반환
    const result = await api('/users/register', {
      method: 'POST',
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

    // 2) 토큰 저장 (서류 업로드 시 인증에 필요)
    saveToken(result.access_token);  // localstorage에 토큰 저장
    const token = result.access_token;
    const role = document.querySelector('#role').value;

    // 3) 신분증 사본 업로드 (공통 필수)
    await uploadDocument(token, 'identity_copy', idFile);

    // 4) 역할별 추가 서류 업로드 (선택)
    if (role === 'volunteer') {
      const criminalFile = document.querySelector('#doc-criminal').files[0];
      if (criminalFile) {  // 선택했을때만 업로드 (선택 안해도 가입가능)
        await uploadDocument(token, 'criminal_record', criminalFile);
      }
    } else if (role === 'guardian') {
      const guardianFile = document.querySelector('#doc-family').files[0];
      if (guardianFile) {
        // 셀렉트박스 값이 DocumentType enum 값과 이름 똑같아서 그대로 넘김
        const guardianType = document.querySelector('#doc-guardian-type').value;
        await uploadDocument(token, guardianType, guardianFile);
      }
    }

    window.location.href = '/pages/login.html';
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  }
});
