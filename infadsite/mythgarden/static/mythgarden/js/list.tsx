'use strict'

import React from 'react'

export default function List ({ id, children }: React.PropsWithChildren<ListProps>): JSX.Element {
  return (
        <ul id={id}>
            {children}
        </ul>
  )
}

interface ListProps {
  id: string
}
