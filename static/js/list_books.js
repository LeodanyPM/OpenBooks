const API_URL = "/api/books/?ordering=-created_at";
let nextUrl = API_URL;
let loading = false;

function loadBooks() {
    const booksGrid = document.querySelector("#books-grid");
    const showMoreBtn = document.querySelector("#show-more-btn");
    if (!booksGrid || !showMoreBtn) {
        return;}
    if (!nextUrl || loading) {
        return;}

    loading = true;
    showMoreBtn.disabled = true;

    fetchBooks(nextUrl)
        .then(data => {
            const books = Array.isArray(data) ? data : data.results || [];
            
            books.forEach(book => {
                booksGrid.appendChild(createBookCard(book)); });
            nextUrl = data.next || null;
            if (nextUrl) {
                showMoreBtn.classList.remove("d-none");
            } else {
                showMoreBtn.classList.add("d-none");
            }})
        .catch(error => {
            console.error(error);})
        .finally(() => {
            loading = false;
            showMoreBtn.disabled = false;});
}

function handleBookClick(event) {
    const bookCard = event.target.closest(".book-card");
    if (bookCard) {
        const bookId = bookCard.dataset.bookId;
        console.log(`Libro clickeado: ID ${bookId}`);}
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
