document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("submit", (e) => {
        const form = e.target.closest(".delete-notification-form");
        if (!form) return;

        e.preventDefault();
        const csrfToken = form.querySelector("[name=csrfmiddlewaretoken]").value;
        const url = form.dataset.url;
        const notificationItem = form.closest(".list-group-item");

        fetch(url, {
            method: "POST",
            headers: {
                "X-CSRFToken": csrfToken,
                "X-Requested-With": "XMLHttpRequest"}
                    })
        .then(async response => {
            const responseText = await response.text();            
            if (!response.ok) {
                throw new Error(`Server response: ${response.status}: ${responseText.substring(0, 100)}`);}
            return JSON.parse(responseText);
                                })
        .then(data => {
            if (data.success) {
                notificationItem.style.transition = "opacity 0.3s ease";
                notificationItem.style.opacity = "0";
                setTimeout(() => notificationItem.remove(), 300);}
                        })
        .catch(error => {
            console.error("Error", error);
            alert("There was an error.");});
    });

});
