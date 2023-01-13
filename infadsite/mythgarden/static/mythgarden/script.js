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
}
// fn: code to run when the page loads
function setup() {
    console.log('setting up');
    listenOnElement('message', 'click', hide);
    listenOnElements('action', 'click', executeAction);
}
window.onload = setup;
