// main.js — run after DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Modal functionality
    const modals = {
        login: document.getElementById('loginModal'),
        register: document.getElementById('registerModal')
    };

    // Open modals
    const navLink = document.querySelector('.nav-link');
    if (navLink) {
        navLink.addEventListener('click', (e) => {
            e.preventDefault();
            openModal('login');
        });
    }

    const btnCadastrar = document.getElementById('btnCadastrar');
    if (btnCadastrar) {
        btnCadastrar.addEventListener('click', () => {
            openModal('register');
        });
    }

    const btnJunte = document.getElementById('btnJunte');
    if (btnJunte) {
        btnJunte.addEventListener('click', () => {
            openModal('register');
        });
    }

    // Switch between modals
    const linkCadastro = document.getElementById('linkCadastro');
    if (linkCadastro) {
        linkCadastro.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal('login');
            openModal('register');
        });
    }

    const linkLogin = document.getElementById('linkLogin');
    if (linkLogin) {
        linkLogin.addEventListener('click', (e) => {
            e.preventDefault();
            closeModal('register');
            openModal('login');
        });
    }

    // Close buttons
    document.querySelectorAll('.close').forEach(btn => {
        btn.addEventListener('click', function() {
            closeModal(this.dataset.modal);
        });
    });

    // Close on outside click
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.classList.remove('active');
        }
    });

    // Form submissions (MODIFICADO CONFORME IMAGEM)
    // No formulário de LOGIN (dentro do evento submit):
    const loginForm = document.querySelector('#loginModal .form');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Simular login bem-sucedido
            window.location.href = 'dashboard.html';
        });
    }

    // No formulário de CADASTRO (dentro do evento submit):
    const registerForm = document.querySelector('#registerModal .form');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            e.preventDefault();
            // Simular cadastro bem-sucedido
            alert('Conta criada com sucesso!');
            window.location.href = 'dashboard.html';
        });
    }

    function openModal(type) {
        const modal = type === 'login' ? modals.login : modals.register;
        if (modal) modal.classList.add('active');
    }

    function closeModal(modalId) {
        const modalEl = document.getElementById(modalId);
        if (modalEl) modalEl.classList.remove('active');
    }
});