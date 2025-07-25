const handleClick = () => {
    chrome.tabs.create({
        url: "https://prodweb.snu.in/psp/CSPROD/EMPLOYEE/HRMS/c/SA_LEARNER_SERVICES.SSR_SSENRL_LIST.GBL",
    });
}

const captureButton = document.getElementById('capture-schedule')!;
captureButton.addEventListener('click', handleClick)
