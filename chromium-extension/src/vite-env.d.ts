/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_SCHEDULE_URL: string;
    readonly VITE_GUIDE_URL: string;
    readonly VITE_BACKEND_URL: string;
    readonly VITE_HANDLER_URL: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}