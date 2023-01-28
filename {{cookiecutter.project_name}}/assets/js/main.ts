import axios from "axios";
import "./modals";
import "./toasts";

export * from "./components";

axios.defaults.baseURL = window.origin;
