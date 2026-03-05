document.addEventListener("DOMContentLoaded", function () {
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
                console.error(error);
            }
        });
    });
});