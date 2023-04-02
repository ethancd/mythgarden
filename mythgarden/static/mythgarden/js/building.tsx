'use strict'

import React from 'react'

export default function Building ({ name, id }: BuildingProps): JSX.Element {
  return (
        <li className="building" key={id}>
            <div className='icon'>🏠</div>
            <span className="name">{name}</span>
        </li>
  )
}

interface BuildingProps {
  name: string
  id: number
}

export { Building, type BuildingProps }
