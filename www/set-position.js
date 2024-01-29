document.addEventListener("visibilitychange", function() {
    if (document.visibilityState === 'hidden') {
        saveVisibleRowId();
    }
});

window.addEventListener('load', function() {
    scrollToSavedRow();
});

function saveVisibleRowId() {
    const rows = document.querySelectorAll('tr.item');
    const viewportHeight = window.innerHeight;
    for (let row of rows) {
        const rect = row.getBoundingClientRect();
        if (rect.top >= 0 && rect.bottom <= viewportHeight) {
            checkbox = row.querySelector('input.uk-checkbox')
            localStorage.setItem('visible-position', checkbox.id);
            break;
        }
    }
}

function scrollToSavedRow() {
    const savedPos = localStorage.getItem('visible-position');
    if (savedPos) {
        const elementToScroll = document.getElementById(savedPos);
        if (elementToScroll) {
            elementToScroll.scrollIntoView();
        }
    }
}
