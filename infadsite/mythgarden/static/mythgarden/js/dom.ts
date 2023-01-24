/* DOM functions */

// fn: add an event listener to an element (specified by class name)
function listenOnElement(className: string, event: string, fn: Function) {
    const element = findElementByClassName(className);
    _listen(element, event, fn);
}

function listenOnElements(className: string, event: string, fn: Function) {
    const elements = findAllElementsByClassName(className);
    elements.forEach(element => _listen(element, event, fn));
}

function _listen(element: HTMLElement, event: string, fn: Function) {
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


export {
    listenOnElement,
    listenOnElements,
    findElementByClassName,
    findAllElementsByClassName,
}