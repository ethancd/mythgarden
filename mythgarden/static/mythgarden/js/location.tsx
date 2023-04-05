'use strict'

import React from 'react'
import Color from 'color'
import { type ColorFilter } from './lightColorLogic'

const MAX_FILTER_OPACITY = 0.5;
export default function Location ({ name, imageUrl, arrows, activities, colorFilter, children }: React.PropsWithChildren<LocationProps & HasColorFilter>): JSX.Element {
  const backgroundColor = Color.rgb(colorFilter.rgbTemperature).darken(colorFilter.shadeBy).hex()
  const opacity = Math.min(colorFilter.shadeBy, MAX_FILTER_OPACITY)

  return (
        <div id='location'>
            <h2 className="name">{ name }</h2>
            <div className='landscape-filter' style={{
              backgroundColor,
              opacity,
            }}></div>
            <div className='darkness-filter'></div>
            <img className="landscape" src={imageUrl}></img>

            <ul className='activities'>
              {activities.map(activity => {
                return (
                  <li
                  className={`local-activity ${activity.actionType.toLowerCase()}`}
                  key={activity.actionType}
                  data-entity-id={activity.id}
                  data-action-type={activity.actionType}>
                    <img src={activity.imageUrl}></img>
                  </li>
                )
              })}
            </ul>

            <ul className="directions">
              {arrows.map(arrow => {
                return (
                  <li
                  className={`arrow ${arrow.direction.toLowerCase()}`}
                  key={arrow.id}
                  data-entity-id={arrow.id}>
                    <span>{arrow.direction}</span>
                  </li>
                )
              })}
            </ul>
            {children}
        </div>
  )
}

interface LocationData {
  name: string
  imageUrl: string
  hasInventory: boolean
  arrows: Arrow[]
  activities: Activity[]
}

interface Arrow {
  direction: string
  id: number
}

interface Activity {
  actionType: string
  id?: number
  imageUrl: string
}

type LocationProps = Omit<LocationData, 'hasInventory'>

interface HasColorFilter {
  colorFilter: ColorFilter
}

export { Location, type LocationProps, type LocationData}
