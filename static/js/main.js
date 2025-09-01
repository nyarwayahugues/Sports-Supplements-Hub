// back to top
const backTop = document.getElementById('backTop');
window.addEventListener('scroll', () => {
  if (window.scrollY > 400) backTop.style.display = 'flex';
  else backTop.style.display = 'none';
});
backTop?.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));

// Quick view: fetch product partial or build from DOM (simple approach: fetch product endpoint)
const quickViewModal = document.getElementById('quickViewModal');
if (quickViewModal) {
  quickViewModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const id = button.getAttribute('data-id');
    const content = document.getElementById('quickViewContent');
    const whats = document.getElementById('quickViewWhats');

    content.innerHTML = 'Loading…';

    fetch(`/product/${id}`)
      .then(r => r.text())
      .then(html => {
        // The product_detail route returns full page — try to extract useful chunk or display html
        // For simplicity, replace content with returned page body (naive)
        content.innerHTML = html;
        // Update WhatsApp link inside returned content if needed
        const a = content.querySelector('a.whatsapp-link');
        if (a && whats) {
          whats.href = a.href;
        } else if (whats) {
          // fallback:
          whats.href = `/`;
        }
      })
      .catch(err => {
        content.innerHTML = '<div class="text-danger">Could not load product.</div>';
      });
  });
}
