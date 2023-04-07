import React from 'react'
import List from "./list";
import colors from "./_colors";
import {Villager, type VillagerData} from "./villager";
import {ActionPillProps} from "./action";

function VillagersList ({ villagers, actionDictionary }: VillagersListProps): JSX.Element {
  return (
      <List id='villagers' baseColor={colors.dustyPink}>
        {villagers?.map(villager => {
          const actionPill = actionDictionary[`villager-${villager.id}`]
          return Villager({ ...villager, actionPill })
        })}
      </List>
  )
}

interface VillagersListProps {
  villagers: VillagerData[]
  actionDictionary: Record<string, ActionPillProps>
}

export { VillagersList }