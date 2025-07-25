import { Day, DayEnum, Timing } from "../types/course.type";

const extractTimings = (input: string): Timing[] => {
    const abbrevToDay: { [key: string]: Day } = {
        Mo: DayEnum.MONDAY,
        Tu: DayEnum.TUESDAY,
        We: DayEnum.WEDNESDAY,
        Th: DayEnum.THURSDAY,
        Fr: DayEnum.FRIDAY,
        Sa: DayEnum.SATURDAY,
        Su: DayEnum.SUNDAY
    };

    const results: Timing[] = [];

    const lines = input
        .split('\n')
        .map(line => line.trim())
        .filter(line => line.length > 0);

    for (const line of lines) {
        let start_time: string | null = null;
        let end_time: string | null = null;
        let days: Day[] = [];

        const timeMatch = line.match(/(\d{1,2}:\d{2}[AP]M)\s*-\s*(\d{1,2}:\d{2}[AP]M)/);

        if (timeMatch) {
            start_time = timeMatch[1];
            end_time = timeMatch[2];
        }

        const dayPart = timeMatch ? line.slice(0, line.indexOf(timeMatch[0])) : line;

        const dayAbbrevs = dayPart.match(/(Mo|Tu|We|Th|Fr|Sa|Su)/g) || [];

        days = dayAbbrevs.map(abbrev => abbrevToDay[abbrev]).filter(Boolean);

        results.push({
            start_time,
            end_time,
            days
        });
    }

    return results;
}
export default extractTimings;