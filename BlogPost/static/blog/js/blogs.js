// <!-- INFINITE SCROLL JAVASCRIPT -->

document.addEventListener("DOMContentLoaded", () => {
    const trigger = document.getElementById("load-more-trigger");
    const container = document.getElementById("blog-grid-container");
    const loadingSpinner = document.getElementById("loading-indicator");
    const endMessage = document.getElementById("end-of-content");

    // Abort if no trigger or container exists (e.g. empty state)
    if (!trigger || !container) return;

    let isLoading = false;
    let hasNext = trigger.dataset.hasNext === "true";
    let currentPage = parseInt(trigger.dataset.currentPage, 10);

    const loadMoreArticles = async () => {
        if (isLoading || !hasNext) return;

        isLoading = true;
        loadingSpinner.classList.remove("d-none");

        try {
            // Build the URL preserving existing GET parameters (q, status)
            const url = new URL(window.location.href);
            url.searchParams.set("page", currentPage + 1);

            // Fetch the HTML text of the next page
            const response = await fetch(url.toString());
            if (!response.ok) throw new Error("Network response was not ok");
            const htmlString = await response.text();

            // Parse the returned HTML string into a DOM Document
            const parser = new DOMParser();
            const doc = parser.parseFromString(htmlString, "text/html");

            // Extract ONLY the `.blog-item` columns to append to our grid
            const newCards = doc.querySelectorAll(".blog-item");
            newCards.forEach(card => container.appendChild(card));

            // Extract the new pagination state from the parsed document's trigger
            const newTrigger = doc.getElementById("load-more-trigger");
            if (newTrigger) {
                hasNext = newTrigger.dataset.hasNext === "true";
                currentPage = parseInt(newTrigger.dataset.currentPage, 10);
                
                // Update current trigger state for the next scroll event
                trigger.dataset.hasNext = hasNext;
                trigger.dataset.currentPage = currentPage;
            } else {
                hasNext = false;
            }

        } catch (error) {
            console.error("Error loading more articles:", error);
            // Optionally handle/display the error to the user
        } finally {
            isLoading = false;
            loadingSpinner.classList.add("d-none");
            
            if (!hasNext) {
                endMessage.classList.remove("d-none");
                trigger.style.display = "none";
            }
        }
    };

    // Use IntersectionObserver to trigger loading when near the bottom of the page
    const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
            loadMoreArticles();
        }
    }, {
        root: null,
        rootMargin: "200px", // Trigger slightly before the element enters the viewport
        threshold: 0.1
    });

    observer.observe(trigger);
});