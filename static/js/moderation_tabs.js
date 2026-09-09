document.addEventListener("DOMContentLoaded", () => {
                                document.querySelectorAll(".book-row").forEach(row => {
                                    row.addEventListener("click", () => {
                                        window.location.href = row.dataset.href;});
                                                                                        });

    const reportedTab = document.getElementById("reported-tab");
    const tbody = document.getElementById("reported-books-tbody");
    const emptyDiv = document.getElementById("reported-empty");
    let reportsLoaded = false;
    reportedTab.addEventListener("click", () => {
                                    if (!reportsLoaded) {
                                        loadReportedBooks();
                                        reportsLoaded = true;}
                                                });

    function loadReportedBooks() {
        const url = reportedTab.dataset.url;
        fetch(url, {
                    method: "GET",
                    headers: {"X-Requested-With": "XMLHttpRequest"}
                    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);}
            return response.json();
                            })
        .then(data => {
            if (data.length === 0) {
                emptyDiv.style.display = "block";
                return;}
            data.forEach(book => {
                            const row = document.createElement("tr");
                            row.style.cursor = "pointer";
                            row.dataset.href = `/moderation/reported/${book.id}/`;                
                            row.innerHTML = `
                                <td class="fw-semibold">${escapeHtml(book.title)}</td>
                                <td>${escapeHtml(book.author)}</td>
                                <td>${escapeHtml(book.reported_by)}</td>
                                <td class="text-muted">${formatDate(book.reported_at)}</td>`;

                            row.addEventListener("click", () => {
                                window.location.href = row.dataset.href;});
                            tbody.appendChild(row);
                                });
                    })
        .catch(error => {
                        console.error("Error loading reported books:", error);
                        emptyDiv.style.display = "block";
                        emptyDiv.classList.remove("alert-success");
                        emptyDiv.classList.add("alert-danger");
                        emptyDiv.textContent = "Failed to load reported books. Please try again.";});
    }
});
