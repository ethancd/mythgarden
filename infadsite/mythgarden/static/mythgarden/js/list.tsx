'use strict'

import React from 'react'

export default function List ({ orientation, id, children }: React.PropsWithChildren<ListProps>): JSX.Element {
  return (
        <ul className={orientation} id={id}>
            {children}
        </ul>
  )
}

interface ListProps {
  orientation: string
  id: string
}
