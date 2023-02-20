'use strict';

import React from "react";
import { useContext } from 'react';
import { PostAction } from './PostActionContext';

export default function Action({ description, emoji, display_cost }) {
    const postAction = useContext(PostAction).bind(this, description);

    return (
        <li
            onClick={postAction}
            className='action'
        >
            <span className='type-emoji'>{emoji}</span>&nbsp;
            <span className="description">{description}</span>
            <span className="cost">{display_cost}</span>
        </li>
    )
}