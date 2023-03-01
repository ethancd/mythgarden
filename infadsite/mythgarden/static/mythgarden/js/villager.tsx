'use strict'

import React from 'react'

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Villager ({ name, portrait_url, affinity, description, id }: VillagerProps): JSX.Element {
  return (
    <li className="villager" key={id}>
      <div className="row">
        <div className="portrait">
          <img src={portrait_url}></img>
        </div>
        <div className="column">
          <span className="name">{name}</span>
          <span className="affinity">{affinity}</span>
        </div>
      </div>
      <span className="description">{description}</span>
    </li>
  )
}

interface VillagerProps {
  name: string
  portrait_url: string
  affinity: string
  description: string
  id: number
}

export { Villager, type VillagerProps }
