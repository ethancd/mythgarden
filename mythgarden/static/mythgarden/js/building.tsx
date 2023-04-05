'use strict'

import React from 'react'

export default function Building ({ name, id, imageUrl, coords }: BuildingProps): JSX.Element {
  console.log(imageUrl)
  return (
        <li
          className={`building over-${coords.over} down-${coords.down}`}
          key={id}
          data-entity-id={id}>
          <img src={imageUrl}></img>
        </li>
  )
}

interface BuildingProps {
  name: string
  id: number
  imageUrl: string
  coords: {
    over: number
    down: number
  }
}

export { Building, type BuildingProps }
