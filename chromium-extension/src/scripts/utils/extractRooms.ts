const extractRooms = (input: string): string[] => {
    try {
        const lines = input
            .split('\n')
            .map(line => line.trim().toUpperCase())
            .filter(line => line.length > 0);

        const rooms = new Set<string>();

        for (const line of lines) {
            const match = line.match(/\b([A-Z]*[0-9]+[A-Z]*)\b/);

            if (!match) {
                return [];
            }

            rooms.add(match[1]);
        }

        return Array.from(rooms);
    } catch {
        return [];
    }
}
export default extractRooms