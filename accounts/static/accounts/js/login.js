document.addEventListener('DOMContentLoaded', function() {
    // --- Setup for Django Form Fields ---
    const inputs = document.querySelectorAll('.form-group input:not([type="checkbox"])');
    inputs.forEach(input => {
        input.classList.add('form-control');
        // If the field has an error (checked server side), add the invalid class
        if(input.nextElementSibling && input.nextElementSibling.classList.contains('invalid-feedback')) {
            input.classList.add('is-invalid');
        }
    });
    // --- Password Toggle Logic ---
    const passwordInput = document.querySelector('input[name="password"]');
    const toggleBtn = document.getElementById('togglePassword');
    const eyeIcon = document.getElementById('eyeIcon');
    
    // SVG paths for Eye and Eye-Off
    const pathEye = '<path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>';
    const pathEyeOff = '<path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"></path>';
    if (passwordInput && toggleBtn) {
        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            eyeIcon.innerHTML = type === 'password' ? pathEye : pathEyeOff;
        });
    }
});