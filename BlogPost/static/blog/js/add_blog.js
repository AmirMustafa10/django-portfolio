document.addEventListener('DOMContentLoaded', () => {
    // We find the input by searching for type="file" inside the cover-upload area
    // to robustly support Django's default rendering of FileInput.
    const fileInput = document.querySelector('.cover-upload input[type="file"]');
    const previewContainer = document.getElementById('cover-preview-container');
    const previewImage = document.getElementById('cover-preview-image');
    const previewFilename = document.getElementById('cover-preview-filename');
    const emptyText = document.getElementById('cover-empty-text');
    if (fileInput) {
        // Add custom class for styling the file input properly
        fileInput.classList.add('form-control-file');
        
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                
                reader.onload = function(event) {
                    previewImage.src = event.target.result;
                    previewFilename.textContent = file.name;
                    previewContainer.style.display = 'block';
                    emptyText.style.display = 'none';
                };
                
                reader.readAsDataURL(file);
            } else {
                // Reset if no valid image selected
                previewImage.src = '';
                previewFilename.textContent = '';
                previewContainer.style.display = 'none';
                emptyText.style.display = 'block';
            }
        });
    }
});