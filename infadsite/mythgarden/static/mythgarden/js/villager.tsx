'use strict'

import React from 'react'

export default function Villager ({ name, affinity, id }: VillagerProps): JSX.Element {
  return (
        <li className="villager" key={id}>
            <span className="villager-name">{name}</span>
            <span className="affinity">{affinity}</span>
        </li>
  )
}

interface VillagerProps {
  name: string
  affinity: string
  id: number
}

export { Villager, type VillagerProps }
