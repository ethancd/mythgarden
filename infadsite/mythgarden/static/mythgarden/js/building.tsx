'use strict'

import React from 'react'

export default function Building ({ name, id }) {
  return (
        <li className="building" key={id}>
            <span className="building">{name}</span>
        </li>
  )
}
