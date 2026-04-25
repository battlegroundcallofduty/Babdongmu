const favicon = document.createElement('link');
favicon.rel = 'icon';
favicon.href = '/favicon.ico';
favicon.type = 'image/x-icon';
document.head.appendChild(favicon);

fetch('/base/footer.html')
  .then(res => res.text())
  .then(html => {
    const placeholder = document.getElementById('footer-placeholder');
    if (placeholder) placeholder.innerHTML = html;
  });
