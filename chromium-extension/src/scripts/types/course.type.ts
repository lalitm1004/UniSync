export interface Course {
    course_code: string;
    course_title: string;
    course_sections: CourseSection[];
}

export interface CourseSection {
    section: string;
    component: Component;
    timings: Timing[];
    rooms: string[];
    start_date: string | null;
    end_date: string | null;
}

export interface Timing {
    start_time: string | null;
    end_time: string | null;
    days: Day[];
}

export const ComponentEnum = {
    LECTURE: 'LECTURE',
    TUTORIAL: 'TUTORIAL',
    PRACTICAL: 'PRACTICAL',
} as const;
export type Component = typeof ComponentEnum[keyof typeof ComponentEnum];


export const DayEnum = {
    MONDAY: 'MONDAY',
    TUESDAY: 'TUESDAY',
    WEDNESDAY: 'WEDNESDAY',
    THURSDAY: 'THURSDAY',
    FRIDAY: 'FRIDAY',
    SATURDAY: 'SATURDAY',
    SUNDAY: 'SUNDAY'
} as const;
export type Day = typeof DayEnum[keyof typeof DayEnum];
