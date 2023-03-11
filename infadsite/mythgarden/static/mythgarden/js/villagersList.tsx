import React from 'react'
import List from "./list";
import colors from "./_colors";
import {Villager, type VillagerData} from "./villager";

function VillagersList ({ villagers, activeGiftId, activeVillagerNames }: VillagersListProps): JSX.Element {
  return (
      <List id='villagers' baseColor={colors.dustyPink}>
        {villagers?.map(villager => {
          const villagerProps = { ...villager, activeGiftId }
          const villagerIsActive = activeVillagerNames.find((name) => name === villager.name)

          if (villagerIsActive == null) {
            villagerProps.activeGiftId = null
          }
          return Villager(villagerProps)
        })}
      </List>
  )
}

interface VillagersListProps {
  villagers: VillagerData[]
  activeGiftId: number | null
  activeVillagerNames: string[]
}

export { VillagersList }