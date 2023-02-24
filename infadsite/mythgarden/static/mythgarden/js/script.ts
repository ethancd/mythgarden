// A typescript file for the game Mythgarden

import {
  findElementByClassName
} from './dom'

import Hero from './hero'
import List from './list'
import Item from './item'
import Action from './action'
import Villager from './villager'
import Building from './building'
import Clock from './clock'
import Wallet from './wallet'
import Dialogue from './dialogue'
import Message from './message'
import Location from './location'

import ReactDOM from 'react-dom/client'
import React from 'react'

// fn: update the page with the results of an action
function updatePage (response: any) {
  console.log('updating page')
  renderApp(response)
  if (response.hero) renderHero(response.hero)
  if (response.clock) renderClock(response.clock)
  if (response.wallet) renderWallet(response.wallet)
  if (response.place) renderLocation(response.place)
  if (response.inventory) renderInventory(response.inventory)
  if (response.buildings) renderBuildingsList(response.buildings)
  if (response.local_item_tokens) renderLocalItemsList(response.local_item_tokens)
  if (response.villager_states) renderVillagersList(response.villager_states)
  if (response.dialogue) {
    renderDialogue(response.dialogue)
  } else {
    renderDialogue({}, false)
  }

  // if (response.error || response.message) {
  //   const value = response.error || response.message
  //   renderMessage(value)
  // } else {
  //   renderMessage('', false)
  // }

  appendLogEntry(response.log_statement)
  renderActionsList(response.actions)
}

// fn: put error message in user-facing message box
function passErrorToUser (response: any) {
  // renderMessage(response.error || 'Unknown error, oops :)', true)
}

export {
  updatePage,
  passErrorToUser
}

// fn: append a log entry based on the passed text
function appendLogEntry (text: string) {
  console.log('appending log entry')
  const log = findElementByClassName('log')
  const entry = document.createElement('li')
  entry.className = 'log-entry'
  entry.textContent = text
  log.appendChild(entry)
}

function setUpRootNode (componentName) {
  const rootNode = document.getElementById(`${componentName}-root`)
  window[`${componentName}Root`] = ReactDOM.createRoot(rootNode)
}

function renderHero (heroData) {
  window.heroRoot.render(React.createElement(Hero, heroData))
}
function renderClock (value) {
  window.clockRoot.render(React.createElement(Clock, { value }))
}

function renderWallet (value) {
  window.walletRoot.render(React.createElement(Wallet, { value }))
}

function renderLocation (location) {
  window.locationRoot.render(React.createElement(Location, location))
  renderLocalItemsList([])
}

function renderInventory (items) {
  const children = items.map(item => Item(item))
  window.inventoryRoot.render(React.createElement(List, { children, orientation: 'horizontal', id: 'inventory' }))
}

function renderActionsList (actions) {
  const children = actions.map(action => Action(action))
  window.actionsRoot.render(React.createElement(List, { children, orientation: 'vertical', id: 'actions' }))
}

function renderLocalItemsList (items) {
  const children = items.map(item => Item(item))
  window.localItemsRoot.render(React.createElement(List, { children, orientation: 'horizontal', id: 'local-items' }))
}

function renderVillagersList (villagers) {
  const children = villagers.map(villager => Villager(villager))
  window.villagersRoot.render(React.createElement(List, { children, orientation: 'vertical', id: 'villagers' }))
}

function renderBuildingsList (buildings) {
  const children = buildings.map(building => Building(building))
  window.buildingsRoot.render(React.createElement(List, { children, orientation: 'horizontal', id: 'buildings' }))
}

function renderDialogue (dialogue, shouldShow = true) {
  window.dialogueRoot.render(React.createElement(Dialogue, { ...dialogue, key: dialogue.id, shouldShow }))
}

function renderMessage (value, shouldShow = true) {
  window.messageRoot.render(React.createElement(Message, { value, key: Math.random(), shouldShow }))
}

// fn: code to run when the page loads
function setup () {
  console.log('setting up')

  const appData = JSON.parse(document.getElementById('app-data').textContent);

  ['hero', 'location', 'clock', 'wallet', 'inventory', 'actions', 'localItems', 'villagers', 'buildings', 'dialogue'].forEach(setUpRootNode)

  renderHero(appData.hero)
  renderClock(appData.clock)
  renderWallet(appData.wallet)
  renderLocation(appData.place)
  renderInventory(appData.inventory)
  renderActionsList(appData.actions)
  renderLocalItemsList(appData.local_item_tokens)
  renderVillagersList(appData.villager_states)
  renderBuildingsList(appData.buildings)
  // const isMessageEmpty = !appData.message || appData.message.length === 0
  // renderMessage(appData.message, !isMessageEmpty)
}

if (typeof window !== 'undefined') {
  // window.onload = setup;
}
