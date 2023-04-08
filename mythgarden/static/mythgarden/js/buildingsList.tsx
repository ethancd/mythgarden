import React from 'react'
import List from "./list";
import {ActionPillProps} from "./action";
import colors from "./_colors";
import Building, {type BuildingData} from "./building";

function BuildingsList ({ buildings, actionDictionary }: BuildingsListProps): JSX.Element {
  return (
      <List id='buildings' baseColor={colors.lavenderPurpleTranslucent}>
        {buildings.map(building => {
          const actionPill = actionDictionary[`place-${building.id}`]
          return (
            <Building {...{...building, actionPill}} key={building.id}></Building>
          )
        })}
      </List>
  )
}

interface BuildingsListProps {
  buildings: BuildingData[]
  actionDictionary: Record<string, ActionPillProps>
}

export { BuildingsList }