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

            if (response.game_over) {
                window.location.href = '/';
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
    if (response.hero) setScoreValue(response.hero);
    if (response.clock) setClockValue(response.clock);
    if (response.wallet) setWalletValue(response.wallet);
    if (response.place) updateLocation(response.place);
    if (response.inventory) updateInventory(response.inventory);
    if (response.buildings) updateBuildings(response.buildings);
    if (response.local_item_tokens) updateLocalItems(response.local_item_tokens);
    if (response.villager_states) updateVillagers(response.villager_states);
    if (response.dialogue) {
        showDialogue(response.dialogue);
    } else {
        hideDialogue();
    }

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

// fn: update the displayed score
function setScoreValue(hero: any) {
    console.log('updating score')
    const scoreEl = findElementByClassName('score');
    scoreEl.innerText = `${hero.score} (⚜️${hero.koin_earned} x ${hero.hearts_earned}❤️)`
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
    clearLocalItems();
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
function createItemElement(item_token: any) {
    const itemEl = document.createElement('li');
    itemEl.className = 'item';
    itemEl.classList.toggle('watered', item_token.has_been_watered);
    itemEl.classList.add(item_token.rarity);
    itemEl.innerHTML = `<span class="item-name">${item_token.name}</span>`;

    return itemEl;
}

// fn: update the displayed buildings
function updateBuildings(buildings: any[]) {
    console.log('updating buildings');
    const buildingsEl = findElementByClassName('buildings');
    clearList(buildingsEl);

    buildings.forEach((building) => {
        const buildingEl = createBuildingElement(building);
        buildingsEl.appendChild(buildingEl);
    });
}

// fn: create a building element
function createBuildingElement(building: any) {
    const buildingEl = document.createElement('li');
    buildingEl.className = 'building';
    buildingEl.innerHTML = `<span class="building-name">${building.name}</span>`;

    return buildingEl;
}

// fn: clear the displayed local items
function clearLocalItems() {
    const contentsEl = findElementByClassName('contents');

    if (contentsEl) {
        clearList(contentsEl);
    }
}

// fn: update the displayed local items
function updateLocalItems(local_item_tokens: any[]) {
    console.log('updating local items');
    const contentsEl = findElementByClassName('contents');
    if (!contentsEl) {
        console.log('no contents element found');
        return;
    }
    clearList(contentsEl);

    local_item_tokens.forEach((item_token) => {
        const itemEl = createItemElement(item_token);
        contentsEl.appendChild(itemEl);
    });
}

// fn: update the displayed villagers
function updateVillagers(villager_states: any[]) {
    console.log('updating villagers');
    const villagersEl = findElementByClassName('villagers');
    clearList(villagersEl);

    villager_states.forEach((villager_state) => {
        const villagerEl = createVillagerElement(villager_state);
        villagersEl.appendChild(villagerEl);
    });
}

// fn: create a villager element
function createVillagerElement(villager_state: any) {
    const villagerEl = document.createElement('li');
    villagerEl.className = 'villager';
    villagerEl.innerHTML = `<span class="villager-name">${villager_state.villager.name}</span>\
                            <span class="villager-state">${villager_state.display_affinity}</span>`;

    return villagerEl;
}


// fn: show the dialogue box with dialogue text and speaker info
function showDialogue(dialogue: any) {
    console.log('showing dialogue');
    const dialogueEl = findElementByClassName('dialogue');
    const dialogueTextEl = findElementByClassName('dialogue-text');
    const dialogueSpeakerNameEl = findElementByClassName('speaker-name');
    const dialogueSpeakerPortraitEl = findElementByClassName('speaker-portrait');

    dialogueTextEl.innerText = dialogue.full_text;
    dialogueSpeakerNameEl.innerText = dialogue.speaker.name;
    //@ts-ignore
    dialogueSpeakerPortraitEl.src = dialogue.speaker.portrait.url;

    show(dialogueEl);
}

// fn: hide the dialogue box and empty its contents
function hideDialogue() {
    console.log('hiding dialogue');
    const dialogueEl = findElementByClassName('dialogue');
    hide(dialogueEl);

    const dialogueTextEl = findElementByClassName('dialogue-text');
    const dialogueSpeakerNameEl = findElementByClassName('speaker-name');
    const dialogueSpeakerPortraitEl = findElementByClassName('speaker-portrait');

    dialogueTextEl.innerText = '';
    dialogueSpeakerNameEl.innerText = '';
    //@ts-ignore
    dialogueSpeakerPortraitEl.src = '';
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
    listenOnElement('dialogue', 'click', hide);
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