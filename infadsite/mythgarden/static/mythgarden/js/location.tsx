'use strict'

import React from 'react'
import Color from 'color'
import { type ColorFilter } from './lightColorLogic'

const MAX_FILTER_OPACITY = 0.5;
export default function Location ({ name, imageUrl, colorFilter, children }: React.PropsWithChildren<LocationProps & HasColorFilter>): JSX.Element {
  const backgroundColor = Color.rgb(colorFilter.rgbTemperature).darken(colorFilter.shadeBy).hex()
  const opacity = Math.min(colorFilter.shadeBy, MAX_FILTER_OPACITY)

  return (
        <div id='location'>
            <h2 className="name">{ name }</h2>
            <div className='landscape-filter' style={{
              backgroundColor,
              opacity,
            }}></div>
            <img className="landscape" src={imageUrl}></img>
            {children}
        </div>
  )
}

interface LocationProps {
  name: string
  imageUrl: string
}

interface HasColorFilter {
  colorFilter: ColorFilter
}

export { Location, type LocationProps }
