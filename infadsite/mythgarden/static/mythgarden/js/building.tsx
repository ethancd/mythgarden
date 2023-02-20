'use strict';

import React from "react";

function Building({ name, id }) {
    return (
        <li className="building" key={id}>
            <span className="building">{name}</span>
        </li>
    )
}

export default function BuildingsList({ buildings }) {
    return (
        <ul className="buildings vertical">
            {buildings.map(buildings => Building(buildings))}
        </ul>
    )
}