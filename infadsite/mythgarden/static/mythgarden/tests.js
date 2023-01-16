"use strict";
// Tests for MythGarden js business logic
Object.defineProperty(exports, "__esModule", { value: true });
var chai_1 = require("chai");
// fn: helper function to create a mock action element
// function createMockActionElement(cost: string='1h'): HTMLElement {
//     const actionEl = document.createElement('div');
//     actionEl.className = 'action';
//
//     const descEl = document.createElement('div');
//     descEl.className = 'desc';
//     descEl.textContent = 'test';
//     actionEl.appendChild(descEl);
//
//     const costEl = document.createElement('div');
//     costEl.className = 'cost';
//     costEl.textContent = cost;
//     actionEl.appendChild(costEl);
//
//     return actionEl;
// }
// Test executeAction function (in script.ts)
// describe('executeAction', () => {
//     it('should toggle the executing class on the element', () => {
//         const actionEl = createMockActionElement()
//         executeAction(actionEl);
//
//         assert.isTrue(actionEl.classList.contains('executing'));
//     });
//
//     it('should log the action', () => {
//         const actionEl = createMockActionElement()
//         executeAction(actionEl);
//
//         const logEntry = findElementByClassName('log-entry');
//         assert.equal(logEntry.textContent, 'You tested.');
//     });
//
//     it('should pay the cost of the action', () => {
//         const actionEl = createMockActionElement('1h')
//         executeAction(actionEl);
//
//         const clockEl = findElementByClassName('clock');
//         assert.equal(clockEl.textContent, '23h');
//     }
// }
// Function to test: createLogEntry
describe('createLogEntry', function () {
    it('should return a string', function () {
        var logEntry = createLogEntry('test');
        chai_1.assert.isString(logEntry);
    });
    it('should return a string created using the passed text', function () {
        var logEntry = createLogEntry('test');
        chai_1.assert.equal(logEntry, 'You tested.');
    });
});
// Function to test: parseDuration
describe('parseDuration', function () {
    it('should return a number', function () {
        var duration = parseDuration('1h');
        chai_1.assert.isNumber(duration);
    });
    it('should return the number if the unit is h', function () {
        var duration = parseDuration('1h');
        chai_1.assert.equal(duration, 1);
    });
    it('should return the number divided by 60 if the unit is m', function () {
        var duration = parseDuration('30m');
        chai_1.assert.equal(duration, .5);
    });
    it('should return the number multiplied by 24 if the unit is d', function () {
        var duration = parseDuration('2d');
        chai_1.assert.equal(duration, 48);
    });
    it('should throw an error if the unit is unknown', function () {
        chai_1.assert.throws(function () { return parseDuration('1y'); });
    });
    it('should throw an error if the string has no unit', function () {
        chai_1.assert.throws(function () { return parseDuration('1'); });
    });
});
// Function to test: calcNewClockValues
describe('calcNewClockValues', function () {
    it('should return an array', function () {
        var newValues = calcNewClockValues({ day: '1', time: '1' }, 1);
        chai_1.assert.isArray(newValues);
    });
    it('should return an array with the new day and time', function () {
        var newValues = calcNewClockValues({ day: '1', time: '1' }, 1);
        chai_1.assert.deepEqual(newValues, [1, 2]);
    });
    it('should roll over to the next day when the time goes to 24+', function () {
        var newValues = calcNewClockValues({ day: '1', time: '23' }, 1);
        chai_1.assert.deepEqual(newValues, [2, 0]);
    });
    it('should roll back to the start of the week when the day goes to 7+', function () {
        var newValues = calcNewClockValues({ day: '6', time: '23' }, 11);
        chai_1.assert.deepEqual(newValues, [0, 10]);
    });
    it('should roll over to the right day when the time goes over by more than 24 hours', function () {
        var newValues = calcNewClockValues({ day: '3', time: '23' }, 48);
        chai_1.assert.deepEqual(newValues, [5, 23]);
    });
    it('should preserve decimals in the time', function () {
        var newValues = calcNewClockValues({ day: '1', time: '1' }, 1.5);
        chai_1.assert.deepEqual(newValues, [1, 2.5]);
    });
}
// Function to test: genClockDisplayValue
, 
// Function to test: genClockDisplayValue
describe('genClockDisplayValue', function () {
    it('should return a string', function () {
        var displayValue = genClockDisplayValue(1, 1);
        chai_1.assert.isString(displayValue);
    });
    it('should return the day and time', function () {
        var displayValue = genClockDisplayValue(1, 9);
        chai_1.assert.equal(displayValue, 'Mon 9am');
    });
    it('should show pm for times after 12', function () {
        var displayValue = genClockDisplayValue(1, 13);
        chai_1.assert.equal(displayValue, 'Mon 1pm');
    });
    it('should show pm when the time is 12', function () {
        var displayValue = genClockDisplayValue(1, 12);
        chai_1.assert.equal(displayValue, 'Mon 12pm');
    });
    it('should show am when the time is before 12', function () {
        var displayValue = genClockDisplayValue(1, 11);
        chai_1.assert.equal(displayValue, 'Mon 11am');
    });
    it('should show 12am if the time is 0', function () {
        var displayValue = genClockDisplayValue(1, 0);
        chai_1.assert.equal(displayValue, 'Mon 12am');
    });
    it('should show 12:30am if the time is 0.5', function () {
        var displayValue = genClockDisplayValue(1, 0);
        chai_1.assert.equal(displayValue, 'Mon 12:30am');
    });
    it('should throw an error if the day is more than 6', function () {
        chai_1.assert.throws(function () { return genClockDisplayValue(7, 1); });
    });
    it('should throw an error if the day is less than 0', function () {
        chai_1.assert.throws(function () { return genClockDisplayValue(-1, 1); });
    });
    it('should throw an error if the time is more than 24', function () {
        chai_1.assert.throws(function () { return genClockDisplayValue(1, 25); });
    });
    it('should throw an error if the time is less than 0', function () {
        chai_1.assert.throws(function () { return genClockDisplayValue(1, -1); });
    });
}));
