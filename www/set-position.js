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
            localContext.setItem('visible-position', checkbox.id);
            break;
        }
    }
}

function scrollToSavedRow() {
    const savedPos = localContext.getItem('visible-position');
    if (savedPos) {
        console.log("Move to " + savedPos)
        // Use requestAnimationFrame to wait for the browser to complete reflow.
        // Using requestAnimationFrame twice in a row is a technique leveraged to ensure that
        // an operation is executed after the browser has completed any pending layout reflows
        // and repaints.
        requestAnimationFrame(() => {
            requestAnimationFrame(() => {
                const elementToScroll = document.getElementById(savedPos);
                if (elementToScroll) {
                    elementToScroll.scrollIntoView();
                }
            });
        });
    }
}
