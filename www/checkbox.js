// Use HTML filename without the extension as the DB name
const dbName = document.location.pathname.split('/').pop().split('.')[0];
const dbVersion = 1;
let db;
let showUnchecked = true

document.addEventListener('DOMContentLoaded', function() {
    initCheckboxDatabase();
    // Add event listener to clear-checkboxes menu
    document.getElementById('clear-checkboxes').addEventListener('click', function() {
        clearCheckboxes(db);
        UIkit.dropdown('.uk-navbar-dropdown').hide();
    });
    document.getElementById('toggle-unchecked').addEventListener('click', function() {
        toggleUnchecked();
        UIkit.dropdown('.uk-navbar-dropdown').hide();
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
    const transaction = db.transaction(['checkboxes'], 'readwrite');
    const store = transaction.objectStore('checkboxes');

    let latestCheckboxIds = [];

    document.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
        checkbox.checked = false; // Set default checked state to false
        latestCheckboxIds.push(checkbox.id); // Record the latest checkboxes
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
    cleanupDatabase(store, latestCheckboxIds);
}

function cleanupDatabase(store, checkboxIds) {
    // Delete all unused records
    const request = store.getAll();
    request.onsuccess = function() {
        const allRecords = request.result;
        allRecords.forEach(function(record) {
            if (!checkboxIds.includes(record.id)) {
                store.delete(record.id);
                console.log('Deleted unused record:', record.id);
            }
        });
    };
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

function toggleUnchecked() {
    showUnchecked = !showUnchecked;
    document.querySelectorAll('input[type="checkbox"]').forEach(function(checkbox) {
        display = showUnchecked || checkbox.checked ? 'block' : 'none';
        document.querySelectorAll('.' + checkbox.id).forEach(function(element) {
            element.style.display = display;
        });
    });
    // Hide comments when hiding unchecked
    document.querySelectorAll('.comment').forEach(function(comment) {
        comment.style.display = showUnchecked ? 'block' : 'none';
    });
}
