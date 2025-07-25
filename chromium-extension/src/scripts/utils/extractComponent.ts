import { Component, ComponentEnum } from "../types/course.type";

const extractComponent = (input: string): Component | null => {
    const firstChar = input.charAt(0).toLowerCase();

    switch (firstChar) {
        case 'l':
            return ComponentEnum.LECTURE;
        case 't':
            return ComponentEnum.TUTORIAL;
        case 'p':
            return ComponentEnum.PRACTICAL;
        default:
            return null;
    }
}
export default extractComponent;