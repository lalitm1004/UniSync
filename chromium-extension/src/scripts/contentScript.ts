import { Course, CourseSection } from "./types/course.type";
import extractComponent from "./utils/extractComponent";
import extractCourseInfo from "./utils/extractCourseInfo";
import extractDates from "./utils/extractDates";
import extractRooms from "./utils/extractRooms";
import extractTimings from "./utils/extractTimings";

const getTextContent = (element: Element | null): string =>
    element?.textContent?.trim() ?? "";

const extractSchedule = (): Course[] => {
    const courseDivs = Array.from(document.querySelectorAll('div[id*="DERIVED_REGFRM1_DESCR20"]'));

    return courseDivs
        .filter(div => getTextContent(div.querySelector('span[id^="STATUS"]')).toLowerCase() === 'enrolled')
        .map(div => {
            const headerText = getTextContent(div.querySelector('td.PAGROUPDIVIDER'));
            if (!headerText) return null;

            const { course_code, course_title } = extractCourseInfo(headerText);

            const sectionRows = Array.from(div.querySelectorAll('tr[id^="trCLASS_MTG_VW"]'));

            const course_sections: CourseSection[] = sectionRows.flatMap(row => {
                const section = getTextContent(row.querySelector('a[id^="MTG_SECTION"]'));
                const componentRaw = getTextContent(row.querySelector('span[id^="MTG_COMP"]'));
                const timingsRaw = getTextContent(row.querySelector('span[id^="MTG_SCHED"]'));
                const roomsRaw = getTextContent(row.querySelector('span[id^="MTG_LOC"]'));
                const datesRaw = getTextContent(row.querySelector('span[id^="MTG_DATES"]'));

                const component = extractComponent(componentRaw);
                if (!section || !component || !datesRaw) return [];

                const timings = extractTimings(timingsRaw);
                const rooms = extractRooms(roomsRaw);
                const { start_date, end_date } = extractDates(datesRaw);

                return [{
                    section,
                    component,
                    timings,
                    rooms,
                    start_date,
                    end_date
                }];
            });

            return {
                course_code,
                course_title,
                course_sections
            };
        })
        .filter((course): course is Course => course !== null);
}

const main = () => {
    const data = extractSchedule();
    chrome.runtime.sendMessage({
        topic: 'parsed_schedule',
        data,
    });
}

main();
