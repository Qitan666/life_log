document.addEventListener("DOMContentLoaded", function () {
    // ===== Like button =====
    const likeButtons = document.querySelectorAll(".like-btn");
    const csrfTokenMeta = document.querySelector('meta[name="csrf-token"]');
    const csrfToken = csrfTokenMeta ? csrfTokenMeta.getAttribute("content") : "";

    likeButtons.forEach((button) => {
        button.addEventListener("click", async function (event) {
            event.preventDefault();
            event.stopPropagation();

            if (button.disabled) return;

            const url = button.dataset.likeUrl;
            const countEl = button.querySelector(".like-count");

            try {
                const response = await fetch(url, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": csrfToken,
                        "X-Requested-With": "XMLHttpRequest",
                    },
                });

                if (!response.ok) {
                    throw new Error("Failed to toggle like.");
                }

                const data = await response.json();

                if (data.liked) {
                    button.classList.add("liked");
                } else {
                    button.classList.remove("liked");
                }

                if (countEl) {
                    countEl.textContent = data.like_count;
                }

                button.classList.remove("pop");
                void button.offsetWidth;
                button.classList.add("pop");
            } catch (error) {
                console.error("like error:", error);
            }
        });
    });

    // ===== Sidebar toggle =====
    const sidebar = document.getElementById("categorySidebar");
    const sidebarToggle = document.getElementById("sidebarToggle");
    const sidebarClose = document.getElementById("sidebarClose");
    const sidebarBackdrop = document.getElementById("sidebarBackdrop");

    function openSidebar() {
        if (!sidebar) return;
        sidebar.classList.add("open");
        if (sidebarBackdrop) sidebarBackdrop.classList.add("show");
    }

    function closeSidebar() {
        if (!sidebar) return;
        sidebar.classList.remove("open");
        if (sidebarBackdrop) sidebarBackdrop.classList.remove("show");
    }

    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", openSidebar);
    }

    if (sidebarClose) {
        sidebarClose.addEventListener("click", closeSidebar);
    }

    if (sidebarBackdrop) {
        sidebarBackdrop.addEventListener("click", closeSidebar);
    }
});