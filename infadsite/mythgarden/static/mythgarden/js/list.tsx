'use strict'

import React, { useContext } from 'react'
import Color from 'color'
import { ColorModContext } from './app'

export default function List ({ id, baseColor, children }: React.PropsWithChildren<ListProps>): JSX.Element {
  const { darkenBy, desaturateBy } = useContext(ColorModContext)

  const color = Color(baseColor)
  const backgroundColor = color.darken(darkenBy).desaturate(desaturateBy).hex()

  return (
        <ul id={id} style={{ backgroundColor }}>
            {children}
        </ul>
  )
}

interface ListProps {
  id: string
  baseColor: string
}
