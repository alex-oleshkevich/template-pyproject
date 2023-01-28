import { Notyf } from "notyf";

const TOAST_EVENT = "toast";
type ToastType = "success" | "error";
type ToastOptions = {
    message: string;
    category: ToastType;
};
export const toast = new Notyf({
    position: { x: "center", y: "bottom" },
    ripple: false,
    duration: 3000,
    dismissible: true,
});
window.toast = toast;

function onToast(e: Event | CustomEvent<ToastOptions>) {
    if (e instanceof CustomEvent) {
        toast.open({ type: e.detail.category || "success", message: e.detail.message });
    }
}

document.addEventListener(TOAST_EVENT, onToast);

// show flash messages as toasts
(window.__TOASTS__ || []).forEach((message) => {
    toast.open({ type: message.category, message: message.message });
});
