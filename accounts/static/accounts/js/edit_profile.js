document.addEventListener("DOMContentLoaded", () => {
  // --- 1. MODULAR SETUP ---
  initializeFormsets();
  setupFilePreviews();
  setupUnsavedChanges();
  handleDeletions();
  setupDeleteModal();

  // Ensure proper HTML attributes for Django fields
  document.querySelectorAll("input, select, textarea").forEach((el) => {
    if (
      !el.classList.contains("form-control") &&
      !el.classList.contains("form-select") &&
      !el.classList.contains("form-check-input")
    ) {
      if (el.tagName === "SELECT") {
        el.classList.add("form-select");
      } else if (el.type !== "checkbox" && el.type !== "hidden") {
        el.classList.add("form-control");
      }
    }

    // Add autocomplete off to URLs
    if (
      el.name === "github_url" ||
      el.name === "linkedin_url" ||
      el.name === "website_url"
    ) {
      el.setAttribute("autocomplete", "off");
    }
  });

  // --- 2. FORMSET MANAGEMENT ---
  function initializeFormsets() {
    // Add Skill
    const addSkillBtn = document.getElementById("add-skill-btn");
    const newSkillInput = document.getElementById("new-skill-input");

    if (addSkillBtn && newSkillInput) {
      addSkillBtn.addEventListener("click", () => {
        const val = newSkillInput.value.trim();

        if (!val) {
          return;
        }

        const newRow = addFormsetRow(
          "skills",
          "skills-empty-template",
          "skills-container",
        );

        const hiddenInput = newRow.querySelector('input[type="hidden"]');
        const displaySpan = newRow.querySelector(".skill-name-display");

        if (hiddenInput && displaySpan) {
          hiddenInput.value = val;
          displaySpan.textContent = val;
        }

        newSkillInput.value = "";
      });

      newSkillInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter") {
          e.preventDefault();
          addSkillBtn.click();
        }
      });
    }

    // Add Experience
    const addExpBtn = document.getElementById("add-experience-btn");

    if (addExpBtn) {
      addExpBtn.addEventListener("click", () => {
        addFormsetRow(
          "experience",
          "experience-empty-template",
          "experience-container",
        );
      });
    }

    // Add Education
    const addEduBtn = document.getElementById("add-education-btn");

    if (addEduBtn) {
      addEduBtn.addEventListener("click", () => {
        addFormsetRow(
          "education",
          "education-empty-template",
          "education-container",
        );
      });
    }
  }

  function addFormsetRow(prefix, templateId, containerId) {
    const container = document.getElementById(containerId);
    const template = document.getElementById(templateId).innerHTML;
    const totalFormsInput = document.getElementById(`id_${prefix}-TOTAL_FORMS`);

    const currentCount = parseInt(totalFormsInput.value);

    // Replace __prefix__ with the correct index
    const newHtml = template.replace(/__prefix__/g, currentCount);

    // Append and Increment TOTAL_FORMS
    container.insertAdjacentHTML("beforeend", newHtml);
    totalFormsInput.value = currentCount + 1;

    // Re-apply standard classes to newly injected fields
    const newRow = container.lastElementChild;

    newRow.querySelectorAll("input, select, textarea").forEach((el) => {
      if (el.tagName === "SELECT") {
        el.classList.add("form-select");
      } else if (el.type !== "checkbox" && el.type !== "hidden") {
        el.classList.add("form-control");
      }
    });

    window.isFormDirty = true;

    return newRow;
  }

  // --- 3. DELETIONS & UNDO (Event Delegation) ---
  function handleDeletions() {
    let itemToDelete = null;

    // Hide Django native DELETE checkboxes via class
    document
      .querySelectorAll('input[type="checkbox"][name$="-DELETE"]')
      .forEach((cb) => {
        cb.classList.add("django-delete-checkbox");
      });

    document.addEventListener("click", (e) => {
      // Handle Delete Trigger
      const deleteBtn = e.target.closest('[data-action="delete"]');

      if (deleteBtn) {
        const targetId = deleteBtn.dataset.target;
        const prefix = deleteBtn.dataset.prefix;
        const targetEl = document.getElementById(targetId);

        if (prefix === "skills") {
          processDelete(targetEl);
        } else {
          itemToDelete = targetEl;

          const modal = new bootstrap.Modal(
            document.getElementById("deleteModal"),
          );

          modal.show();
        }
      }

      // Handle Undo Trigger
      const undoBtn = e.target.closest('[data-action="undo"]');

      if (undoBtn) {
        const targetId = undoBtn.dataset.target;
        const targetEl = document.getElementById(targetId);

        if (targetEl) {
          const deleteInput = targetEl.querySelector(
            'input[type="checkbox"][name$="-DELETE"]',
          );

          if (deleteInput) {
            deleteInput.checked = false;
          }

          targetEl.classList.remove("d-none");

          undoBtn.closest(".undo-banner").remove();

          window.isFormDirty = true;
        }
      }
    });

    // Handle Modal Confirm
    const confirmDeleteBtn = document.getElementById("confirm-delete-btn");

    if (confirmDeleteBtn) {
      confirmDeleteBtn.addEventListener("click", () => {
        if (itemToDelete) {
          processDelete(itemToDelete);

          const modal = bootstrap.Modal.getInstance(
            document.getElementById("deleteModal"),
          );

          modal.hide();

          itemToDelete = null;
        }
      });
    }
  }

  function processDelete(element) {
    const deleteInput = element.querySelector(
      'input[type="checkbox"][name$="-DELETE"]',
    );

    const idInput = element.querySelector('input[type="hidden"][name$="-id"]');

    if (idInput && idInput.value) {
      // Existing DB record: check DELETE, hide visually, provide undo
      if (deleteInput) {
        deleteInput.checked = true;
      }

      element.classList.add("d-none");

      const undoHtml = `
        <div class="undo-banner">
          <span class="text-danger fw-medium">
            Item flagged for deletion.
          </span>

          <button
            type="button"
            class="btn btn-sm btn-outline-secondary rounded-3"
            data-action="undo"
            data-target="${element.id}"
          >
            Undo
          </button>
        </div>
      `;

      element.insertAdjacentHTML("afterend", undoHtml);
    } else {
      // Unsaved record: physically remove from DOM
      element.remove();
    }

    window.isFormDirty = true;
  }

  // --- 4. FILE PREVIEWS ---
  function setupFilePreviews() {
    // =========================
    // Avatar Preview
    // =========================

    const avatarUpload = document.getElementById("id_avatar");
    const avatarPreview = document.getElementById("avatarPreview");

    if (avatarUpload && avatarPreview) {
      avatarUpload.addEventListener("change", function () {
        const file = this.files[0];

        if (!file) {
          return;
        }

        // Validate image
        if (!file.type.startsWith("image/")) {
          alert("Please select a valid image.");
          this.value = "";
          return;
        }

        // Preview selected image
        const reader = new FileReader();

        reader.onload = function (e) {
          avatarPreview.src = e.target.result;
        };

        reader.readAsDataURL(file);

        window.isFormDirty = true;
      });
    }

    // =========================
    // Resume Preview
    // =========================

    const resumeUpload = document.getElementById("id_resume");
    const resumeNameDisplay = document.getElementById("resumeNameDisplay");

    if (resumeUpload && resumeNameDisplay) {
      resumeUpload.addEventListener("change", function () {
        const file = this.files[0];

        if (!file) {
          return;
        }

        // Allowed file extensions
        const allowedExtensions = [".pdf", ".doc", ".docx"];

        const fileName = file.name.toLowerCase();

        const isValid = allowedExtensions.some((extension) =>
          fileName.endsWith(extension),
        );

        // Validate resume
        if (!isValid) {
          alert("Please select a PDF, DOC, or DOCX file.");
          this.value = "";
          return;
        }

        // Show selected file
        resumeNameDisplay.innerHTML = `
                <span class="text-main fw-medium text-truncate">
                    Selected file: ${file.name}
                </span>
            `;

        window.isFormDirty = true;
      });
    }
  }

  // --- 5. UNSAVED CHANGES & UX ALERTS ---
  function setupUnsavedChanges() {
    window.isFormDirty = false;

    const profileForm = document.getElementById("profile-edit-form");

    if (!profileForm) {
      return;
    }

    profileForm.addEventListener("input", () => {
      window.isFormDirty = true;
    });

    profileForm.addEventListener("change", () => {
      window.isFormDirty = true;
    });

    window.addEventListener("beforeunload", (e) => {
      if (window.isFormDirty) {
        e.preventDefault();
        e.returnValue = "";
      }
    });

    // Disable dirty check on legitimate submit
    profileForm.addEventListener("submit", () => {
      window.isFormDirty = false;
    });

    // "Current" Switch logic (Disable End Date)
    document.addEventListener("change", (e) => {
      if (e.target.matches('input[type="checkbox"][name$="is_current"]')) {
        const card = e.target.closest(".nested-card");

        if (!card) {
          return;
        }

        const endDateInput = card.querySelector(
          'input[name$="end_date"], input[name$="end_year"]',
        );

        if (endDateInput) {
          endDateInput.disabled = e.target.checked;

          if (e.target.checked) {
            endDateInput.value = "";
          }
        }
      }
    });
  }
});

const addSkillBtn = document.getElementById("add-skill-btn");
const newSkillInput = document.getElementById("new-skill-input");
const skillsList = document.querySelector(".skills-container");

if (addSkillBtn && newSkillInput && skillsList) {
  addSkillBtn.addEventListener("click", function () {
    const skillName = newSkillInput.value.trim();

    if (!skillName) {
      return;
    }

    const skillId = `new-${Date.now()}`;

    const label = document.createElement("label");

    label.innerHTML = `
            <input
                type="checkbox"
                name="skills"
                value="${skillId}"
                checked
                data-new-skill="true"
            >

            ${skillName}

            <input
                type="hidden"
                name="new_skills"
                value="${skillName}"
            >
        `;

    skillsList.appendChild(label);

    newSkillInput.value = "";

    window.isFormDirty = true;
  });
}


function setupDeleteModal() {
    const deleteForm = document.getElementById("confirm-delete-form");
    const deleteType = document.getElementById("delete-item-type");
    const deleteName = document.getElementById("delete-item-name");

    if (!deleteForm) {
        return;
    }

    document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", function () {
            deleteForm.action = this.dataset.deleteUrl;

            deleteType.textContent = this.dataset.deleteType || "";
            deleteName.textContent = this.dataset.deleteName || "";
        });
    });
}