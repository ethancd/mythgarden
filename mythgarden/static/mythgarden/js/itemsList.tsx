import React from 'react'
import List from "./list";
import {Villager, type VillagerData} from "./villager";
import {ActionPillProps} from "./action";
import Item, {ItemData} from "./item";
import EmptyItem from "./emptyItem";

const MAX_ITEMS = 6

function ItemsList ({ items, id, baseColor, actionDictionary }: ItemsListProps): JSX.Element {
  const paddedItems = items.concat(Array(MAX_ITEMS - items.length).fill(null))

  return (
      <List id={id} baseColor={baseColor}>
        {paddedItems.map((item, n) => {
          if (item == null) {
            return (
              EmptyItem({ slotNumber: n })
            )
          }

          const actionPill = actionDictionary[`item-${item.id}`]
          return (
            Item({...item, actionPill})
          )
        })}
      </List>
  )
}

interface ItemsListProps {
  items: ItemData[]
  id: string
  baseColor: string
  actionDictionary: Record<string, ActionPillProps>
}

export { ItemsList }