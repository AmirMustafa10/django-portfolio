document.addEventListener('DOMContentLoaded', () => {
    // Target the file input securely (works with Django's ClearableFileInput rendering)
    const fileInput = document.querySelector('.cover-upload input[type="file"]');
    const previewContainer = document.getElementById('new-cover-preview-container');
    const previewImage = document.getElementById('new-cover-preview-image');
    const previewFilename = document.getElementById('new-cover-preview-filename');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    previewImage.src = event.target.result;
                    previewFilename.textContent = file.name;
                    previewContainer.style.display = 'block';
                };
                
                reader.readAsDataURL(file);
            } else {
                // Reset if selection is cleared or invalid
                previewImage.src = '';
                previewFilename.textContent = '';
                previewContainer.style.display = 'none';
            }
        });
    }
});