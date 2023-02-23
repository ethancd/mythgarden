// A typescript file for the game Mythgarden
import Cookies from 'js-cookie'
/* DOM functions */
// fn: add an event listener to an element (specified by class name)
function listenOnElement (className, event, fn) {
  const element = findElementByClassName(className)
  listen(element, event, fn)
}
function listenOnElements (className, event, fn) {
  const elements = findAllElementsByClassName(className)
  elements.forEach(element => listen(element, event, fn))
}
function listen (element, event, fn) {
  element.addEventListener(event, () => {
    fn(element)
    console.log(`${element.tagName}.${element.className}#${element.id} ${event} event fired`)
  })
  // @ts-ignore
  console.log(`bound ${element.className} on ${event} to ${fn.name}`)
}
// fn: find first element with a class name
function findElementByClassName (className) {
  return document.getElementsByClassName(className)[0]
}
// fn: find all elements with a class name
function findAllElementsByClassName (className) {
  // @ts-ignore
  return Array.from(document.getElementsByClassName(className))
}
/* user interaction functions */
// fn: hide an element
function hide (element) {
  element.style.display = 'none'
}
// fn: execute an action
function executeAction (element) {
  element.classList.toggle('executing')
  logAction(element.getElementsByClassName('description')[0])
  payActionCost(element.getElementsByClassName('cost')[0])
  post('action', { actionType: element.id })
    .then((response) => {
      console.log(response)
      element.classList.toggle('executing')
    }).catch((response) => {
      console.log(response)
      element.classList.toggle('executing')
    })
}
// fn: log an action given the action description element
function logAction (desc) {
  const actionDescText = getStrOrError(desc.textContent)
  const logText = createLogEntry(actionDescText)
  appendLogEntry(logText)
}
// fn: create a log entry from the passed text
function createLogEntry (text) {
  return `You ${text}ed.`
}
// fn: append a log entry based on the passed text
function appendLogEntry (text) {
  const log = findElementByClassName('log')
  const entry = document.createElement('li')
  entry.className = 'log-entry'
  entry.textContent = text
  log.appendChild(entry)
}
// fn: pay the cost of an action given the action cost element
function payActionCost (cost) {
  const costText = getStrOrError(cost.textContent)
  const costAmount = parseDuration(costText)
  advanceClock(costAmount)
}
// fn: parse duration in hours from a display string
function parseDuration (displayString) {
  // this split returns an empty string in [0], number in [1], and unit in [2]
  const [_, amountText, unit] = displayString.split(/(\d+)/)
  let amount = parseInt(amountText)
  switch (unit) {
    case 'h':
      break
    case 'm':
      amount /= 60
      break
    case 'd':
      amount *= 24
      break
    default:
      throw new Error(`Invalid duration unit: ${unit}`)
  }
  return amount
}
// fn: advance the game clock by the passed amount {
function advanceClock (amount) {
  const clockEl = findElementByClassName('clock')
  const [newDay, newTime] = calcNewClockValues(clockEl.dataset, amount)
  const newDisplay = genClockDisplayValue(newDay, newTime)
  setClockValues(clockEl, newDay, newTime, newDisplay)
}
// fn: add new time to current time and advance day if necessary
function calcNewClockValues (clockData, amount) {
  if (clockData.day === undefined || clockData.time === undefined) {
    throw new Error('Clock data is missing')
  }
  const day = parseInt(clockData.day)
  const time = parseFloat(clockData.time) // preserve decimal places for eg half hours
  const newTime = time + amount
  if (newTime >= 24) {
    const daysToAdd = Math.floor(newTime / 24)
    return [(day + daysToAdd) % 7, newTime % 24]
  } else {
    return [day, newTime]
  }
}
// fn: generate a display string for the clock
function genClockDisplayValue (day, time) {
  if (day < 0 || day > 6 || time < 0 || time > 24) {
    throw new Error('Invalid day or time')
  }
  const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
  const weekdayText = WEEKDAYS[day]
  let hourText = ''
  if (time > 12) {
    hourText = `${Math.floor(time - 12)}`
  } else if (time < 1) {
    hourText = '12'
  } else {
    hourText = `${Math.floor(time)}`
  }
  const hasMinutes = time % 1 !== 0
  let minuteText = ''
  if (hasMinutes) {
    minuteText = `:${Math.floor(time % 1 * 60)}`
  }
  const timeSuffix = time >= 12 ? 'pm' : 'am'
  return `${weekdayText} ${hourText}${minuteText}${timeSuffix}`
}
// fn: update the values in the clock element
function setClockValues (clockEl, day, time, display) {
  clockEl.dataset.day = day.toString()
  clockEl.dataset.time = time.toString()
  clockEl.innerText = display
}
// fn: code to run when the page loads
function setup () {
  console.log('setting up')
  listenOnElement('message', 'click', hide)
  listenOnElements('action', 'click', executeAction)
}
if (typeof window !== 'undefined') {
  window.onload = setup
}
export { createLogEntry, parseDuration, calcNewClockValues, genClockDisplayValue }
// fn: given a post url and a data object, make an xhr call to the server and return the response
function post (url, data) {
  const csrftoken = getStrOrError(Cookies.get('csrftoken'))
  console.log(url)
  console.log(csrftoken)
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', url)
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.setRequestHeader('X-CSRFToken', csrftoken)
    xhr.send(JSON.stringify(data))
    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        reject(xhr.responseText)
      }
    }
  })
}
// fn: check if a value is a string, and throw an error if not
function getStrOrError (str) {
  if (typeof str !== 'string') {
    throw new Error(`Expected string, got ${typeof str}`)
  }
  return str
}
