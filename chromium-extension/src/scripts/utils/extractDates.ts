const extractDates = (input: string): { start_date: string | null, end_date: string | null } => {
    const parts = input.split('-')
    const [startStrRaw, endStrRaw] = parts.map(part => part.trim())

    let start_date: string | null = null
    let end_date: string | null = null

    if (startStrRaw) {
        const [d, m, y] = startStrRaw.split('/').map(Number)
        const date = new Date(y, m - 1, d)
        if (
            !isNaN(d) && !isNaN(m) && !isNaN(y) &&
            date.getFullYear() === y &&
            date.getMonth() === m - 1 &&
            date.getDate() === d
        ) {
            start_date = date.toISOString().split('T')[0]
        }
    }

    if (endStrRaw) {
        const [d, m, y] = endStrRaw.split('/').map(Number)
        const date = new Date(y, m - 1, d)
        if (
            !isNaN(d) && !isNaN(m) && !isNaN(y) &&
            date.getFullYear() === y &&
            date.getMonth() === m - 1 &&
            date.getDate() === d
        ) {
            end_date = date.toISOString().split('T')[0]
        }
    }

    return { start_date, end_date }
}
export default extractDates;