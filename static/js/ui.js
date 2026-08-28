function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}


const STAR_RATINGS = {
                    1:'★☆☆☆☆',
                    2:'★★☆☆☆',
                    3:'★★★☆☆',
                    4:'★★★★☆',
                    5:'★★★★★'
                     }
function ratingToStars(score){
    const rounded = Math.round(score) || 0;
    const stars = STAR_RATINGS[rounded] || '☆☆☆☆☆'
    return `<span style="color:gold;">${stars}</span>`;
                    }

