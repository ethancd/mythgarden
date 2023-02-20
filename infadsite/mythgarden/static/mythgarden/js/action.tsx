'use strict';

import React from "react";
import { useContext } from 'react';
import { PostAction } from './PostActionContext';

function Action({ description, emoji, display_cost, updatePage, passErrorToUser }) {
    return (
        <li
            onClick={useContext(PostAction).bind(this, description)}
            className='action'
        >
            <span className='type-emoji'>{emoji}</span>&nbsp;
            <span className="description">{description}</span>
            <span className="cost">{display_cost}</span>
        </li>
    )
}

export default function ActionsList({ actions, updatePage, passErrorToUser }) {
    return (
        <ul className="vertical actions">
            {actions.map(action => {
                return Action({...action, updatePage, passErrorToUser})
            })}
        </ul>
    )
}