document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("searchForm");
    const input = document.getElementById("locationInput");
    const searchBtn = document.getElementById("searchBtn");
    const btnText = searchBtn ? searchBtn.querySelector(".btn-text") : null;
    const btnLoader = searchBtn ? searchBtn.querySelector(".btn-loader") : null;

    const quickPicks = document.querySelectorAll(".quick-pick");
    const filterInput = document.getElementById("matchSearch");
    const matchCards = document.querySelectorAll(".match-card");
    const toggleReasonsBtn = document.getElementById("toggleReasonsBtn");
    const reasonGroups = document.querySelectorAll(".reason-group");
    const scrollToMatchesBtn = document.getElementById("scrollToMatches");
    const matchesSection = document.getElementById("matchesSection");

    if (form && searchBtn) {
        form.addEventListener("submit", () => {
            searchBtn.disabled = true;
            if (btnText) btnText.textContent = "Scanning habitat...";
            if (btnLoader) btnLoader.classList.remove("hidden");
        });
    }

    quickPicks.forEach((button) => {
        button.addEventListener("click", () => {
            const location = button.dataset.location;
            if (input && location) {
                input.value = location;
                input.focus();
            }
        });
    });

    if (filterInput) {
        filterInput.addEventListener("input", (event) => {
            const query = event.target.value.trim().toLowerCase();

            matchCards.forEach((card) => {
                const name = card.dataset.name || "";
                const visible = name.includes(query);
                card.classList.toggle("filtered-out", !visible);
            });
        });
    }

    if (toggleReasonsBtn) {
        let collapsed = false;

        toggleReasonsBtn.addEventListener("click", () => {
            collapsed = !collapsed;

            reasonGroups.forEach((group) => {
                group.classList.toggle("collapsed", collapsed);
            });

            toggleReasonsBtn.textContent = collapsed ? "Expand reasons" : "Collapse reasons";
        });
    }

    if (scrollToMatchesBtn && matchesSection) {
        scrollToMatchesBtn.addEventListener("click", () => {
            matchesSection.scrollIntoView({ behavior: "smooth", block: "start" });
        });
    }
});