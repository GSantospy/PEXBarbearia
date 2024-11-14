document.addEventListener('DOMContentLoaded', () => {
    const senhaToggles = [
        { toggleId: 'toggleSenha', inputId: 'senhaNova' },
        { toggleId: 'toggleConfirmarSenha', inputId: 'senhaNovaConfirmar' },
        { toggleId: 'senhaLogin', inputId: 'senha' },
        { toggleId: 'toggleCadastro', inputId: 'senha'},
        { toggleId: 'togglePerfil', inputId: 'senhaUsuario'}
        
    ];

    senhaToggles.forEach(({ toggleId, inputId }) => {
        const toggle = document.getElementById(toggleId);
        const input = document.getElementById(inputId);

        if (toggle && input) {
            toggle.addEventListener('click', () => {
                const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
                input.setAttribute('type', type);
                toggle.classList.toggle('bi-eye');
                toggle.classList.toggle('bi-eye-slash');
            });
        }
    });
});
