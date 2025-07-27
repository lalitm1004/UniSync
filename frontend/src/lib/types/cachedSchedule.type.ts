import { z } from "zod";
import { DayEnum } from "./day.type";
import { ComponentEnum } from "./component.type";


export const CachedTimingSchema = z.object({
    start_time: z.string().nullable(),
    end_time: z.string().nullable(),
    days: z.array(DayEnum),
});

export const CachedCourseSectionSchema = z.object({
    section: z.string(),
    component: ComponentEnum,
    timings: z.array(CachedTimingSchema),
    rooms: z.array(z.string()),
    start_date: z.string().nullable(),
    end_date: z.string().nullable(),
});

export const CachedCourseSchema = z.object({
    course_code: z.string(),
    course_title: z.string(),
    course_sections: z.array(CachedCourseSectionSchema),
});

export const CachedScheduleSchema = z.array(CachedCourseSchema);

export type CachedTiming = z.infer<typeof CachedTimingSchema>;
export type CachedCourseSection = z.infer<typeof CachedCourseSectionSchema>;
export type CachedCourse = z.infer<typeof CachedCourseSchema>;
export type CachedSchedule = z.infer<typeof CachedScheduleSchema>;