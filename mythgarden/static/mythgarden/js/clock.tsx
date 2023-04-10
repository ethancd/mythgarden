'use strict'

import React from 'react'

import {type HeroData} from './hero'
import RainbowText from "./rainbowText";

const LATE_WARNING_TIME = 20 * 60
const VERY_LATE_WARNING_TIME = 22 * 60
const VERY_VERY_LATE_WARNING_TIME = 23.5 * 60

export default function Clock ({ display, time, boostLevel, luckPercent }: ClockProps): JSX.Element {
  function getLateness(time: number) {
    if (time >= VERY_VERY_LATE_WARNING_TIME) return 'very-very-late'
    if (time >= VERY_LATE_WARNING_TIME) return 'very-late'
    if (time >= LATE_WARNING_TIME) return 'late'
    return ''
  }

  const lateness = getLateness(time)

  return (
      <div id="clock">
        <div className={lateness}>{display}</div>
        { boostLevel > 0
          ? <div id="boost">lvl.{boostLevel}</div>
          : null }
        { luckPercent != ''
          ? <div id='luck-percent'>{`+${luckPercent}`} <RainbowText text={'luck'} shading={0.35}></RainbowText></div>
          : null
        }
      </div>
  )
}

interface ClockData {
  display: string
  time: number
  dayNumber: number
}

type ClockProps = Pick<ClockData, 'display' | 'time'> & Pick<HeroData, 'boostLevel'|'luckPercent'>

export { Clock, type ClockData }
