'use strict';

import React from "react";

export default function List({ orientation, id, children }) {
    return (
        <ul className={orientation} id={id}>
            {children}
        </ul>
    )
}