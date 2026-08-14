document.addEventListener('DOMContentLoaded', () => {
    // Minimal JS for binding Delete buttons to the shared #deleteModal.
    // Assumes a global `#deleteModal` and `#confirm-delete-form` exist in `base.html`.
    const deleteButtons = document.querySelectorAll('.btn-delete[data-delete-url]');
    const deleteForm = document.getElementById('confirm-delete-form');
    const deleteNameTarget = document.getElementById('deleteItemName'); 
    const deleteTypeTarget = document.getElementById('deleteItemType'); 
    deleteButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const url = this.getAttribute('data-delete-url');
            const name = this.getAttribute('data-delete-name');
            const type = this.getAttribute('data-delete-type');
            if (deleteForm) {
                deleteForm.action = url;
            }
            if (deleteNameTarget && name) {
                deleteNameTarget.textContent = name;
            }
            if (deleteTypeTarget && type) {
                deleteTypeTarget.textContent = type.toLowerCase();
            }
        });
    });
});