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
