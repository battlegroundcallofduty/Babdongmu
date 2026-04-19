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
    const message = Array.isArray(detail)
      ? detail.map(d => d.msg.replace(/^Value error,\s*/i, '')).join(', ')
      : (detail || '서류 업로드에 실패했어요.');
    const err = new Error(message);
    err.status = response.status;  // http 상태 코드를 에러 객체에 담음(catch에서 꺼내쓰려고)
    throw err;
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

  let token = null; // catch에서 롤백 여부 판단하기 위해 try 바깥에 선언

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
    token = result.access_token; // 여기서 설정되면 회원가입 성공한 것
    // saveToken 삭제 → 회원가입 후 자동 로그인 방지, 서류 업로드엔 token 변수 직접 사용
    const role = document.querySelector('#role').value;

    // 3) 신분증 사본 업로드 (공통 필수)
    await uploadDocument(token, 'identity_copy', idFile);

    // 4) 역할별 추가 서류 업로드 (선택)
    if (role === 'volunteer') {
      const criminalFile = document.querySelector('#doc-criminal').files[0];
      if (criminalFile) {
        await uploadDocument(token, 'criminal_record', criminalFile);
      }
    } else if (role === 'guardian') {
      const guardianFile = document.querySelector('#doc-family').files[0];
      if (guardianFile) {
        const guardianType = document.querySelector('#doc-guardian-type').value;
        await uploadDocument(token, guardianType, guardianFile);
      }
    }

    window.location.href = '/pages/login.html';
  } catch (err) {
    // token이 있다는 건 회원가입은 성공했지만 서류 업로드가 실패한 것
    // → 유저 삭제 롤백
    if (token) {
      // api()는 localStorage에서 토큰 읽는데 saveToken 안 했으니 직접 fetch로 토큰 넘김
      await fetch('/api/v1/users/me', {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` },
      }).catch(() => {});
      localStorage.removeItem('access_token');
      token = null;
      // 503: R2 서버 문제 → 기술 메시지 숨기고 안내 문구로 표시
      // 400: 형식 오류/크기 초과 → 백엔드 메시지 그대로 (유저가 고칠수있도록 뭔지 알려줌)
      errorMsg.textContent = err.status === 503 // 조건 ? 참일때값 : 거짓일때값
        ? '서버 오류로 업로드에 실패했습니다. 잠시 후 다시 시도해주세요.'
        : `${err.message} 알맞은 파일을 다시 선택해주세요.`;  // f-string이랑 비슷
    } else {
      errorMsg.textContent = err.message;
    }
    errorMsg.classList.remove('hidden');
  }
});
