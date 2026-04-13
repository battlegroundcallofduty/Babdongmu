// 봉사자/보호자 탭 전환 및 서류 필드 토글
document.querySelectorAll('.tab[data-role]').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab[data-role]').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById('role').value = tab.dataset.role;

    const selectedRole = tab.dataset.role;
    document.querySelectorAll('[data-role-doc]').forEach(el => {
      el.classList.toggle('hidden', el.dataset.roleDoc !== selectedRole);
    });
  });
});

// 회원가입 폼 제출
document.getElementById('register-form')?.addEventListener('submit', async (e) => {
  e.preventDefault();

  const password = document.getElementById('password').value;
  const passwordConfirm = document.getElementById('password-confirm').value;
  const errorMsg = document.getElementById('error-msg');

  if (password !== passwordConfirm) {
    errorMsg.textContent = '비밀번호가 일치하지 않습니다.';
    errorMsg.classList.remove('hidden');
    return;
  }

  errorMsg.classList.add('hidden');

  try {
    await api('/users/register', {
      method: 'POST',
      body: JSON.stringify({
        email: document.getElementById('email').value,
        password,
        password_confirm: passwordConfirm,
        name: document.getElementById('name').value,
        phone_number: document.getElementById('phone').value,
        user_role: document.getElementById('role').value,
        address: document.getElementById('district').value,
      }),
    });

    window.location.href = '/pages/login.html';
  } catch (err) {
    errorMsg.textContent = err.message;
    errorMsg.classList.remove('hidden');
  }
});
