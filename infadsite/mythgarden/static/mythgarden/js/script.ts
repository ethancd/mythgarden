// A typescript file for the game Mythgarden

import {
    findElementByClassName,
    findAllElementsByClassName,
    listenOnElement,
    listenOnElements,
    hide,
    show,
    clearList,
} from './dom';

import {
    post,
} from './ajax';


// fn: execute a user's chosen action by sending a request to the server and updating the page with the results
function executeAction(element: HTMLElement) {
    element.classList.toggle('executing');

    const description = getActionDescription(element);

    post('action', {description})
        .then((response: any) => {
            console.log(response);
            if (response.error) {
                throw response;
            }
            updatePage(response);

            element.classList.toggle('executing');
        }).catch((response: any) => {
            console.log(response)
            passErrorToUser(response);
            element.classList.toggle('executing');
        });
}

// fn: get the description of an action element
function getActionDescription(element: HTMLElement) {
    const descriptionEl = element.getElementsByClassName('description')[0] as HTMLElement;
    const description = descriptionEl.innerText;

    return description;
}

// fn: update the page with the results of an action
function updatePage(response: any) {
    if (response.clock) setClockValue(response.clock);
    if (response.wallet) setWalletValue(response.wallet);
    if (response.place) updateLocation(response.place);
    if (response.inventory) updateInventory(response.inventory);
    if (response.landmarks) updateLandmarks(response.landmarks);
    if (response.landmark_contents) updateLandmarkContents(response.landmark_contents);

    appendLogEntry(response.log_statement);
    updateActions(response.actions);

    rebind();
}

// fn: put error message in user-facing message box
function passErrorToUser(response: any) {
    const message = findElementByClassName('message');

    if (response.error) {
        message.innerText = response.error;
    } else {
        message.innerText = "Unexpected server error 😳";
    }

    show(message);
}

// fn: update the display value of the clock element
function setClockValue(display: string) {
    console.log('updating clock')
    const clockEl = findElementByClassName('clock')
    clockEl.innerText = display;
}

// fn: update the display value of the wallet element
function setWalletValue(display: string) {
    console.log('updating wallet')
    const walletEl = findElementByClassName('wallet')
    walletEl.innerText = display;
}

// fn: update displayed location name and landscape to the new location
function updateLocation(location: any) {
    console.log('updating location');

    setLocationNameValue(location.name);
    updateLocationLandscapeImage(location.image.url);
    clearLandmarkContents();
}

// fn: update the displayed location name
function setLocationNameValue(name: string) {
    const locationNameEl = findElementByClassName('location');
    locationNameEl.innerText = name;
}

// fn: update the displayed location landscape image
function updateLocationLandscapeImage(url: string) {
    const landscapeEl = findElementByClassName('landscape');
    //@ts-ignore
    landscapeEl.src = url;
}

// fn: update the displayed inventory
function updateInventory(inventory: any[]) {
    console.log('updating inventory')
    const inventoryEl = findElementByClassName('inventory');
    clearList(inventoryEl);

    inventory.forEach((item) => {
        const itemEl = createItemElement(item);
        inventoryEl.appendChild(itemEl);
    });
}

// fn: create an item element
function createItemElement(item: any) {
    const itemEl = document.createElement('li');
    itemEl.className = 'item';
    itemEl.innerHTML = `<span class="item-name">${item.name}</span>`;

    return itemEl;
}

// fn: update the displayed landmarks
function updateLandmarks(landmarks: any[]) {
    console.log('updating landmarks');
    const landmarksEl = findElementByClassName('landmarks');
    clearList(landmarksEl);

    landmarks.forEach((landmark) => {
        const landmarkEl = createLandmarkElement(landmark);
        landmarksEl.appendChild(landmarkEl);
    });
}

// fn: create a landmark element
function createLandmarkElement(landmark: any) {
    const landmarkEl = document.createElement('li');
    landmarkEl.className = 'landmark';
    landmarkEl.innerHTML = `<span class="landmark-name">${landmark.name}</span>`;

    if (landmark.is_field_or_shop) {
        landmarkEl.appendChild(createLandmarkContentsElement());
    }

    return landmarkEl;
}

// fn: create an empty landmark contents element
// actual contents will be filled by updateLandmarkContents
function createLandmarkContentsElement() {
    const contentsEl = document.createElement('ul');
    contentsEl.className = 'contents horizontal';

    return contentsEl;
}

// fn: clear the displayed landmark contents
function clearLandmarkContents() {
    const contentsEl = findElementByClassName('contents');

    if (contentsEl) {
        clearList(contentsEl);
    }
}

// fn: update the displayed landmark contents
// assumes that the landmark contents element already exists
function updateLandmarkContents(contents: any[]) {
    console.log('updating landmark contents');
    const contentsEl = findElementByClassName('contents');
    if (!contentsEl) {
        console.log('no contents element found');
        return;
    }
    clearList(contentsEl);

    contents.forEach((item) => {
        const itemEl = createItemElement(item);
        contentsEl.appendChild(itemEl);
    });
}

// fn: append a log entry based on the passed text
function appendLogEntry(text: string) {
    console.log('appending log entry');
    const log = findElementByClassName('log');
    const entry = document.createElement('li');
    entry.className = 'log-entry';
    entry.textContent = text;
    log.appendChild(entry);
}

// fn: update the displayed actions
function updateActions(actions: any[]) {
    console.log('updating actions');
    const actionsEl = findElementByClassName('actions');
    clearList(actionsEl);

    actions.forEach((action) => {
        const actionEl = createActionElement(action);
        actionsEl.appendChild(actionEl);
    });
}

// fn: create an action element
function createActionElement(action: any) {
    const actionEl = document.createElement('li');
    actionEl.className = 'action';
    actionEl.innerHTML = `<span class="description">${action.description}</span>\
                          <span class="cost">${action.display_cost}</span>`;

    return actionEl;
}

// fn: code to run when the page loads
function setup() {
    console.log('setting up')

    listenOnElement('message', 'click', hide);
    listenOnElements('action', 'click', executeAction);
}

// fn: code to run after the page has been updated
function rebind() {
    console.log('rebinding');

    listenOnElements('action', 'click', executeAction);
}

if (typeof window !== "undefined") {
    window.onload = setup;
}