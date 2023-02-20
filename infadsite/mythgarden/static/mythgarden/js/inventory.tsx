'use strict';

import Item from './item';
import React from "react";

export default function Inventory({ items, orientation, id }) {
    return (
        <ul className={`${orientation}`} id={id}>
            {items.map(item => (Item(item)))}
        </ul>
    )
}