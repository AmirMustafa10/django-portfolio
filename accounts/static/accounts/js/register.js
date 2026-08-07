document.addEventListener('DOMContentLoaded', function() {
    // --- Setup for Django Form Fields ---
    // Ensure standard Django inputs get the form-control class
    const inputs = document.querySelectorAll('.form-group input');
    inputs.forEach(input => {
        input.classList.add('form-control');
        // If the field has an error (checked server side), add the invalid class
        if(input.nextElementSibling && input.nextElementSibling.classList.contains('invalid-feedback')) {
            input.classList.add('is-invalid');
        }
    });
    // --- Password Toggle Logic ---
    // Needs to dynamically target the password input based on Django's generated ID (usually id_password)
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
        // --- Password Strength & Requirements Logic ---
        const bar1 = document.getElementById('bar-1');
        const bar2 = document.getElementById('bar-2');
        const bar3 = document.getElementById('bar-3');
        const bar4 = document.getElementById('bar-4');
        const strengthText = document.getElementById('strengthText');
        
        const reqLength = document.getElementById('req-length');
        const reqNumber = document.getElementById('req-number');
        const reqSpecial = document.getElementById('req-special');
        function updateRequirementIcon(element, isValid) {
            if (isValid) {
                element.classList.remove('req-unmet');
                element.classList.add('req-met');
                element.innerHTML = '<path d="M9 12l2 2 4-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path><circle cx="12" cy="12" r="10" stroke-width="2"></circle>';
            } else {
                element.classList.remove('req-met');
                element.classList.add('req-unmet');
                element.innerHTML = '<circle cx="12" cy="12" r="10" stroke-width="2"></circle><path d="M9 12l2 2 4-4" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>';
            }
        }
        passwordInput.addEventListener('input', function() {
            const val = passwordInput.value;
            let strength = 0;
            
            // Check Requirements
            const hasLength = val.length >= 8;
            const hasNumber = /\d/.test(val);
            const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(val);
            const hasMixed = /[a-z]/.test(val) && /[A-Z]/.test(val);
            updateRequirementIcon(reqLength, hasLength);
            updateRequirementIcon(reqNumber, hasNumber);
            updateRequirementIcon(reqSpecial, hasSpecial);
            // Calculate Strength (0-4)
            if (val.length > 0) strength++;
            if (hasLength && hasNumber) strength++;
            if (hasLength && hasNumber && hasMixed) strength++;
            if (hasLength && hasNumber && hasMixed && hasSpecial) strength++;
            // Reset bars
            [bar1, bar2, bar3, bar4].forEach(bar => bar.style.backgroundColor = 'var(--border-light)');
            
            // Color mapping
            if (strength === 0) {
                strengthText.textContent = "Password strength";
                strengthText.style.color = "var(--text-muted)";
            } else if (strength === 1) {
                bar1.style.backgroundColor = "#ef4444"; // Red
                strengthText.textContent = "Weak";
                strengthText.style.color = "#ef4444";
            } else if (strength === 2) {
                bar1.style.backgroundColor = "#f59e0b"; // Orange
                bar2.style.backgroundColor = "#f59e0b";
                strengthText.textContent = "Fair";
                strengthText.style.color = "#f59e0b";
            } else if (strength === 3) {
                bar1.style.backgroundColor = "#eab308"; // Yellow
                bar2.style.backgroundColor = "#eab308";
                bar3.style.backgroundColor = "#eab308";
                strengthText.textContent = "Good";
                strengthText.style.color = "#eab308";
            } else if (strength >= 4) {
                bar1.style.backgroundColor = "#10b981"; // Green
                bar2.style.backgroundColor = "#10b981";
                bar3.style.backgroundColor = "#10b981";
                bar4.style.backgroundColor = "#10b981";
                strengthText.textContent = "Strong";
                strengthText.style.color = "#10b981";
            }
        });
    }
});