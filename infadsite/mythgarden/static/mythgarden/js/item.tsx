'use strict';

import React from "react";

export default function Item({ name, emoji, id, rarity, has_been_watered }) {
    return (
        <li
            className={`item ${rarity} ${has_been_watered && 'watered'}`}
            key={id}
        >
            <span className='type-emoji'>{emoji}</span>&nbsp;
            <span className='item-name'>{name}</span>
        </li>
    )
}