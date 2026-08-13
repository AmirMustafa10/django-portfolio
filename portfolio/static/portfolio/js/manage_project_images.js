// <!-- 20. VANILLA JS FOR NEW IMAGE PREVIEWS -->
    document.addEventListener('DOMContentLoaded', () => {
        const fileInput = document.getElementById('project-images');
        const previewContainer = document.getElementById('new-images-container');
        const previewGrid = document.getElementById('new-images-preview-grid');

        if (!fileInput || !previewContainer || !previewGrid) return;

        fileInput.addEventListener('change', function(e) {
            // Clear previous previews
            previewGrid.innerHTML = '';
            
            const files = e.target.files;
            
            if (files.length === 0) {
                previewContainer.style.display = 'none';
                return;
            }

            previewContainer.style.display = 'block';

            Array.from(files).forEach((file, index) => {
                // Ensure the selected file is actually an image (Client-side UI check)
                if (!file.type.match('image.*')) {
                    return; 
                }

                const reader = new FileReader();

                reader.onload = function(e) {
                    const imgUrl = e.target.result;
                    const fileName = file.name;
                    const imageIndex = index + 1;

                    // Create the preview card HTML
                    const cardHtml = `
                        <div class="col">
                            <article class="image-card new-image-card h-100 d-flex flex-column shadow-sm">
                                <div class="position-relative">
                                    <img src="${imgUrl}" alt="New image preview ${imageIndex}" class="image-preview-img">
                                    <span class="position-absolute top-0 start-0 m-2 image-badge new-badge shadow-sm">
                                        New #${imageIndex}
                                    </span>
                                </div>
                                <div class="p-3 bg-surface flex-grow-1">
                                    <p class="new-filename m-0 text-truncate" title="${fileName}">${fileName}</p>
                                </div>
                            </article>
                        </div>
                    `;

                    // Append to grid
                    previewGrid.insertAdjacentHTML('beforeend', cardHtml);
                };

                reader.readAsDataURL(file);
            });
        });
    });

// <!-- 21. BIND DELETE BUTTONS TO SHARED MODAL -->
    document.addEventListener('DOMContentLoaded', () => {
        const deleteButtons = document.querySelectorAll('.delete-btn[data-delete-url]');
        const deleteForm = document.getElementById('confirm-delete-form');
        const deleteNameTarget = document.getElementById('deleteItemName');
        const deleteTypeTarget = document.getElementById('deleteItemType');

        deleteButtons.forEach(btn => {
            btn.addEventListener('click', function() {
                const url = this.getAttribute('data-delete-url');
                const name = this.getAttribute('data-delete-name');
                const type = this.getAttribute('data-delete-type');

                // Bind URL to form action
                if (deleteForm && url) {
                    deleteForm.action = url;
                }
                
                // Update Modal text
                if (deleteNameTarget && name) {
                    deleteNameTarget.textContent = name;
                }
                if (deleteTypeTarget && type) {
                    deleteTypeTarget.textContent = type.toLowerCase();
                }
            });
        });
    });
