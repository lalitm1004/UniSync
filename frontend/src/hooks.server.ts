import type { Handle } from "@sveltejs/kit";
import { sequence } from "@sveltejs/kit/hooks";

import createSupabase from "$lib/server/middleware/createSupabase";
import handleDevice from "$lib/server/middleware/handleDevice";

export const handle: Handle = sequence(createSupabase, handleDevice);