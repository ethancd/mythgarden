'use strict'

import React, { useContext } from 'react'
import { PostAction } from './PostActionContext'

export default function Action ({ description, emoji, display_cost, unique_digest }) {
  const postAction = useContext(PostAction).bind(this, description)

  return (
        <li
            onClick={postAction}
            className='action'
            key={unique_digest}
        >
            <span className='type-emoji'>{emoji}</span>&nbsp;
            <span className="description">{description}</span>
            <span className="cost">{display_cost}</span>
        </li>
  )
}
