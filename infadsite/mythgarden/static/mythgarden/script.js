// A typescript file for the game Mythgarden
/* DOM functions */
// fn: add an event listener to an element (specified by class name)
function listenOnElement(className, event, fn) {
    var element = findElementByClassName(className);
    listen(element, event, fn);
}
function listenOnElements(className, event, fn) {
    var elements = findAllElementsByClassName(className);
    elements.forEach(function (element) { return listen(element, event, fn); });
}
function listen(element, event, fn) {
    element.addEventListener(event, function () {
        fn(element);
        console.log("".concat(element.tagName, ".").concat(element.className, "#").concat(element.id, " ").concat(event, " event fired"));
    });
    // @ts-ignore
    console.log("bound ".concat(element.className, " on ").concat(event, " to ").concat(fn.name));
}
// fn: find first element with a class name
function findElementByClassName(className) {
    return document.getElementsByClassName(className)[0];
}
// fn: find all elements with a class name
function findAllElementsByClassName(className) {
    // @ts-ignore
    return Array.from(document.getElementsByClassName(className));
}
/* user interaction functions */
// fn: hide an element
function hide(element) {
    element.style.display = "none";
}
// fn: execute an action
function executeAction(element) {
    element.classList.toggle('executing');
    logAction(element.getElementsByClassName('desc')[0]);
    payActionCost(element.getElementsByClassName('cost')[0]);
    setTimeout(function () {
        element.classList.toggle('executing');
    }, 1000);
}
// fn: log an action given the action description element
function logAction(desc) {
    var actionDescText = desc.textContent;
    var logText = createLogEntry(actionDescText);
    appendLogEntry(logText);
}
// fn: create a log entry from the passed text
function createLogEntry(text) {
    return "You ".concat(text, "ed.");
}
// fn: append a log entry based on the passed text
function appendLogEntry(text) {
    var log = findElementByClassName('log');
    var entry = document.createElement('li');
    entry.className = 'log-entry';
    entry.textContent = text;
    log.appendChild(entry);
}
// fn: pay the cost of an action given the action cost element
function payActionCost(cost) {
    var costText = cost.textContent;
    var costAmount = parseDuration(costText);
    advanceClock(costAmount);
}
// fn: parse duration in hours from a display string
function parseDuration(displayString) {
    var _a = displayString.split(/(\d+)/), amountText = _a[0], unit = _a[1];
    var amount = parseInt(amountText);
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
            throw new Error("Invalid duration unit: ".concat(unit));
    }
    return amount;
}
// fn: advance the game clock by the passed amount {
function advanceClock(amount) {
    var clockEl = findElementByClassName('clock');
    var _a = calcNewClockValues(clockEl.dataset, amount), newDay = _a[0], newTime = _a[1];
    var newDisplay = genClockDisplayValue(newDay, newTime);
    setClockValues(clockEl, newDay, newTime, newDisplay);
}
// fn: add new time to current time and advance day if necessary
function calcNewClockValues(clockData, amount) {
    var day = parseInt(clockData.day);
    var time = parseInt(clockData.time);
    var newTime = time + amount;
    if (newTime >= 24) {
        return [(day + 1) % 7, newTime - 24];
    }
    else {
        return [day, newTime];
    }
}
// fn: generate a display string for the clock
function genClockDisplayValue(day, time) {
    var WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    var weekdayText = WEEKDAYS[day];
    var hourText = '';
    if (time > 12) {
        hourText = "".concat(Math.floor(time - 12));
    }
    else if (time < 1) {
        hourText = '12';
    }
    else {
        hourText = "".concat(Math.floor(time));
    }
    var hasMinutes = time % 1 !== 0;
    var minuteText = '';
    if (hasMinutes) {
        minuteText = ":".concat(Math.floor(time % 1 * 60));
    }
    var timeSuffix = time >= 12 ? 'pm' : 'am';
    return "".concat(weekdayText, " ").concat(hourText).concat(minuteText).concat(timeSuffix);
}
// fn: update the values in the clock element
function setClockValues(clockEl, day, time, display) {
    clockEl.dataset.day = day.toString();
    clockEl.dataset.time = time.toString();
    clockEl.innerText = display;
}
// fn: code to run when the page loads
function setup() {
    console.log('setting up');
    listenOnElement('message', 'click', hide);
    listenOnElements('action', 'click', executeAction);
}
window.onload = setup;
