type HTMXAfterSwapDetail = {
    xhr: XMLHttpRequest;
    etc: Record<string, any>;
    successful: boolean;
    failed: boolean;
    target: HTMLElement;
    pathInfo: {
        anchor: "" | undefined;
        finalRequestPath: string;
        requestPath: string;
        responsePath: string;
    };
    requestConfig: {};
};

function onHtmxAfterSwap(e: Event | CustomEvent<HTMXAfterSwapDetail>) {
    if (!(e instanceof CustomEvent)) {
        return;
    }

    if (e.detail.target.id == "modals") {
        setTimeout(() => {
            e.detail.target.querySelector("*:first-child")!.classList.add("show");
        }, 10);
    }
}

function closeModal() {
    const modal = document.querySelector("#modals *:first-child");
    if (modal) {
        modal.classList.remove("show");
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}

document.addEventListener("htmx:afterSwap", onHtmxAfterSwap);
document.addEventListener("modals.close", closeModal);

window.closeModal = closeModal;
