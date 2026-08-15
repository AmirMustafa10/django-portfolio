document.addEventListener('DOMContentLoaded', () => {
    const stream = document.getElementById('dc-conv-stream');
    const list = document.getElementById('dc-conv-list');
    const btnNewest = document.getElementById('dc-conv-newest');
    const loader = document.getElementById('dc-conv-loader');
    
    if (!stream || !list) return;
    // --- 1. INITIAL SCROLL TO BOTTOM ---
    stream.scrollTop = stream.scrollHeight;
    let isLoadingOlder = false;
    let hasNextPage = false;
    let nextPageNum = 2;
    // Helper to grab pagination state from injected meta element
    const updatePaginationState = () => {
        const meta = list.querySelector('.dc-conv-pagination-meta');
        if (meta) {
            hasNextPage = meta.dataset.hasNext === "true";
            nextPageNum = meta.dataset.nextPage;
            meta.remove(); // Keep DOM clean
        }
    };
    updatePaginationState();
    // --- 2. SCROLL EVENT LISTENER ---
    stream.addEventListener('scroll', async () => {
        
        // Toggle 'Newest' Button visibility
        const distFromBottom = stream.scrollHeight - stream.scrollTop - stream.clientHeight;
        if (distFromBottom > 250) {
            btnNewest.classList.remove('d-none');
        } else {
            btnNewest.classList.add('d-none');
        }
        // Load Older Messages
        if (stream.scrollTop < 50 && !isLoadingOlder && hasNextPage) {
            isLoadingOlder = true;
            loader.classList.remove('d-none');
            
            const url = new URL(window.location.href);
            url.searchParams.set('page', nextPageNum);
            try {
                const response = await fetch(url);
                if (response.ok) {
                    const html = await response.text();
                    
                    // Safely parse the HTML response
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const olderList = doc.getElementById('dc-conv-list');
                    if (olderList) {
                        // Anchor viewport to prevent jumping
                        const oldHeight = stream.scrollHeight;
                        
                        // Insert directly ABOVE current history
                        list.insertAdjacentHTML('afterbegin', olderList.innerHTML);
                        
                        // Adjust scroll position to counter the new height
                        stream.scrollTop += (stream.scrollHeight - oldHeight);
                        
                        // Sync pagination
                        updatePaginationState();
                    }
                }
            } catch (e) {
                console.error("Failed to load older messages:", e);
            } finally {
                isLoadingOlder = false;
                loader.classList.add('d-none');
            }
        }
    });
    // --- 3. GO TO LATEST CLICK ---
    if (btnNewest) {
        btnNewest.addEventListener('click', () => {
            stream.scrollTo({
                top: stream.scrollHeight,
                behavior: 'smooth'
            });
        });
    }
    
    // --- 4. MESSAGE ACTIONS & INLINE EDITING (Event Delegation) ---
    document.addEventListener('click', (e) => {
        
        // Close all dropdowns if clicking outside
        if (!e.target.closest('.dc-conv-menu-container')) {
            document.querySelectorAll('.dc-conv-menu').forEach(dd => {
                dd.classList.add('d-none');
                const toggle = dd.previousElementSibling;
                if (toggle) toggle.setAttribute('aria-expanded', 'false');
            });
        }
        // Toggle Dropdown Menu
        const menuToggle = e.target.closest('.dc-conv-menu-toggle');
        if (menuToggle) {
            const dropdown = menuToggle.nextElementSibling;
            const isExpanded = menuToggle.getAttribute('aria-expanded') === 'true';
            
            // Close others
            document.querySelectorAll('.dc-conv-menu').forEach(dd => {
                dd.classList.add('d-none');
                const toggleBtn = dd.previousElementSibling;
                if (toggleBtn) toggleBtn.setAttribute('aria-expanded', 'false');
            });
            if (!isExpanded) {
                dropdown.classList.remove('d-none');
                menuToggle.setAttribute('aria-expanded', 'true');
            }
            return;
        }
        // Open Inline Edit
        const btnEditToggle = e.target.closest('.dc-conv-edit-toggle');
        if (btnEditToggle) {
            const row = btnEditToggle.closest('.dc-conv-content-wrapper');
            const displayView = row.querySelector('.dc-conv-display');
            const editForm = row.querySelector('.dc-conv-edit');
            
            if(displayView && editForm) {
                displayView.classList.add('d-none');
                editForm.classList.remove('d-none');
                const textarea = editForm.querySelector('textarea');
                if (textarea) {
                    textarea.focus();
                    // Auto-expand textarea
                    textarea.style.height = 'auto';
                    textarea.style.height = (textarea.scrollHeight) + 'px';
                }
            }
            return;
        }
        // Cancel Inline Edit
        const btnCancelEdit = e.target.closest('.dc-conv-edit-cancel');
        if (btnCancelEdit) {
            const row = btnCancelEdit.closest('.dc-conv-content-wrapper');
            const displayView = row.querySelector('.dc-conv-display');
            const editForm = row.querySelector('.dc-conv-edit');
            
            if(displayView && editForm) {
                editForm.classList.add('d-none');
                displayView.classList.remove('d-none');
            }
            return;
        }
    });
    // Dynamic Textarea Sizing (Composer & Edit)
    document.addEventListener('input', (e) => {
        if (e.target.classList.contains('dc-conv-composer-input') || e.target.classList.contains('dc-conv-edit-input')) {
            e.target.style.height = 'auto';
            e.target.style.height = (e.target.scrollHeight) + 'px';
        }
    });
});