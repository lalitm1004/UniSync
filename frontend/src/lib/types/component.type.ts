import { z } from "zod";

export const ComponentEnum = z.enum(["LECTURE", "TUTORIAL", "PRACTICAL"]);

export type Component = z.infer<typeof ComponentEnum>;
