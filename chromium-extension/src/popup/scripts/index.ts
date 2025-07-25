const captureSchedule = (): void => {
    chrome.tabs.create({
        url: import.meta.env.VITE_SCHEDULE_URL,
    });
}
const captureButton = document.getElementById('capture-schedule')!;
captureButton.addEventListener('click', captureSchedule);


const openGuide = (): void => {
    chrome.tabs.create({
        url: import.meta.env.VITE_GUIDE_URL,
    });
}
const guideButton = document.getElementById('open-guide')!;
guideButton.addEventListener('click', openGuide);
