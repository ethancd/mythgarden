// A typescript file for the game Mythgarden

import {
    findElementByClassName,
    findAllElementsByClassName,
    listenOnElement,
    listenOnElements,
} from './dom';

import {
    post,
} from './ajax';


/* user interaction functions */

// fn: hide an element
function hide(element: HTMLElement) {
    element.style.display = "none";
}

// fn: execute an action
function executeAction(element: HTMLElement) {
    element.classList.toggle('executing');

    const descEl = element.getElementsByClassName('desc')[0];
    const descText = getStrOrError(descEl.textContent);

    // logAction(element.getElementsByClassName('desc')[0]);
    // payActionCost(element.getElementsByClassName('cost')[0]);

    post('action', {description: descText})
        .then((response) => {
            console.log(response);
            // update clock if necessary
            //   updateClock(response.clock_display)
            // update wallet if necessary
            //   updateWallet(response.wallet_display)
            // update location if necessary
            //   updateLocation(response.place);
            // update inventory if necessary
            //  updateInventory(response.inventory);
            // appendLogEntry(response.log_entry);
            // updateActions(response.actions);
            // @ts-ignore


            element.classList.toggle('executing');
        }).catch((response) => {
            console.log(response);
            element.classList.toggle('executing');
        });
}

// fn: update displayed location name and landscape to the new location
function updateLocation(newLocation: string) {
    console.log('updating location');
    const LANDSCAPES: any = {
        'Balamb Farm': 'idyllic-green-farm',
        'General Store': 'old-timey-general-store',
    };

    const locationEl = findElementByClassName('location');
    const landscapeEl = findElementByClassName('landscape');

    const landscapeFileName = LANDSCAPES[newLocation]

    // This confusing regex creates 3 capture groups:
    // 1. (.*\/) the static path to the image (excluding the filename)
    // 2. ([A-Za-z-]*) the filename (excluding the extension)
    // 3. (\.[a-z]*) the extension
    // Capture groups $1 and $3 are preserved by the replace,
    // and the filename is replaced with the new location's filename
    const staticPathRegex = /(.*\/)([A-Za-z-]*)(\.[a-z]*)/;

    locationEl.innerText = newLocation;
    const currentImageSrc = getStrOrError(landscapeEl.getAttribute('src'));
    const newImageSrc = currentImageSrc.replace(staticPathRegex, `$1${landscapeFileName}$3`);

    //@ts-ignore
    landscapeEl.src = newImageSrc;
}

// fn: log an action given the action description element
function logAction(desc: Element) {
    const actionDescText = getStrOrError(desc.textContent);
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
    const costText = getStrOrError(cost.textContent);
    const costAmount = parseDuration(costText);

    advanceClock(costAmount);
}

// fn: parse duration in hours from a display string
function parseDuration(displayString: string): number {
     // this split returns an empty string in [0], number in [1], and unit in [2]
    const [_, amountText, unit] = displayString.split(/(\d+)/);
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
    if (clockData.day === undefined || clockData.time === undefined) {
        throw new Error('Clock data is missing');
    }

    const day = parseInt(clockData.day);
    const time = parseFloat(clockData.time); // preserve decimal places for eg half hours
    const newTime = time + amount;

    if (newTime >= 24) {
        const daysToAdd = Math.floor(newTime / 24);
        return [(day + daysToAdd) % 7, newTime % 24];
    } else {
        return [day, newTime];
    }
}

// fn: generate a display string for the clock
function genClockDisplayValue(day: number, time: number): string {
    if (day < 0 || day > 6 || time < 0 || time > 24) {
        throw new Error('Invalid day or time');
    }

    const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const weekdayText = WEEKDAYS[day];

    let hourText;

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

if (typeof window !== "undefined") {
    window.onload = setup;
}

export {
    createLogEntry,
    parseDuration,
    calcNewClockValues,
    genClockDisplayValue,
}



// fn: check if a value is a string, and throw an error if not
function getStrOrError(str: any): string {
    if (typeof str !== 'string') {
        throw new Error(`Expected string, got ${typeof str}`);
    }

    return str;
}