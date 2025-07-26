chrome.runtime.onMessage.addListener((request) => {
    if (request.topic === 'parsed_schedule' && request.data) {
        (async () => {
            try {
                const response = await fetch(`${import.meta.env.VITE_BACKEND_URL}/schedule-cache`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${import.meta.env.VITE_API_ACCESS_KEY}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        courses: request.data
                    })
                });

                if (response.status === 201) {
                    const data = await response.json();
                    const params = new URLSearchParams({ id: data.id });

                    chrome.tabs.create({
                        url: `${import.meta.env.VITE_FRONTEND_URL}/unisync?${params.toString()}`
                    })
                } else if (response.status === 503) {
                    const params = new URLSearchParams({ code: "CACHE_FULL" });

                    chrome.tabs.create({
                        url: `${import.meta.env.VITE_FRONTEND_URL}/error?${params.toString()}`
                    })
                } else {
                    const params = new URLSearchParams({ code: "UNKNOWN_ERROR", status: response.status.toString() });

                    chrome.tabs.create({
                        url: `${import.meta.env.VITE_FRONTEND_URL}/error?${params.toString()}`
                    })
                }
            } catch (error) {
                const params = new URLSearchParams({ code: "UNKNOWN_ERROR" });

                chrome.tabs.create({
                    url: `${import.meta.env.VITE_FRONTEND_URL}/error?${params.toString()}`
                })
            }
        })();
    }
})