'use strict'

import React from 'react'

export default function Building ({ name, id }: BuildingProps): JSX.Element {
  return (
        <li className="building" key={id}>
            <span className="building">{name}</span>
        </li>
  )
}

interface BuildingProps {
  name: string
  id: number
}

export { Building, type BuildingProps }
