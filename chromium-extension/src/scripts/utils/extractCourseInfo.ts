const extractCourseInfo = (input: string): { course_code: string; course_title: string; } => {
    const match = input.match(/([A-Z]{3}\d{3,4})\s*-\s*(.+)/);

    if (!match) {
        return {
            course_code: "ERROR",
            course_title: "Failed to parse course header",
        };
    }

    const course_code = match[1];
    const course_title = match[2];
    return { course_code, course_title };
}
export default extractCourseInfo;