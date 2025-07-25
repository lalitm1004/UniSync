import { Course, CourseSection } from "./types/course.type";
import extractComponent from "./utils/extractComponent";
import extractCourseInfo from "./utils/extractCourseInfo";
import extractDates from "./utils/extractDates";
import extractRooms from "./utils/extractRooms";
import extractTimings from "./utils/extractTimings";

const extractSchedule = (): Course[] => {
    const courseDivs = document.querySelectorAll('div[id*="DERIVED_REGFRM1_DESCR20"]')
    const courses: Course[] = [];
    const misc: string[] = [];

    courseDivs.forEach((div) => {
        const statusSpan = div.querySelector('span[id^="STATUS"]');
        if (!statusSpan || statusSpan.textContent?.trim().toLowerCase() !== 'enrolled') {
            return;
        }


        const courseHeader = div.querySelector('td.PAGROUPDIVIDER');
        if (!courseHeader || !courseHeader.textContent?.trim()) {
            return;
        };

        const { course_code, course_title } = extractCourseInfo(courseHeader.textContent?.trim());
        misc.push(course_code);

        const course_sections: CourseSection[] = [];
        const sectionRows = div.querySelectorAll('tr[id^="trCLASS_MTG_VW"]');

        sectionRows.forEach((row) => {
            const sectionAnchor = row.querySelector('a[id^="MTG_SECTION"]');
            if (!sectionAnchor || !sectionAnchor.textContent?.trim()) {
                return;
            }
            const section = sectionAnchor.textContent.trim();

            const componentSpan = row.querySelector('span[id^="MTG_COMP"]');
            if (!componentSpan || !componentSpan.textContent?.trim()) {
                return;
            }
            const component = extractComponent(componentSpan.textContent.trim());
            if (!component) {
                return;
            }

            const timingsSpan = row.querySelector('span[id^="MTG_SCHED"]')!;
            const timings = extractTimings(timingsSpan?.textContent?.trim() ?? "");

            const roomsSpan = row.querySelector('span[id^="MTG_LOC"]')!;
            const rooms = extractRooms(roomsSpan.textContent?.trim() ?? "");

            const datesSpan = row.querySelector('span[id^="MTG_DATES"]');
            if (!datesSpan || !datesSpan.textContent?.trim()) {
                return;
            }
            const { start_date, end_date } = extractDates(datesSpan.textContent.trim());

            course_sections.push({
                section,
                component,
                timings,
                rooms,
                start_date,
                end_date
            })
        });

        courses.push({
            course_code,
            course_title,
            course_sections
        });
    });

    return courses;
}

const main = () => {
    const data = extractSchedule();
    chrome.runtime.sendMessage({
        topic: 'parsed_schedule',
        data,
    });
}

main();