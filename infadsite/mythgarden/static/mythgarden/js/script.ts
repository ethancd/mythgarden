// A typescript file for the game Mythgarden

import {
    findElementByClassName,
    listenOnElement,
    hide,
    show,
} from './dom';

import Hero from './hero';
import Inventory from './inventory';
import ActionsList from './action';
import VillagersList from "./villager";
import BuildingsList from "./building";
import Clock from "./clock";
import Wallet from "./wallet";
import Dialogue from "./dialogue";

import ReactDOM from "react-dom/client";
import React from "react";


// fn: update the page with the results of an action
function updatePage(response: any) {
    if (response.hero) renderHero(response.hero);
    if (response.clock) renderClock(response.clock);
    if (response.wallet) renderWallet(response.wallet);
    if (response.place) updateLocation(response.place);
    if (response.inventory) renderInventory(response.inventory);
    if (response.buildings) renderBuildingsList(response.buildings);
    if (response.local_item_tokens) renderLocalItemsList(response.local_item_tokens);
    if (response.villager_states) renderVillagersList(response.villager_states);
    if (response.dialogue) {
        renderDialogue(response.dialogue);
    } else {
        renderDialogue({}, false);
    }

    appendLogEntry(response.log_statement);
    renderActionsList(response.actions);
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

export {
    updatePage,
    passErrorToUser,
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


// fn: clear the displayed local items
function clearLocalItems() {
    renderLocalItemsList([])
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

function setUpRootNode(componentName) {
    const rootNode = document.getElementById(`${componentName}-root`);
    window[`${componentName}Root`] = ReactDOM.createRoot(rootNode);
}

function renderHero(heroData) {
    window.heroRoot.render(React.createElement(Hero, heroData));
}
function renderClock(value) {
    window.clockRoot.render(React.createElement(Clock, {value}));
}

function renderWallet(value) {
    window.walletRoot.render(React.createElement(Wallet, {value}));
}

function renderInventory(items) {
    window.inventoryRoot.render(React.createElement(Inventory, {items, orientation: 'horizontal', id: 'inventory'}));
}

function renderActionsList(actions) {
    window.actionsRoot.render(React.createElement(ActionsList, {actions, updatePage, passErrorToUser}));
}

function renderLocalItemsList(items) {
    window.localItemsRoot.render(React.createElement(Inventory, {items, orientation: 'horizontal', id: 'local-items'}));
}

function renderVillagersList(villagers) {
    window.villagersRoot.render(React.createElement(VillagersList, {villagers}));
}

function renderBuildingsList(buildings) {
    window.buildingsRoot.render(React.createElement(BuildingsList, {buildings}));
}

function renderDialogue(dialogue, shouldShow=true) {
    console.log(dialogue)
    console.log(shouldShow)
    window.dialogueRoot.render(React.createElement(Dialogue, { ...dialogue, key: dialogue.id, shouldShow }));
}

// fn: code to run when the page loads
function setup() {
    console.log('setting up')

    const appData = JSON.parse(document.getElementById('app-data').textContent);

    [ 'hero', 'clock', 'wallet', 'inventory', 'actions', 'localItems', 'villagers', 'buildings', 'dialogue'].forEach(setUpRootNode);

    renderHero(appData.hero)
    renderClock(appData.clock)
    renderWallet(appData.wallet)
    renderInventory(appData.inventory)
    renderActionsList(appData.actions)
    renderLocalItemsList(appData.local_item_tokens)
    renderVillagersList(appData.villager_states)
    renderBuildingsList(appData.buildings)

    listenOnElement('message', 'click', hide);
}

if (typeof window !== "undefined") {
    window.onload = setup;
}