'use strict'

import React, { useContext } from 'react'
import Color from 'color'
import { ColorModContext } from './app'

export default function Section ({ id, baseColor, children }: React.PropsWithChildren<SectionProps>): JSX.Element {
  const { darkenBy, desaturateBy } = useContext(ColorModContext)

  const color = Color(baseColor)
  const backgroundColorObj = color.darken(darkenBy).desaturate(desaturateBy)
  const backgroundColor = backgroundColorObj.hex()

  return (
        <section id={id} className={ backgroundColorObj.isDark() ? 'dark-mode' : ''} style={{ backgroundColor }}>
            {children}
        </section>
  )
}

interface SectionProps {
  id: string
  baseColor: string
}
