document.addEventListener('DOMContentLoaded', () => {
    
    // VANILLA JS FOR COMMENTS (Event Delegation for performance)
    const commentsSection = document.getElementById('comments-section');
    if (!commentsSection) return;
    commentsSection.addEventListener('click', async (e) => {
        
        // --- A) TOGGLE INLINE REPLY FORM ---
        const btnReplyToggle = e.target.closest('.btn-reply-toggle');
        if (btnReplyToggle) {
            const targetId = btnReplyToggle.getAttribute('aria-controls');
            const formWrapper = document.getElementById(targetId);
            
            if (formWrapper) {
                // Close all other open reply forms first for a clean UX
                document.querySelectorAll('.reply-form-wrapper:not(.d-none)').forEach(el => {
                    if(el.id !== targetId) el.classList.add('d-none');
                });
                
                formWrapper.classList.toggle('d-none');
                
                if (!formWrapper.classList.contains('d-none')) {
                    const textarea = formWrapper.querySelector('textarea');
                    if (textarea) textarea.focus();
                }
            }
            return;
        }
        // --- B) CANCEL REPLY FORM ---
        const btnReplyCancel = e.target.closest('.btn-reply-cancel');
        if (btnReplyCancel) {
            const formWrapper = btnReplyCancel.closest('.reply-form-wrapper');
            if (formWrapper) {
                formWrapper.classList.add('d-none');
                const textarea = formWrapper.querySelector('textarea');
                if (textarea) textarea.value = ''; // clear input
            }
            return;
        }
        // --- C) VIEW / HIDE NESTED REPLIES & LAZY LOADING ---
        const btnViewReplies = e.target.closest('.btn-view-replies');
        if (btnViewReplies) {
            const targetId = btnViewReplies.getAttribute('aria-controls');
            const repliesContainer = document.getElementById(targetId);
            const isExpanded = btnViewReplies.getAttribute('aria-expanded') === 'true';
            const count = btnViewReplies.getAttribute('data-reply-count');
            const textSpan = btnViewReplies.querySelector('.toggle-text');
            const icon = btnViewReplies.querySelector('.toggle-icon');
            if (repliesContainer) {
                if (isExpanded) {
                    // Action: Hide
                    repliesContainer.classList.add('d-none');
                    btnViewReplies.setAttribute('aria-expanded', 'false');
                    if(icon) icon.classList.remove('rotate-180');
                    if(textSpan) textSpan.textContent = `View ${count} repl${count > 1 ? 'ies' : 'y'}`;
                } else {
                    // Action: Show
                    
                    // Lazy Load logic (if container is empty and backend provides an endpoint)
                    const fetchUrl = repliesContainer.getAttribute('data-replies-url');
                    if (repliesContainer.innerHTML.trim() === '' && fetchUrl && fetchUrl !== '') {
                        try {
                            if(textSpan) textSpan.textContent = 'Loading...';
                            const response = await fetch(fetchUrl);
                            if (response.ok) {
                                const html = await response.text();
                                repliesContainer.insertAdjacentHTML("beforeend", html);
                            }
                        } catch (err) {
                            console.error('Error fetching replies:', err);
                        }
                    }
                    repliesContainer.classList.remove('d-none');
                    btnViewReplies.setAttribute('aria-expanded', 'true');
                    if(icon) icon.classList.add('rotate-180');
                    if(textSpan) textSpan.textContent = 'Hide replies';
                }
            }
            return;
        }
    });
});

document.querySelectorAll(".comment-menu-toggle").forEach((button) => {
    button.addEventListener("click", function (event) {
        event.stopPropagation();

        const menuId = this.getAttribute("aria-controls");
        const menu = document.getElementById(menuId);

        if (!menu) {
            return;
        }

        const isOpen = !menu.classList.contains("d-none");

        document
            .querySelectorAll(".comment-menu-dropdown")
            .forEach((item) => {
                item.classList.add("d-none");
            });

        document
            .querySelectorAll(".comment-menu-toggle")
            .forEach((item) => {
                item.setAttribute("aria-expanded", "false");
            });

        if (!isOpen) {
            menu.classList.remove("d-none");
            this.setAttribute("aria-expanded", "true");
        }
    });
});

document.addEventListener("click", () => {
    document
        .querySelectorAll(".comment-menu-dropdown")
        .forEach((menu) => {
            menu.classList.add("d-none");
        });

    document
        .querySelectorAll(".comment-menu-toggle")
        .forEach((button) => {
            button.setAttribute("aria-expanded", "false");
        });
});

document.querySelectorAll(".comment-edit-btn").forEach((button) => {
    button.addEventListener("click", function () {
        const commentId = this.dataset.commentId;

        const body = document.getElementById(
            `comment-body-${commentId}`
        );

        const editForm = document.getElementById(
            `comment-edit-form-${commentId}`
        );

        if (!body || !editForm) {
            return;
        }

        body.classList.add("d-none");
        editForm.classList.remove("d-none");

        const textarea = editForm.querySelector("textarea");

        if (textarea) {
            textarea.focus();

            textarea.setSelectionRange(
                textarea.value.length,
                textarea.value.length
            );
        }
    });
});

document.querySelectorAll(".btn-edit-cancel").forEach((button) => {
    button.addEventListener("click", function () {
        const editForm = this.closest(".comment-edit-form-wrapper");
        const comment = editForm.closest(".comment-item");

        if (!editForm || !comment) {
            return;
        }

        const body = comment.querySelector(".comment-body");

        editForm.classList.add("d-none");
        body.classList.remove("d-none");
    });
});