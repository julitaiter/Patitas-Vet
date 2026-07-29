(function () {
    "use strict";

    document.querySelectorAll("[data-auto-dismiss-ms]").forEach((message) => {
        const duration = Number(message.dataset.autoDismissMs) || 3000;
        window.setTimeout(() => {
            bootstrap.Alert.getOrCreateInstance(message).close();
        }, duration);
    });
})();
