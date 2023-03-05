'use strict'

import React from 'react'
import { type ClockProps } from './clock'

const SUNRISE = 6 * 60
const SUNSET = 18 * 60
const TIME_IN_12_HOURS = SUNSET - SUNRISE
const TIME_IN_24_HOURS = 24 * 60
const TRUE_DAWN = SUNRISE - 90
const TRUE_NIGHT = SUNSET + 90

const MOON_HI = SUNSET - 30
const MOON_BYE = SUNRISE

const PHASE_WIDTH_STEP = 0.08 // ~ 1 / 14 -- aka how big of steps to take to move from 1 to 0 in 14 days
const INITIAL_PHASE_WIDTH = PHASE_WIDTH_STEP * 6 // this way, the final day will have phase-width = 0 aka half moon

// this equation brought to you by wolfram alpha:
// solving for the parabola with points at (0,0), (.5, 1), and (1, 0)
// (aka sunrise, noon, and sunset)
const parabola = (x: number): number => (4 * x) - (4 * x * x)
const getPercent = (n: number): string => `${n * 100}%`

function Sun ({ time }: Pick<ClockProps, 'time'>): JSX.Element | null {
  const isSunVisible = time > TRUE_DAWN && time < TRUE_NIGHT
  const isSunUp = time >= SUNRISE && time <= SUNSET

  function getX (time: number): number {
    if (isSunUp) {
      const timePastSunrise = time - SUNRISE
      return timePastSunrise / TIME_IN_12_HOURS
    } else {
      const timeUntilSunrise = (SUNRISE + TIME_IN_24_HOURS - time) % TIME_IN_24_HOURS
      return timeUntilSunrise / TIME_IN_12_HOURS
    }
  }

  function getY (x: number): number {
    if (isSunUp) {
      return parabola(x)
    } else {
      return -parabola(x)
    }
  }

  const x = getX(time)
  const y = getY(x)

  if (isSunVisible) {
    return (
      <div id="sun" style={{ left: getPercent(x), bottom: getPercent(y) }}></div>
    )
  } else {
    return null
  }
}

// eslint-disable-next-line @typescript-eslint/naming-convention
function Moon ({ time, day_number }: Pick<ClockProps, 'time' | 'day_number'>): JSX.Element | null {
  const isMoonVisible = time < MOON_BYE || time > MOON_HI

  const isMoonUp = time <= SUNRISE || time >= SUNSET

  function getX (time: number): number {
    if (isMoonUp) {
      const timePastSunset = (time + TIME_IN_24_HOURS - SUNSET) % TIME_IN_24_HOURS
      return timePastSunset / TIME_IN_12_HOURS
    } else {
      const timeUntilSunset = SUNSET - time
      return timeUntilSunset / TIME_IN_12_HOURS
    }
  }

  function getY (x: number): number {
    if (isMoonUp) {
      return parabola(x)
    } else {
      return -parabola(x)
    }
  }

  // eslint-disable-next-line @typescript-eslint/naming-convention
  function getPhaseWidth (day_number: number): number {
    return INITIAL_PHASE_WIDTH - (PHASE_WIDTH_STEP * day_number)
  }

  const x = getX(time)
  const y = getY(x)
  const phaseWidth = getPhaseWidth(day_number)

  console.log(day_number)

  if (isMoonVisible) {
    return (
      <div id="moon" style={{ left: getPercent(x), bottom: getPercent(y) }}>
        <div id="darkside"></div>
        <div id="ellipse" style={{ width: getPercent(phaseWidth) }}></div>
      </div>
    )
  } else {
    return null
  }
}

export {
  Sun,
  Moon
}
