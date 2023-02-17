'use strict';

import Item from './item';
import React from "react";

export default function Inventory({ items }) {
    return (
        <ul className="horizontal inventory">
            {items.map(item => (Item(item)))}
        </ul>
    )
}