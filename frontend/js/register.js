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

// 파일 업로드 함수(파일: json에 못담아서 multipart 씀)
async function uploadDocument(token, documentType, file) {
  const formData = new FormData();  // FormData: multipart 요청 생성
  formData.append('document_type', documentType);
  formData.append('file', file);

  // api(): content-type json 강제. boundary값 X
  // fetch: content-type 자동 설정, boundary값 O(multipart: 파싱 때문에 파일경계값 필요)
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
    err.status = response.status;  // http 상태 코드를 에러 객체에 담음(catch용)
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

  errorMsg.classList.add('hidden');

  let token = null; // catch에서 가입 성공 판단 위해 try 바깥에 선언

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
    token = result.access_token;
    // saveToken 삭제 → 회원가입 후 자동 로그인 방지, 서류 업로드엔 token 변수 직접 사용
    const role = document.querySelector('#role').value;

    // 3) 신분증 사본 업로드 (선택)
    const idFile = document.querySelector('#doc-id').files[0];
    if (idFile) {
      await uploadDocument(token, 'identity_copy', idFile);
    }

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

    window.location.href = '/pages/login.html?registered=1';
  } catch (err) {
    if (token) {
      // 서류는 회원가입 필수값이 아님
      // 서류 업로드 실패해도 계정유지(가입처리), 로그인 후 마이페이지에서 재업로드 가능
      // TODO: R2에만 올라가고 DB 연결 안 된 파일(orphan)은 백엔드 스케줄러에서 주기적으로 정리 예정
      // 503: R2 서버 문제 → 안내 문구로 표시
      // 400: 형식 오류/크기 초과 → 백엔드 메시지(유저가 수정할수있도록)
      const msg = err.status === 503
        ? '서류 업로드에 실패했습니다.\n가입은 완료됐으니 로그인 후 마이페이지에서 다시 업로드해주세요.'
        : `서류 업로드 오류: ${err.message}\n가입은 완료됐으니 로그인 후 마이페이지에서 다시 업로드해주세요.`;
      alert(msg);
      window.location.href = '/pages/login.html';
    } else {
      errorMsg.textContent = err.message;
      errorMsg.classList.remove('hidden');
    }
  }
});
