'use strict'

import React from 'react'
import {Affinity, AffinityProps} from "./affinity";
import ActionPill, {ActionPillProps} from "./action";

export default function Villager ({ name, imageUrl, affinity, description, id, actionPill }: VillagerProps): JSX.Element {

  return (
    <li
      className={`villager`}
      key={id}
      data-entity-id={id}>
      <div className="row">
        <div className="portrait">
          <img src={imageUrl}></img>
          { actionPill != null
            ? <ActionPill {...actionPill}></ActionPill>
            : null
          }
        </div>
        <div className="column">
          <Affinity {...affinity}></Affinity>
        </div>
      </div>
      <span className="name">{name}</span>
      <span className="description">{description}</span>
    </li>
  )
}

type VillagerProps = VillagerData & VillagerExtras

interface VillagerData {
  name: string
  imageUrl: string
  description: string
  id: number
  affinity: AffinityProps
}

interface VillagerExtras {
  actionPill: ActionPillProps
}

export { Villager, type VillagerProps, type VillagerData }
