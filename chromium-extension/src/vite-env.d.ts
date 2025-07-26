/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_SCHEDULE_URL: string;
    readonly VITE_GUIDE_URL: string;
    readonly VITE_BACKEND_URL: string;
    readonly VITE_FRONTEND_URL: string;
    readonly VITE_API_ACCESS_KEY: string;
}

interface ImportMeta {
    readonly env: ImportMetaEnv;
}