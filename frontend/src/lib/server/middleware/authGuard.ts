import { redirect, type Handle } from "@sveltejs/kit";

const authGuard: Handle = async ({ event, resolve }) => {
    const currentPath = event.url.pathname;
    const user = event.locals.user;

    if (!user && currentPath.startsWith('/unisync')) {
        const urlParams = new URLSearchParams({
            code: "NO_USER",
        })
        return redirect(303, `/error?${urlParams.toString()}`)
    }

    return resolve(event);
}

export default authGuard;