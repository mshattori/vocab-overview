document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('toggle-answers').addEventListener('click', function() {
        // Toggle visibility
        document.querySelectorAll('.answer-text').forEach(function(element) {
            if (element.style.visibility === 'hidden') {
                element.style.visibility = 'visible';
            } else {
                element.style.visibility = 'hidden';
            }
        });
    });
});
