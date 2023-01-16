// A typescript file for the game Mythgarden

/* DOM functions */

// fn: add an event listener to an element (specified by class name)
function listenOnElement(className: string, event: string, fn: Function) {
    const element = findElementByClassName(className);
    listen(element, event, fn);
}

function listenOnElements(className: string, event: string, fn: Function) {
    const elements = findAllElementsByClassName(className);
    elements.forEach(element => listen(element, event, fn));
}

function listen(element: HTMLElement, event: string, fn: Function) {
    element.addEventListener(event, () => {
        fn(element)
        console.log(`${element.tagName}.${element.className}#${element.id} ${event} event fired`);
    });

    // @ts-ignore
    console.log(`bound ${element.className} on ${event} to ${fn.name}`);
}

// fn: find first element with a class name
function findElementByClassName(className: string): HTMLElement{
    return document.getElementsByClassName(className)[0] as HTMLElement;
}

// fn: find all elements with a class name
function findAllElementsByClassName(className: string): HTMLElement[] {
    // @ts-ignore
    return Array.from(document.getElementsByClassName(className)) as HTMLElement[];
}

/* user interaction functions */

// fn: hide an element
function hide(element: HTMLElement) {
    element.style.display = "none";
}

// fn: execute an action
function executeAction(element: HTMLElement) {
    element.classList.toggle('executing');

    logAction(element.getElementsByClassName('desc')[0]);
    payActionCost(element.getElementsByClassName('cost')[0]);

    setTimeout(() => {
        element.classList.toggle('executing');
    }, 1000);
}

// fn: log an action given the action description element
function logAction(desc: Element) {
    const actionDescText = desc.textContent;
    const logText = createLogEntry(actionDescText);

    appendLogEntry(logText);
}

// fn: create a log entry from the passed text
function createLogEntry(text: string): string {
    return `You ${text}ed.`;
}

// fn: append a log entry based on the passed text
function appendLogEntry(text: string) {
    const log = findElementByClassName('log');
    const entry = document.createElement('li');
    entry.className = 'log-entry';
    entry.textContent = text;
    log.appendChild(entry);
}


// fn: pay the cost of an action given the action cost element
function payActionCost(cost: Element) {
    const costText = cost.textContent;
    const costAmount = parseDuration(costText);

    advanceClock(costAmount);
}

// fn: parse duration in hours from a display string
function parseDuration(displayString: string): number {
    const [amountText, unit] = displayString.split(/(\d+)/)
    let amount = parseInt(amountText);

    switch (unit) {
        case 'h':
            break;
        case 'm':
            amount /= 60;
            break;
        case 'd':
            amount *= 24;
            break;
        default:
            throw new Error(`Invalid duration unit: ${unit}`);
    }

    return amount ;
}

// fn: advance the game clock by the passed amount {
function advanceClock(amount: number) {
    const clockEl = findElementByClassName('clock')
    const [newDay, newTime] = calcNewClockValues(clockEl.dataset, amount);
    const newDisplay = genClockDisplayValue(newDay, newTime);

    setClockValues(clockEl, newDay, newTime, newDisplay);
}

// fn: add new time to current time and advance day if necessary
function calcNewClockValues(clockData: DOMStringMap, amount: number): [number, number] {
    const day = parseInt(clockData.day);
    const time = parseInt(clockData.time);
    const newTime = time + amount;

    if (newTime >= 24) {
        return [(day + 1) % 7, newTime - 24];
    } else {
        return [day, newTime];
    }
}

// fn: generate a display string for the clock
function genClockDisplayValue(day: number, time: number): string {
    const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const weekdayText = WEEKDAYS[day];

    let hourText = '';

    if (time > 12) {
        hourText = `${Math.floor(time - 12)}`;
    } else if (time < 1) {
        hourText = '12';
    } else {
        hourText = `${Math.floor(time)}`;
    }

    const hasMinutes = time % 1 !== 0;
    let minuteText = '';

    if (hasMinutes) {
        minuteText = `:${Math.floor(time % 1 * 60)}`
    }

    const timeSuffix = time >= 12 ? 'pm' : 'am';

    return `${weekdayText} ${hourText}${minuteText}${timeSuffix}`;
}

// fn: update the values in the clock element
function setClockValues(clockEl: HTMLElement, day: number, time: number, display: string) {
    clockEl.dataset.day = day.toString();
    clockEl.dataset.time = time.toString();
    clockEl.innerText = display;
}

// fn: code to run when the page loads
function setup() {
    console.log('setting up')

    listenOnElement('message', 'click', hide);
    listenOnElements('action', 'click', executeAction);
}

window.onload = setup;