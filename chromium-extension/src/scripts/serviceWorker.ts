chrome.runtime.onMessage.addListener((request) => {
    if (request.topic === 'parsed_schedule' && request.data) {
        chrome.tabs.create({ url: `https://google.com/${JSON.stringify(request.data)}` });
    }
})