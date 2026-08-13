function setupDeleteModal() {

    const deleteForm = document.getElementById("confirm-delete-form");
    const deleteType = document.getElementById("delete-item-type");
    const deleteName = document.getElementById("delete-item-name");

    if (!deleteForm) {
        return;
    }

    document.querySelectorAll(".btn-delete").forEach((button) => {

        button.addEventListener("click", function () {

            deleteForm.action = this.dataset.deleteUrl;

            if (deleteType) {
                deleteType.textContent =
                    this.dataset.deleteType || "";
            }

            if (deleteName) {
                deleteName.textContent =
                    this.dataset.deleteName || "";
            }

        });

    });
}


document.addEventListener("DOMContentLoaded", () => {
    setupDeleteModal();
});