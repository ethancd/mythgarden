import React from 'react'
import List from "./list";
import { Action, type ActionProps} from "./action";
import { ActionStem } from "./actionStem";
import colors from "./_colors";

function ActionsList ({ actions }: ActionsListProps): JSX.Element {
  function collapseActions(actions: ActionProps[]) {
    const newActionsList: ActionProps[] = []
    const actionStemMap: Record<string, string[]> = {}

    actions.forEach((action) => {
      if (action.targetCount <= 1) {
        newActionsList.push(action)
        return;
      }

      const descriptionSplit = action.description.split(' ')
      const targetName = descriptionSplit[descriptionSplit.length -1]
      const truncatedDescription = descriptionSplit.slice(0, -1).join(' ') + '...'
      const isInNewList = newActionsList.find(a => a.description === truncatedDescription)

      if (isInNewList == null) {
        actionStemMap[truncatedDescription] = [targetName]
        const newAction = {...action, description: truncatedDescription}
        newActionsList.push(newAction)
      } else {
        actionStemMap[truncatedDescription].push(targetName)
      }
    })


    return { newActionsList, actionStemMap }
  }

  const { newActionsList, actionStemMap } = collapseActions(actions)

  return (
          <List id='actions' baseColor={colors.blueMoonGray}>
            {newActionsList.map((action: ActionProps) => {
              if (actionStemMap[action.description] == null) {
                return Action(action)
              } else {
                return ActionStem({action, targets: actionStemMap[action.description]})
              }
            })}
          </List>
  )
}

interface ActionsListProps {
  actions: ActionProps[]
}

export { ActionsList }