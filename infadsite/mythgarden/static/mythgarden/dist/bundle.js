/*
 * ATTENTION: The "eval" devtool has been used (maybe by default in mode: "development").
 * This devtool is neither made for production nor for readable output files.
 * It uses "eval()" calls to create a separate source file in the browser devtools.
 * If you are trying to read the output file, select a different devtool (https://webpack.js.org/configuration/devtool/)
 * or disable the default devtool with "devtool: false".
 * If you are looking for production-ready output files, see mode: "production" (https://webpack.js.org/configuration/mode/).
 */
/******/ (() => { // webpackBootstrap
/******/ 	"use strict";
/******/ 	var __webpack_modules__ = ({

/***/ "./mythgarden/static/mythgarden/script.ts":
/*!************************************************!*\
  !*** ./mythgarden/static/mythgarden/script.ts ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"calcNewClockValues\": () => (/* binding */ calcNewClockValues),\n/* harmony export */   \"createLogEntry\": () => (/* binding */ createLogEntry),\n/* harmony export */   \"genClockDisplayValue\": () => (/* binding */ genClockDisplayValue),\n/* harmony export */   \"parseDuration\": () => (/* binding */ parseDuration)\n/* harmony export */ });\n/* harmony import */ var js_cookie__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! js-cookie */ \"./node_modules/js-cookie/dist/js.cookie.mjs\");\n// A typescript file for the game Mythgarden\n\n/* DOM functions */\n// fn: add an event listener to an element (specified by class name)\nfunction listenOnElement(className, event, fn) {\n    const element = findElementByClassName(className);\n    listen(element, event, fn);\n}\nfunction listenOnElements(className, event, fn) {\n    const elements = findAllElementsByClassName(className);\n    elements.forEach(element => listen(element, event, fn));\n}\nfunction listen(element, event, fn) {\n    element.addEventListener(event, () => {\n        fn(element);\n        console.log(`${element.tagName}.${element.className}#${element.id} ${event} event fired`);\n    });\n    // @ts-ignore\n    console.log(`bound ${element.className} on ${event} to ${fn.name}`);\n}\n// fn: find first element with a class name\nfunction findElementByClassName(className) {\n    return document.getElementsByClassName(className)[0];\n}\n// fn: find all elements with a class name\nfunction findAllElementsByClassName(className) {\n    // @ts-ignore\n    return Array.from(document.getElementsByClassName(className));\n}\n/* user interaction functions */\n// fn: hide an element\nfunction hide(element) {\n    element.style.display = \"none\";\n}\n// fn: execute an action\nfunction executeAction(element) {\n    element.classList.toggle('executing');\n    logAction(element.getElementsByClassName('desc')[0]);\n    payActionCost(element.getElementsByClassName('cost')[0]);\n    post('action', { actionType: element.id })\n        .then((response) => {\n        console.log(response);\n        element.classList.toggle('executing');\n    }).catch((response) => {\n        console.log(response);\n        element.classList.toggle('executing');\n    });\n}\n// fn: log an action given the action description element\nfunction logAction(desc) {\n    const actionDescText = getStrOrError(desc.textContent);\n    const logText = createLogEntry(actionDescText);\n    appendLogEntry(logText);\n}\n// fn: create a log entry from the passed text\nfunction createLogEntry(text) {\n    return `You ${text}ed.`;\n}\n// fn: append a log entry based on the passed text\nfunction appendLogEntry(text) {\n    const log = findElementByClassName('log');\n    const entry = document.createElement('li');\n    entry.className = 'log-entry';\n    entry.textContent = text;\n    log.appendChild(entry);\n}\n// fn: pay the cost of an action given the action cost element\nfunction payActionCost(cost) {\n    const costText = getStrOrError(cost.textContent);\n    const costAmount = parseDuration(costText);\n    advanceClock(costAmount);\n}\n// fn: parse duration in hours from a display string\nfunction parseDuration(displayString) {\n    // this split returns an empty string in [0], number in [1], and unit in [2]\n    const [_, amountText, unit] = displayString.split(/(\\d+)/);\n    let amount = parseInt(amountText);\n    switch (unit) {\n        case 'h':\n            break;\n        case 'm':\n            amount /= 60;\n            break;\n        case 'd':\n            amount *= 24;\n            break;\n        default:\n            throw new Error(`Invalid duration unit: ${unit}`);\n    }\n    return amount;\n}\n// fn: advance the game clock by the passed amount {\nfunction advanceClock(amount) {\n    const clockEl = findElementByClassName('clock');\n    const [newDay, newTime] = calcNewClockValues(clockEl.dataset, amount);\n    const newDisplay = genClockDisplayValue(newDay, newTime);\n    setClockValues(clockEl, newDay, newTime, newDisplay);\n}\n// fn: add new time to current time and advance day if necessary\nfunction calcNewClockValues(clockData, amount) {\n    if (clockData.day === undefined || clockData.time === undefined) {\n        throw new Error('Clock data is missing');\n    }\n    const day = parseInt(clockData.day);\n    const time = parseFloat(clockData.time); // preserve decimal places for eg half hours\n    const newTime = time + amount;\n    if (newTime >= 24) {\n        const daysToAdd = Math.floor(newTime / 24);\n        return [(day + daysToAdd) % 7, newTime % 24];\n    }\n    else {\n        return [day, newTime];\n    }\n}\n// fn: generate a display string for the clock\nfunction genClockDisplayValue(day, time) {\n    if (day < 0 || day > 6 || time < 0 || time > 24) {\n        throw new Error('Invalid day or time');\n    }\n    const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];\n    const weekdayText = WEEKDAYS[day];\n    let hourText;\n    if (time > 12) {\n        hourText = `${Math.floor(time - 12)}`;\n    }\n    else if (time < 1) {\n        hourText = '12';\n    }\n    else {\n        hourText = `${Math.floor(time)}`;\n    }\n    const hasMinutes = time % 1 !== 0;\n    let minuteText = '';\n    if (hasMinutes) {\n        minuteText = `:${Math.floor(time % 1 * 60)}`;\n    }\n    const timeSuffix = time >= 12 ? 'pm' : 'am';\n    return `${weekdayText} ${hourText}${minuteText}${timeSuffix}`;\n}\n// fn: update the values in the clock element\nfunction setClockValues(clockEl, day, time, display) {\n    clockEl.dataset.day = day.toString();\n    clockEl.dataset.time = time.toString();\n    clockEl.innerText = display;\n}\n// fn: code to run when the page loads\nfunction setup() {\n    console.log('setting up');\n    listenOnElement('message', 'click', hide);\n    listenOnElements('action', 'click', executeAction);\n}\nif (typeof window !== \"undefined\") {\n    window.onload = setup;\n}\n\n// fn: given a post url and a data object, make an xhr call to the server and return the response\nfunction post(url, data) {\n    const csrftoken = getStrOrError(js_cookie__WEBPACK_IMPORTED_MODULE_0__[\"default\"].get('csrftoken'));\n    console.log(url);\n    console.log(csrftoken);\n    return new Promise((resolve, reject) => {\n        const xhr = new XMLHttpRequest();\n        xhr.open('POST', url);\n        xhr.setRequestHeader('Content-Type', 'application/json');\n        xhr.setRequestHeader('X-CSRFToken', csrftoken);\n        xhr.send(JSON.stringify(data));\n        xhr.onload = () => {\n            if (xhr.status === 200) {\n                resolve(JSON.parse(xhr.responseText));\n            }\n            else {\n                reject(xhr.responseText);\n            }\n        };\n    });\n}\n// fn: check if a value is a string, and throw an error if not\nfunction getStrOrError(str) {\n    if (typeof str !== 'string') {\n        throw new Error(`Expected string, got ${typeof str}`);\n    }\n    return str;\n}\n\n\n//# sourceURL=webpack:///./mythgarden/static/mythgarden/script.ts?");

/***/ }),

/***/ "./node_modules/js-cookie/dist/js.cookie.mjs":
/*!***************************************************!*\
  !*** ./node_modules/js-cookie/dist/js.cookie.mjs ***!
  \***************************************************/
/***/ ((__unused_webpack___webpack_module__, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"default\": () => (__WEBPACK_DEFAULT_EXPORT__)\n/* harmony export */ });\n/*! js-cookie v3.0.1 | MIT */\n/* eslint-disable no-var */\nfunction assign (target) {\n  for (var i = 1; i < arguments.length; i++) {\n    var source = arguments[i];\n    for (var key in source) {\n      target[key] = source[key];\n    }\n  }\n  return target\n}\n/* eslint-enable no-var */\n\n/* eslint-disable no-var */\nvar defaultConverter = {\n  read: function (value) {\n    if (value[0] === '\"') {\n      value = value.slice(1, -1);\n    }\n    return value.replace(/(%[\\dA-F]{2})+/gi, decodeURIComponent)\n  },\n  write: function (value) {\n    return encodeURIComponent(value).replace(\n      /%(2[346BF]|3[AC-F]|40|5[BDE]|60|7[BCD])/g,\n      decodeURIComponent\n    )\n  }\n};\n/* eslint-enable no-var */\n\n/* eslint-disable no-var */\n\nfunction init (converter, defaultAttributes) {\n  function set (key, value, attributes) {\n    if (typeof document === 'undefined') {\n      return\n    }\n\n    attributes = assign({}, defaultAttributes, attributes);\n\n    if (typeof attributes.expires === 'number') {\n      attributes.expires = new Date(Date.now() + attributes.expires * 864e5);\n    }\n    if (attributes.expires) {\n      attributes.expires = attributes.expires.toUTCString();\n    }\n\n    key = encodeURIComponent(key)\n      .replace(/%(2[346B]|5E|60|7C)/g, decodeURIComponent)\n      .replace(/[()]/g, escape);\n\n    var stringifiedAttributes = '';\n    for (var attributeName in attributes) {\n      if (!attributes[attributeName]) {\n        continue\n      }\n\n      stringifiedAttributes += '; ' + attributeName;\n\n      if (attributes[attributeName] === true) {\n        continue\n      }\n\n      // Considers RFC 6265 section 5.2:\n      // ...\n      // 3.  If the remaining unparsed-attributes contains a %x3B (\";\")\n      //     character:\n      // Consume the characters of the unparsed-attributes up to,\n      // not including, the first %x3B (\";\") character.\n      // ...\n      stringifiedAttributes += '=' + attributes[attributeName].split(';')[0];\n    }\n\n    return (document.cookie =\n      key + '=' + converter.write(value, key) + stringifiedAttributes)\n  }\n\n  function get (key) {\n    if (typeof document === 'undefined' || (arguments.length && !key)) {\n      return\n    }\n\n    // To prevent the for loop in the first place assign an empty array\n    // in case there are no cookies at all.\n    var cookies = document.cookie ? document.cookie.split('; ') : [];\n    var jar = {};\n    for (var i = 0; i < cookies.length; i++) {\n      var parts = cookies[i].split('=');\n      var value = parts.slice(1).join('=');\n\n      try {\n        var foundKey = decodeURIComponent(parts[0]);\n        jar[foundKey] = converter.read(value, foundKey);\n\n        if (key === foundKey) {\n          break\n        }\n      } catch (e) {}\n    }\n\n    return key ? jar[key] : jar\n  }\n\n  return Object.create(\n    {\n      set: set,\n      get: get,\n      remove: function (key, attributes) {\n        set(\n          key,\n          '',\n          assign({}, attributes, {\n            expires: -1\n          })\n        );\n      },\n      withAttributes: function (attributes) {\n        return init(this.converter, assign({}, this.attributes, attributes))\n      },\n      withConverter: function (converter) {\n        return init(assign({}, this.converter, converter), this.attributes)\n      }\n    },\n    {\n      attributes: { value: Object.freeze(defaultAttributes) },\n      converter: { value: Object.freeze(converter) }\n    }\n  )\n}\n\nvar api = init(defaultConverter, { path: '/' });\n/* eslint-enable no-var */\n\n/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (api);\n\n\n//# sourceURL=webpack:///./node_modules/js-cookie/dist/js.cookie.mjs?");

/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
/******/ 	/* webpack/runtime/define property getters */
/******/ 	(() => {
/******/ 		// define getter functions for harmony exports
/******/ 		__webpack_require__.d = (exports, definition) => {
/******/ 			for(var key in definition) {
/******/ 				if(__webpack_require__.o(definition, key) && !__webpack_require__.o(exports, key)) {
/******/ 					Object.defineProperty(exports, key, { enumerable: true, get: definition[key] });
/******/ 				}
/******/ 			}
/******/ 		};
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/hasOwnProperty shorthand */
/******/ 	(() => {
/******/ 		__webpack_require__.o = (obj, prop) => (Object.prototype.hasOwnProperty.call(obj, prop))
/******/ 	})();
/******/ 	
/******/ 	/* webpack/runtime/make namespace object */
/******/ 	(() => {
/******/ 		// define __esModule on exports
/******/ 		__webpack_require__.r = (exports) => {
/******/ 			if(typeof Symbol !== 'undefined' && Symbol.toStringTag) {
/******/ 				Object.defineProperty(exports, Symbol.toStringTag, { value: 'Module' });
/******/ 			}
/******/ 			Object.defineProperty(exports, '__esModule', { value: true });
/******/ 		};
/******/ 	})();
/******/ 	
/************************************************************************/
/******/ 	
/******/ 	// startup
/******/ 	// Load entry module and return exports
/******/ 	// This entry module can't be inlined because the eval devtool is used.
/******/ 	var __webpack_exports__ = __webpack_require__("./mythgarden/static/mythgarden/script.ts");
/******/ 	
/******/ })()
;