document.addEventListener('DOMContentLoaded', () => {
    // --- 16. Gallery Logic ---
    const mainImage = document.getElementById('mainGalleryImage');
    const prevBtn = document.getElementById('galleryPrevBtn');
    const nextBtn = document.getElementById('galleryNextBtn');
    const counter = document.getElementById('galleryCounter');
    const thumbnails = document.querySelectorAll('.thumbnail-item');
    const thumbnailTrack = document.getElementById('thumbnailTrack');
    
    if (!mainImage) return; // Exit if no images exist
    
    // Hide controls if there's only 1 image
    if (thumbnails.length <= 1) {
        if (prevBtn) prevBtn.style.display = 'none';
        if (nextBtn) nextBtn.style.display = 'none';
        if (counter) counter.style.display = 'none';
        return;
    }
    let currentIndex = 0;
    const totalImages = thumbnails.length;
    // Function to update the gallery state
    const updateGallery = (index) => {
        // Bounds checking
        if (index < 0) index = totalImages - 1;
        if (index >= totalImages) index = 0;
        
        currentIndex = index;
        const targetThumb = thumbnails[currentIndex];
        
        // Update Main Image
        mainImage.style.opacity = '0.5';
        setTimeout(() => {
            mainImage.src = targetThumb.getAttribute('data-src');
            mainImage.style.opacity = '1';
        }, 150);
        // Update Counter
        if (counter) {
            counter.innerText = `${currentIndex + 1} / ${totalImages}`;
        }
        // Update Thumbnails Active State
        thumbnails.forEach(t => t.classList.remove('active'));
        targetThumb.classList.add('active');
        // Scroll thumbnail into view smoothly
        if (thumbnailTrack) {
            const trackRect = thumbnailTrack.getBoundingClientRect();
            const thumbRect = targetThumb.getBoundingClientRect();
            
            // If thumbnail is outside the visible track area, scroll it
            if (thumbRect.left < trackRect.left || thumbRect.right > trackRect.right) {
                targetThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
            }
        }
    };
    // Thumbnail Click Events
    thumbnails.forEach(thumb => {
        thumb.addEventListener('click', function() {
            const idx = parseInt(this.getAttribute('data-index'));
            updateGallery(idx);
        });
        
        // Keyboard accessibility for thumbnails
        thumb.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                const idx = parseInt(this.getAttribute('data-index'));
                updateGallery(idx);
            }
        });
    });
    // Prev/Next Button Events
    if (prevBtn) {
        prevBtn.addEventListener('click', () => updateGallery(currentIndex - 1));
    }
    if (nextBtn) {
        nextBtn.addEventListener('click', () => updateGallery(currentIndex + 1));
    }
    // Keyboard Accessibility for Main Gallery (Left/Right arrows)
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            updateGallery(currentIndex - 1);
        } else if (e.key === 'ArrowRight') {
            updateGallery(currentIndex + 1);
        }
    });
});