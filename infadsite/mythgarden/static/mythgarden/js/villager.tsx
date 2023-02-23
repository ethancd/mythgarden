'use strict'

import React from 'react'

export default function Villager ({ name, affinity, id }) {
  return (
        <li className="villager" key={id}>
            <span className="villager-name">{name}</span>
            <span className="affinity">{affinity}</span>
        </li>
  )
}
