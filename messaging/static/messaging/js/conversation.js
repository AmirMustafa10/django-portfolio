document.addEventListener('DOMContentLoaded', () => {
    const chatMessages = document.getElementById('chat-messages');
    const messagesList = document.getElementById('messages-list');
    const btnNewest = document.getElementById('btn-newest');
    const loadOlderInd = document.getElementById('load-older-indicator');
    
    if (!chatMessages || !messagesList) return;
    // 15. INITIAL LOAD SCROLL (Bottom)
    chatMessages.scrollTop = chatMessages.scrollHeight;
    let isLoadingOlder = false;
    // SCROLL EVENT: Top & Bottom detection
    chatMessages.addEventListener('scroll', async () => {
        
        // 23. GO TO LATEST DETECTION
        const distFromBottom = chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight;
        if (distFromBottom > 250) {
            btnNewest.classList.remove('d-none');
        } else {
            btnNewest.classList.add('d-none');
        }
        // 16. LOAD OLDER MESSAGES
        const hasNext = messagesList.dataset.hasNext === "true";
        if (chatMessages.scrollTop < 50 && !isLoadingOlder && hasNext) {
            
            // 22. Duplicate Request Protection
            isLoadingOlder = true;
            loadOlderInd.classList.remove('d-none');
            const nextPage = messagesList.dataset.nextPage;
            
            // 17. Load Older URL (preserve current path)
            const url = new URL(window.location.href);
            url.searchParams.set('page', nextPage);
            try {
                const response = await fetch(url);
                if (response.ok) {
                    const html = await response.text();
                    
                    // Parse safely to extract only message rows
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    const olderList = doc.getElementById('messages-list');
                    if (olderList) {
                        // 19. PRESERVE SCROLL POSITION
                        const oldHeight = chatMessages.scrollHeight;
                        
                        // Insert older HTML directly at the top of the history list
                        messagesList.insertAdjacentHTML('afterbegin', olderList.innerHTML);
                        
                        // Anchor viewport
                        chatMessages.scrollTop += (chatMessages.scrollHeight - oldHeight);
                        
                        // Update tracking state
                        messagesList.dataset.hasNext = olderList.dataset.hasNext;
                        messagesList.dataset.nextPage = olderList.dataset.nextPage;
                    }
                }
            } catch (e) {
                console.error("Failed to load older messages:", e);
            } finally {
                isLoadingOlder = false;
                loadOlderInd.classList.add('d-none');
                
                // 21. Stop loading
                if (messagesList.dataset.hasNext === "false") {
                    // History exhausted. Optional subtle visual indicator could go here.
                }
            }
        }
    });
    // 24. GO TO LATEST BEHAVIOR
    if (btnNewest) {
        btnNewest.addEventListener('click', () => {
            chatMessages.scrollTo({
                top: chatMessages.scrollHeight,
                behavior: 'smooth'
            });
        });
    }
    
    // Auto-expand textarea slightly on typing (Optional UI enhancement)
    const textarea = document.querySelector('.composer-textarea');
    if(textarea) {
        textarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});