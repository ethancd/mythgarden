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

/***/ "./mythgarden/static/mythgarden/js/ajax.ts":
/*!*************************************************!*\
  !*** ./mythgarden/static/mythgarden/js/ajax.ts ***!
  \*************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"post\": () => (/* binding */ post)\n/* harmony export */ });\n/* harmony import */ var js_cookie__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! js-cookie */ \"./node_modules/js-cookie/dist/js.cookie.mjs\");\n/* harmony import */ var _staticUtils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./staticUtils */ \"./mythgarden/static/mythgarden/js/staticUtils.ts\");\n\n\n// fn: given a post url and a data object, make an xhr call to the server and return the response\nfunction post(url, data) {\n    const csrftoken = (0,_staticUtils__WEBPACK_IMPORTED_MODULE_1__.getStrOrError)(js_cookie__WEBPACK_IMPORTED_MODULE_0__[\"default\"].get('csrftoken'));\n    return new Promise((resolve, reject) => {\n        const xhr = new XMLHttpRequest();\n        xhr.open('POST', url);\n        xhr.setRequestHeader('Content-Type', 'application/json');\n        xhr.setRequestHeader('X-CSRFToken', csrftoken);\n        xhr.send(JSON.stringify(data));\n        xhr.onload = () => {\n            if (xhr.status === 200) {\n                resolve(JSON.parse(xhr.responseText));\n            }\n            else {\n                reject(xhr.responseText);\n            }\n        };\n    });\n}\n\n\n\n//# sourceURL=webpack:///./mythgarden/static/mythgarden/js/ajax.ts?");

/***/ }),

/***/ "./mythgarden/static/mythgarden/js/dom.ts":
/*!************************************************!*\
  !*** ./mythgarden/static/mythgarden/js/dom.ts ***!
  \************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"clearList\": () => (/* binding */ clearList),\n/* harmony export */   \"findAllElementsByClassName\": () => (/* binding */ findAllElementsByClassName),\n/* harmony export */   \"findElementByClassName\": () => (/* binding */ findElementByClassName),\n/* harmony export */   \"hide\": () => (/* binding */ hide),\n/* harmony export */   \"listenOnElement\": () => (/* binding */ listenOnElement),\n/* harmony export */   \"listenOnElements\": () => (/* binding */ listenOnElements),\n/* harmony export */   \"show\": () => (/* binding */ show)\n/* harmony export */ });\n/* DOM functions */\n// fn: add an event listener to an element (specified by class name)\nfunction listenOnElement(className, event, fn) {\n    const element = findElementByClassName(className);\n    _listen(element, event, fn);\n}\nfunction listenOnElements(className, event, fn) {\n    const elements = findAllElementsByClassName(className);\n    elements.forEach(element => _listen(element, event, fn));\n}\nfunction _listen(element, event, fn) {\n    element.addEventListener(event, () => {\n        fn(element);\n        console.log(`${element.tagName}.${element.className}#${element.id} ${event} event fired`);\n    });\n    // @ts-ignore\n    console.log(`bound ${element.className} on ${event} to ${fn.name}`);\n}\n// fn: find first element with a class name\nfunction findElementByClassName(className) {\n    return document.getElementsByClassName(className)[0];\n}\n// fn: find all elements with a class name\nfunction findAllElementsByClassName(className) {\n    // @ts-ignore\n    return Array.from(document.getElementsByClassName(className));\n}\n// fn: hide an element\nfunction hide(element) {\n    element.style.display = \"none\";\n}\n// fn: show an element\nfunction show(element) {\n    element.style.display = \"block\";\n}\n// fn: remove an element's contents (child elements)\nfunction clearList(element) {\n    while (element.firstChild) {\n        element.removeChild(element.firstChild);\n    }\n}\n\n\n\n//# sourceURL=webpack:///./mythgarden/static/mythgarden/js/dom.ts?");

/***/ }),

/***/ "./mythgarden/static/mythgarden/js/script.ts":
/*!***************************************************!*\
  !*** ./mythgarden/static/mythgarden/js/script.ts ***!
  \***************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony import */ var _dom__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./dom */ \"./mythgarden/static/mythgarden/js/dom.ts\");\n/* harmony import */ var _ajax__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./ajax */ \"./mythgarden/static/mythgarden/js/ajax.ts\");\n// A typescript file for the game Mythgarden\n\n\n// fn: execute a user's chosen action by sending a request to the server and updating the page with the results\nfunction executeAction(element) {\n    element.classList.toggle('executing');\n    const description = getActionDescription(element);\n    (0,_ajax__WEBPACK_IMPORTED_MODULE_1__.post)('action', { description })\n        .then((response) => {\n        console.log(response);\n        if (response.error) {\n            throw response;\n        }\n        updatePage(response);\n        element.classList.toggle('executing');\n    }).catch((response) => {\n        console.log(response);\n        passErrorToUser(response);\n        element.classList.toggle('executing');\n    });\n}\n// fn: get the description of an action element\nfunction getActionDescription(element) {\n    const descriptionEl = element.getElementsByClassName('description')[0];\n    const description = descriptionEl.innerText;\n    return description;\n}\n// fn: update the page with the results of an action\nfunction updatePage(response) {\n    if (response.clock)\n        setClockValue(response.clock);\n    if (response.wallet)\n        setWalletValue(response.wallet);\n    if (response.place)\n        updateLocation(response.place);\n    if (response.inventory)\n        updateInventory(response.inventory);\n    if (response.buildings)\n        updateBuildings(response.buildings);\n    if (response.local_item_tokens)\n        updateLocalItems(response.local_item_tokens);\n    if (response.villager_states)\n        updateVillagers(response.villager_states);\n    appendLogEntry(response.log_statement);\n    updateActions(response.actions);\n    rebind();\n}\n// fn: put error message in user-facing message box\nfunction passErrorToUser(response) {\n    const message = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('message');\n    if (response.error) {\n        message.innerText = response.error;\n    }\n    else {\n        message.innerText = \"Unexpected server error 😳\";\n    }\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.show)(message);\n}\n// fn: update the display value of the clock element\nfunction setClockValue(display) {\n    console.log('updating clock');\n    const clockEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('clock');\n    clockEl.innerText = display;\n}\n// fn: update the display value of the wallet element\nfunction setWalletValue(display) {\n    console.log('updating wallet');\n    const walletEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('wallet');\n    walletEl.innerText = display;\n}\n// fn: update displayed location name and landscape to the new location\nfunction updateLocation(location) {\n    console.log('updating location');\n    setLocationNameValue(location.name);\n    updateLocationLandscapeImage(location.image.url);\n    clearLocalItems();\n}\n// fn: update the displayed location name\nfunction setLocationNameValue(name) {\n    const locationNameEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('location');\n    locationNameEl.innerText = name;\n}\n// fn: update the displayed location landscape image\nfunction updateLocationLandscapeImage(url) {\n    const landscapeEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('landscape');\n    //@ts-ignore\n    landscapeEl.src = url;\n}\n// fn: update the displayed inventory\nfunction updateInventory(inventory) {\n    console.log('updating inventory');\n    const inventoryEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('inventory');\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.clearList)(inventoryEl);\n    inventory.forEach((item) => {\n        const itemEl = createItemElement(item);\n        inventoryEl.appendChild(itemEl);\n    });\n}\n// fn: create an item element\nfunction createItemElement(item_token) {\n    const itemEl = document.createElement('li');\n    itemEl.className = 'item';\n    itemEl.classList.toggle('watered', item_token.has_been_watered);\n    itemEl.innerHTML = `<span class=\"item-name\">${item_token.name}</span>`;\n    return itemEl;\n}\n// fn: update the displayed buildings\nfunction updateBuildings(buildings) {\n    console.log('updating buildings');\n    const buildingsEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('buildings');\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.clearList)(buildingsEl);\n    buildings.forEach((building) => {\n        const buildingEl = createBuildingElement(building);\n        buildingsEl.appendChild(buildingEl);\n    });\n}\n// fn: create a building element\nfunction createBuildingElement(building) {\n    const buildingEl = document.createElement('li');\n    buildingEl.className = 'building';\n    buildingEl.innerHTML = `<span class=\"building-name\">${building.name}</span>`;\n    return buildingEl;\n}\n// fn: clear the displayed local items\nfunction clearLocalItems() {\n    const contentsEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('contents');\n    if (contentsEl) {\n        (0,_dom__WEBPACK_IMPORTED_MODULE_0__.clearList)(contentsEl);\n    }\n}\n// fn: update the displayed local items\nfunction updateLocalItems(local_item_tokens) {\n    console.log('updating local items');\n    const contentsEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('contents');\n    if (!contentsEl) {\n        console.log('no contents element found');\n        return;\n    }\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.clearList)(contentsEl);\n    local_item_tokens.forEach((item_token) => {\n        const itemEl = createItemElement(item_token);\n        contentsEl.appendChild(itemEl);\n    });\n}\n// fn: update the displayed villagers\nfunction updateVillagers(villager_states) {\n    console.log('updating villagers');\n    const villagersEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('villagers');\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.clearList)(villagersEl);\n    villager_states.forEach((villager_state) => {\n        const villagerEl = createVillagerElement(villager_state);\n        villagersEl.appendChild(villagerEl);\n    });\n}\n// fn: create a villager element\nfunction createVillagerElement(villager_state) {\n    const villagerEl = document.createElement('li');\n    villagerEl.className = 'villager';\n    villagerEl.innerHTML = `<span class=\"villager-name\">${villager_state.villager.name}</span>\\\n                            <span class=\"villager-state\">${villager_state.display_affinity}</span>`;\n    return villagerEl;\n}\n// fn: append a log entry based on the passed text\nfunction appendLogEntry(text) {\n    console.log('appending log entry');\n    const log = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('log');\n    const entry = document.createElement('li');\n    entry.className = 'log-entry';\n    entry.textContent = text;\n    log.appendChild(entry);\n}\n// fn: update the displayed actions\nfunction updateActions(actions) {\n    console.log('updating actions');\n    const actionsEl = (0,_dom__WEBPACK_IMPORTED_MODULE_0__.findElementByClassName)('actions');\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.clearList)(actionsEl);\n    actions.forEach((action) => {\n        const actionEl = createActionElement(action);\n        actionsEl.appendChild(actionEl);\n    });\n}\n// fn: create an action element\nfunction createActionElement(action) {\n    const actionEl = document.createElement('li');\n    actionEl.className = 'action';\n    actionEl.innerHTML = `<span class=\"description\">${action.description}</span>\\\n                          <span class=\"cost\">${action.display_cost}</span>`;\n    return actionEl;\n}\n// fn: code to run when the page loads\nfunction setup() {\n    console.log('setting up');\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.listenOnElement)('message', 'click', _dom__WEBPACK_IMPORTED_MODULE_0__.hide);\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.listenOnElements)('action', 'click', executeAction);\n}\n// fn: code to run after the page has been updated\nfunction rebind() {\n    console.log('rebinding');\n    (0,_dom__WEBPACK_IMPORTED_MODULE_0__.listenOnElements)('action', 'click', executeAction);\n}\nif (typeof window !== \"undefined\") {\n    window.onload = setup;\n}\n\n\n//# sourceURL=webpack:///./mythgarden/static/mythgarden/js/script.ts?");

/***/ }),

/***/ "./mythgarden/static/mythgarden/js/staticUtils.ts":
/*!********************************************************!*\
  !*** ./mythgarden/static/mythgarden/js/staticUtils.ts ***!
  \********************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

eval("__webpack_require__.r(__webpack_exports__);\n/* harmony export */ __webpack_require__.d(__webpack_exports__, {\n/* harmony export */   \"getStrOrError\": () => (/* binding */ getStrOrError)\n/* harmony export */ });\n// fn: check if a value is a string, and throw an error if not\nfunction getStrOrError(str) {\n    if (typeof str !== 'string') {\n        throw new Error(`Expected string, got ${typeof str}`);\n    }\n    return str;\n}\n\n\n\n//# sourceURL=webpack:///./mythgarden/static/mythgarden/js/staticUtils.ts?");

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
/******/ 	var __webpack_exports__ = __webpack_require__("./mythgarden/static/mythgarden/js/script.ts");
/******/ 	
/******/ })()
;