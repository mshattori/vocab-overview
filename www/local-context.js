{
    let conextName = document.location.pathname.split('/').pop().split('.')[0];
    let getItem = (key) => {
        return localStorage.getItem(conextName + ':' + key)
    }
    let setItem = (key, value) => {
        localStorage.setItem(conextName + ':' + key, value)
    }
    let removeItem = (key) => {
        localStorage.removeItem(conextName + ':' + key)
    }
    // Export via global object
    var localContext = {
        'getItem': getItem,
        'setItem': setItem,
        'removeItem': removeItem,
    }
}