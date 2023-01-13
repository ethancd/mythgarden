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
}


// fn: code to run when the page loads
function setup() {
    console.log('setting up')

    listenOnElement('message', 'click', hide);
    listenOnElements('action', 'click', executeAction);
}

window.onload = setup;