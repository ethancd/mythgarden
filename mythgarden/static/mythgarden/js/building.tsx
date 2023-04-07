'use strict'

import React from 'react'
import ActionPill, {ActionPillProps} from "./action";

export default function Building ({ name, id, imageUrl, coords, actionPill}: BuildingProps): JSX.Element {
  return (
        <li
          className={`building over-${coords.over} down-${coords.down}`}
          key={id}
          data-entity-id={id}>
          <img src={imageUrl}></img>
          <ActionPill {...actionPill}></ActionPill>
        </li>
  )
}

type BuildingProps = BuildingData & BuildingExtras;

interface BuildingData {
  name: string
  id: number
  imageUrl: string
  coords: {
    over: number
    down: number
  }
}

interface BuildingExtras {
  actionPill: ActionPillProps
}

export { Building, type BuildingData }
