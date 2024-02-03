document.addEventListener('DOMContentLoaded', function() {
    let globalVisibility = 1

    // Set click event listener to toggle visibility
    document.querySelectorAll('.answer-text').forEach(function(element) {
        // NOTE: Using 'element.style.visibility' isn't avairable because hidden elements
        // become unclickable from the screen thus you can't toggle them.
        element.style.opacity = globalVisibility;
        element.addEventListener('click', function() {
            element.style.opacity = element.style.opacity == 1 ? 0 : 1;
        });
    });
    document.getElementById('toggle-answers').addEventListener('click', function() {
        saveVisibleRowId();
        // Toggle visibility of all target element
        globalVisibility = globalVisibility == 1 ? 0 : 1;
        document.querySelectorAll('.answer-text').forEach(function(element) {
            element.style.opacity = globalVisibility;
        });
        UIkit.dropdown('.uk-navbar-dropdown').hide();
        scrollToSavedRow();
    });
});
