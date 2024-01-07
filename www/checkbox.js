// Use HTML filename without the extension as the DB name
const dbName = document.location.pathname.split('/').pop().split('.')[0];
const dbVersion = 1;
let db;

document.addEventListener('DOMContentLoaded', function() {
    initCheckboxDatabase();
    // Add event listener to clear-checkboxes menu
    document.getElementById('clear-checkboxes').addEventListener('click', function() {
        clearCheckboxes(db);
    });
});

function initCheckboxDatabase() {
    const request = indexedDB.open(dbName, dbVersion);
    request.onerror = function(event) {
        console.error('Database error:', event.target.error);
    };
    request.onsuccess = function(event) {
        db = event.target.result;
        initCheckboxStates(db); // Init checkboxes
    };
    request.onupgradeneeded = function(event) {
        // Called when the database needs to be upgraded or created.
        db = event.target.result;
        db.createObjectStore('checkboxes', {keyPath: 'id'});
    };
}

function initCheckboxStates(db) {
    console.log('Initializing checkbox states...');
    const transaction = db.transaction(['checkboxes'], 'readonly');
    const store = transaction.objectStore('checkboxes');

    document.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
        let request = store.get(checkbox.id);
        // Apply checked state and add event listener to checkboxes
        request.onsuccess = function(event) {
            if (request.result) {
                checkbox.checked = request.result.state;
            }
        };
        checkbox.addEventListener('change', function() {
            console.log('Checkbox changed:', checkbox.id, checkbox.checked);
            // Save checkbox state to database
            saveCheckboxState(db, checkbox.id, checkbox.checked);
        });
    });
}

function saveCheckboxState(db, id, state) {
    const transaction = db.transaction(['checkboxes'], 'readwrite');
    const store = transaction.objectStore('checkboxes');
    const data = {id: id, state: state};
    store.put(data);
}

function clearCheckboxes(db) {
    const transaction = db.transaction(['checkboxes'], 'readwrite');
    const store = transaction.objectStore('checkboxes');
    document.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
        checkbox.checked = false;
        store.put({ id: checkbox.id, state: false });
    });
}
