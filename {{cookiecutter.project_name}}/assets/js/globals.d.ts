import Alpine from "alpinejs";
import { Notyf } from "notyf";
import { ToastType } from "./notifications";

declare global {
    interface Window {
        Alpine: Alpine;
        toast: Notyf;
        closeModal: () => void;
        __TOASTS__: { category: ToastType; message: string }[];
    }
}
export {};
