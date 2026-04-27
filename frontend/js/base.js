const favicon = document.createElement('link');
favicon.rel = 'icon';
favicon.href = '/favicon.ico';
favicon.type = 'image/x-icon';
document.head.appendChild(favicon);

async function loadFooter() {
  try {
    const res = await fetch('/base/footer.html');
    const html = await res.text();
    const placeholder = document.querySelector('#footer-placeholder');
    if (placeholder) placeholder.innerHTML = html;
  } catch (err) {
    console.error('footer 로드 실패', err);
  }
}

loadFooter();
