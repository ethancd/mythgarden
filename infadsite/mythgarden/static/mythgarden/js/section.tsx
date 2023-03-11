'use strict'

import React, { useContext } from 'react'
import Color from 'color'
import {FilterizeColorContext} from "./lightColorLogic";

export default function Section ({ id, baseColor, children }: React.PropsWithChildren<SectionProps>): JSX.Element {
  const filterizeColor = useContext(FilterizeColorContext)
  const backgroundColor = filterizeColor(baseColor)

  return (
        <section id={id}
                 className={ Color(backgroundColor).isDark() ? 'dark-mode' : ''}
                 style={{ backgroundColor }}>
            {children}
        </section>
  )
}

interface SectionProps {
  id: string
  baseColor: string
}
