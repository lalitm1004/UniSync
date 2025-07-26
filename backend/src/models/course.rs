use poem_openapi::{Enum, Object};
use serde::{Deserialize, Serialize};

#[derive(Object, Serialize, Deserialize, Clone)]
pub struct Course {
    pub course_code: String,
    pub course_title: String,
    pub course_sections: Vec<CourseSection>,
}

#[derive(Object, Serialize, Deserialize, Clone)]
pub struct CourseSection {
    pub section: String,
    pub component: Component,
    pub timings: Vec<Timing>,
    pub rooms: Vec<String>,
    pub start_date: Option<String>,
    pub end_date: Option<String>,
}

#[derive(Object, Serialize, Deserialize, Clone)]
pub struct Timing {
    pub start_time: Option<String>,
    pub end_time: Option<String>,
    pub days: Vec<Day>,
}

#[derive(Enum, Serialize, Deserialize, Clone)]
pub enum Component {
    #[serde(rename = "LECTURE")]
    LECTURE,

    #[serde(rename = "TUTORIAL")]
    TUTORIAL,

    #[serde(rename = "PRACTICAL")]
    PRACTICAL,
}

#[derive(Enum, Serialize, Deserialize, Clone)]
pub enum Day {
    #[serde(rename = "MONDAY")]
    MONDAY,

    #[serde(rename = "TUESDAY")]
    TUESDAY,

    #[serde(rename = "WEDNESDAY")]
    WEDNESDAY,

    #[serde(rename = "THURSDAY")]
    THURSDAY,

    #[serde(rename = "FRIDAY")]
    FRIDAY,

    #[serde(rename = "SATURDAY")]
    SATURDAY,

    #[serde(rename = "SUNDAY")]
    SUNDAY,
}
