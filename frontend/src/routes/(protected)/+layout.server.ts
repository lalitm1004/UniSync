import { redirect } from '@sveltejs/kit';
import type { LayoutServerLoad } from './$types';

// @ts-ignore
export const load: LayoutServerLoad = async ({ locals }) => {
    if (!locals.user) {
        const urlParams = new URLSearchParams({
            code: "NO_USER",
        });
        throw redirect(303, `/error?${urlParams.toString()}`);
    }

    return {};
}
