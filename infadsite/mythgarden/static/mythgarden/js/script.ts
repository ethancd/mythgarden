// A typescript file for the game Mythgarden

import {
  findElementByClassName
} from './dom'

// fn: append a log entry based on the passed text
function appendLogEntry (text: string) {
  console.log('appending log entry')
  const log = findElementByClassName('log')
  const entry = document.createElement('li')
  entry.className = 'log-entry'
  entry.textContent = text
  log.appendChild(entry)
}
