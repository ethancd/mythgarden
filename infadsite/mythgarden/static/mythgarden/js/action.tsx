import React from 'react'
import { postAction } from './ajax'

import Dialogue from './dialogue'
// eslint-disable-next-line @typescript-eslint/no-unused-expressions
'use strict'
// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Action (this: any, { description, emoji, display_cost, unique_digest }: ActionProps): JSX.Element {
  const postThisAction = postAction.bind(this, description)

  return (
        <li
            onClick={() => { void postThisAction() }}
            className='action'
            key={unique_digest}
        >
            <span className='type-emoji'>{emoji}</span>&nbsp;
            <span className="description">{description}</span>
            <span className="cost">{display_cost}</span>
        </li>
  )
}

interface ActionProps {
  description: string
  emoji: string
  display_cost: string
  unique_digest: string
}

export { Action, type ActionProps }
