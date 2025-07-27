import { get } from "svelte/store";
import { PUBLIC_BACKEND_URL } from "$env/static/public";
import { SessionStore } from "$lib/stores/SupaStore";

interface FetchOptions extends RequestInit {
    headers?: Record<string, string>;
}

export const fetchWithAuthBrowser = async (route: string, options: FetchOptions = {}): Promise<Response> => {
    const jwt = get(SessionStore)?.access_token ?? "";
    const cleanedRoute = route.replace(/^\/+/, "");

    return fetch(`${PUBLIC_BACKEND_URL}/${cleanedRoute}`, {
        ...options,
        headers: {
            ...options.headers,
            'Authorization': `Bearer ${jwt}`
        }
    });
}