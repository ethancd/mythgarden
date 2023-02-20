'use strict';

import React from "react";

function Villager({ name, affinity, id }) {
    return (
        <li className="villager" key={id}>
            <span className="villager-name">{name}</span>
            <span className="affinity">{affinity}</span>
        </li>
    )
}

export default function VillagersList({ villagers }) {
    return (
        <ul className="villagers vertical">
            {villagers.map(villager => Villager(villager))}
        </ul>
    )
}