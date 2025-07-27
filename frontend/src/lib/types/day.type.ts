import { z } from "zod";

export const DayEnum = z.enum([
    "MONDAY",
    "TUESDAY",
    "WEDNESDAY",
    "THURSDAY",
    "FRIDAY",
    "SATURDAY",
    "SUNDAY",
]);

export type Day = z.infer<typeof DayEnum>;
