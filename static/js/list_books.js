const API_URL = "/api/books/?ordering=-created_at";
let nextUrl = API_URL;
let loading = false;

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function createBookCard(book) {
    const col = document.createElement("div");
    col.className = "col-md-4 mb-3";

    col.innerHTML = `
        <div class="card h-100 book-card" data-book-id="${book.id}" style="cursor: pointer;">
            <div class="bg-white border" style="height: 180px;"></div>
            <div class="card-body">
                <h5 class="card-title">${escapeHtml(book.title)}</h5>
                <p class="card-text">${escapeHtml(book.author)}</p>
                <p class="card-text">Rating: ${escapeHtml(book.rating || 0)}</p>
            </div>
        </div>  `;
    return col;
}

function loadBooks() {
    const booksGrid = document.querySelector("#books-grid");
    const showMoreBtn = document.querySelector("#show-more-btn");

    if (!booksGrid || !showMoreBtn) {
        return;                      }

    if (!nextUrl || loading) {
        return;               }

    loading = true;
    showMoreBtn.disabled = true;

    fetch(nextUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            return response.json();
                          })
        .then(data => {
            const books = Array.isArray(data) ? data : data.results || [];

            books.forEach(book => {
                booksGrid.appendChild(createBookCard(book));
            });
            nextUrl = data.next || null;
            if (nextUrl) {
                showMoreBtn.classList.remove("d-none");
            } else {
                showMoreBtn.classList.add("d-none");
                    }
                    })
        .catch(error => {console.error(error);})
        .finally(() => {
            loading = false;
            showMoreBtn.disabled = false;
                        });
}

function handleBookClick(event) {
    const bookCard = event.target.closest(".book-card");
    if (bookCard) {
        const bookId = bookCard.dataset.bookId;
        console.log(`Libro clickeado: ID ${bookId}`);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadBooks();
    const showMoreBtn = document.querySelector("#show-more-btn");
    if (showMoreBtn) {
        showMoreBtn.addEventListener("click", loadBooks);}
    const booksGrid = document.querySelector("#books-grid");
    if (booksGrid) {
        booksGrid.addEventListener("click", handleBookClick);}
});
