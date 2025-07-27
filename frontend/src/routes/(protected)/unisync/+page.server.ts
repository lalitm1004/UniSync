import { SCHEDULE_CACHE_ACCESS_KEY } from "$env/static/private";
import { PUBLIC_BACKEND_URL } from "$env/static/public";
import { CachedScheduleSchema, type CachedSchedule } from "$lib/types/cachedSchedule.type";
import type { PageServerLoad } from "./$types";

// @ts-ignore
export const load: PageServerLoad = async ({ url, fetch }) => {
    const id = url.searchParams.get('id');

    if (id) {
        const response = await fetch(`${PUBLIC_BACKEND_URL}/schedule-cache/${id}`, {
            method: 'GET',
            headers: {
                "Authorization": `Bearer ${SCHEDULE_CACHE_ACCESS_KEY}`
            }
        });

        console.log(response.status)

        if (response.status === 200) {

            const data = await response.json();
            const result = CachedScheduleSchema.safeParse(data);

            if (!result.success) {
                console.error("CachedSchdule validation failed: ", result.error.message);
                return { schedule: [] as CachedSchedule }
            }

            return {
                schedule: result.data
            }
        }
    }

    return {
        schedule: [] as CachedSchedule
    };
}