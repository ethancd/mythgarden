'use strict';

import React from "react";

export default function Location({ name, image_url, children }) {
    return (
        <>
            <div className="location">{ name }</div>
            <img className="landscape" src={image_url}></img>
            {children}
        </>
    )
}