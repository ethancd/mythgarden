'use strict'

import React from 'react'
import Color from 'color'
import { type ColorFilter } from './lightColorLogic'

const MAX_FILTER_OPACITY = 0.5;
// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Location ({ name, image_url, colorFilter, children }: React.PropsWithChildren<LocationProps & HasColorFilter>): JSX.Element {
  const backgroundColor = Color.rgb(colorFilter.rgbTemperature).darken(colorFilter.shadeBy).hex()
  const opacity = Math.min(colorFilter.shadeBy, MAX_FILTER_OPACITY)

  return (
        <div id='location'>
            <h2 className="name">{ name }</h2>
            <div className='landscape-filter' style={{
              backgroundColor,
              opacity,
            }}></div>
            <img className="landscape" src={image_url}></img>
            {children}
        </div>
  )
}

interface LocationProps {
  name: string
  image_url: string
}

interface HasColorFilter {
  colorFilter: ColorFilter
}

export { Location, type LocationProps }
