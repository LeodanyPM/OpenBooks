document.addEventListener("DOMContentLoaded", () => {
    const ratingForm = document.getElementById("rating-form");
    const reportBtn = document.getElementById("report-btn");
    const reportForm = document.getElementById("report-form");
    const cancelReportBtn = document.getElementById("cancel-report-btn");

    if (ratingForm) {
        ratingForm.addEventListener("submit", handleRatingSubmit);}
    if (reportBtn) {
        reportBtn.addEventListener("click", handleReportClick);}
    if (reportForm) {
        reportForm.addEventListener("submit", handleReportSubmit);}
    if (cancelReportBtn) {
        cancelReportBtn.addEventListener("click", () => {
            document.getElementById("report-form-container").classList.add("d-none");});}
});

function submitRating(bookId, ratingData) {
    const url = `/api/books/${bookId}/ratings/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    return fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json",
                   "X-CSRFToken": csrfToken
                 },
        body: JSON.stringify(ratingData)})
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.detail || "Error submitting rating");});
                            }
        return response.json();});
}

function handleRatingSubmit(event) {
    event.preventDefault();
    console.log("Send");
    const score = document.getElementById("rating-score").value;
    const comment = document.getElementById("rating-comment").value.trim();
    const messageDiv = document.getElementById("rating-message");

    if (!score) {
        messageDiv.innerHTML = "<span class='text-danger'>Select a rating.</span>";
        return;}
    if (!comment){
        messageDiv.innerHTML = "<span class='text-danger'> Please write a comment. </span>";}
    else{
        messageDiv.innerHTML = "<span class='text-muted'>Sending...</span>";
        submitRating(BOOK_ID, { score: parseInt(score), comment: comment })
            .then(newRating => {
                messageDiv.innerHTML = "<span class='text-success'>Rating submitted.</span>";
                document.getElementById("rating-form").reset();
                appendRating(newRating);})
            .catch(error => {
                messageDiv.innerHTML = `<span class='text-danger'>${escapeHtml(error.message)}</span>`;});
        }
}

function appendRating(rating) {
    const list = document.getElementById("ratings-list");

    const emptyMessage = list.querySelector(".text-muted");
    if (emptyMessage) {
        emptyMessage.remove();}

    const div = document.createElement("div");
    div.className = "border rounded p-3 mb-2";

    const header = document.createElement("div");
    header.className = "d-flex justify-content-between";

    const user = document.createElement("strong");
    user.textContent = rating.user;

    const stars = document.createElement("span");
    stars.innerHTML = ratingToStars(rating.score);

    header.append(user, stars);

    const comment = document.createElement("p");
    comment.className = "mb-0 mt-2";
    comment.textContent = rating.comment || "";

    div.append(header, comment);
    list.appendChild(div);
}

function handleReportClick() {
    const formContainer = document.getElementById("report-form-container");
    formContainer.classList.toggle("d-none");
}

function handleReportSubmit(event) {
    event.preventDefault();
    const reason = document.getElementById("report-reason").value.trim();
    const messageDiv = document.getElementById("report-message");

    if (!reason) {
        messageDiv.innerHTML = "<span class='text-danger'>Please write a reason.</span>";
        return;}
    messageDiv.innerHTML = "<span class='text-muted'>Sending...</span>";
    submitReport(BOOK_ID, { reason: reason })
        .then(() => {
            alert("Report submitted successfully. This book is no longer publicly visible.");
            window.location.href = "/api/explore/";})
        .catch(error => {
            messageDiv.innerHTML = `<span class='text-danger'>${escapeHtml(error.message)}</span>`;});
}

function submitReport(bookId, reportData) {
    const url = `/api/books/${bookId}/report/`;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    return fetch(url, {
        method: "POST",
        headers: {"Content-Type": "application/json",
                  "X-CSRFToken": csrfToken},
        body: JSON.stringify(reportData)})
    .then(response => {
        if (!response.ok) {
            return response.json().then(data => {
                throw new Error(data.detail || "Error submitting report");
                                                });
                          }
        return response.json();});
}
