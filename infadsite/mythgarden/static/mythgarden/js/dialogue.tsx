'use strict'

import React, { useState } from 'react'

export default function Dialogue ({ name, portrait_url, full_text, shouldShow }) {
  const [show, setShow] = useState(shouldShow)

  if (show) {
    return (
            <div className="dialogue" style={{ display: 'flex' }} onClick={() => { setShow(false) }}>
                <div className="speaker">
                    <img className="speaker-portrait" src={portrait_url}></img>
                    <span className="speaker-name">{name}</span>
                </div>
                <span className="dialogue-text">{full_text}</span>
            </div>
    )
  } else {
    return (<div className="dialogue" style={{ display: 'none' }}></div>)
  }
}
