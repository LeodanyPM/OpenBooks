document.addEventListener("DOMContentLoaded", () => {
    const showMoreBtn = document.getElementById("show-more-btn");
    const booksGrid = document.getElementById("books-grid");

    if (!showMoreBtn) return;

    showMoreBtn.addEventListener("click", () => {
        const nextPage = showMoreBtn.dataset.nextPage;
        const lastPage =  showMoreBtn.dataset.lastPage;

        showMoreBtn.disabled = true;
        showMoreBtn.textContent = "Cargando...";
        
        fetch(`?page=${nextPage}`, {
            headers: { "X-Requested-With": "XMLHttpRequest" }})
        .then(response => {
            if (!response.ok) throw new Error(`Error HTTP: ${response.status}`);
            return response.text();})
        .then(html => {
            booksGrid.insertAdjacentHTML("beforeend", html);

            const next = parseInt(nextPage) + 1;
            

            if (nextPage == lastPage) {
                showMoreBtn.disabled = true;
                showMoreBtn.textContent = "No more books";
                showMoreBtn.classList.replace("btn-secondary", "btn-outline-secondary");
            } else {
                showMoreBtn.dataset.nextPage = next;
                showMoreBtn.disabled = false;
                showMoreBtn.textContent = "Show More";}})
        .catch(error => {
            console.error(error);
            showMoreBtn.disabled = false;
            showMoreBtn.textContent = "Reintentar";
        });});
});
