
document.addEventListener("htmx:beforeSwap", function (event) {
    const status = event.detail.xhr.status;

    // Allow error responses to be displayed in the answer area.
    if (status === 403 || status === 422 || status >= 500) {
        event.detail.shouldSwap = true;
        event.detail.isError = false;
    }
});
