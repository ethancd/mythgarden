'use strict'

import React, { useState } from 'react'

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Dialogue ({ name, portrait_url, full_text, shouldShow }: DialogueProps): JSX.Element {
  const [show, setShow] = useState(shouldShow)

  if (show) {
    return (
            <div id="dialogue" style={{ display: 'flex' }} onClick={() => { setShow(false) }}>
                <div className="speaker">
                  <div className="portrait">
                    <img src={portrait_url}></img>
                  </div>
                  <span className="name">{name}</span>
                </div>
                <span className="dialogue-text">{full_text}</span>
            </div>
    )
  } else {
    return (<div id="dialogue" style={{ display: 'none' }}></div>)
  }
}

interface DialogueProps {
  name: string
  portrait_url: string
  full_text: string
  shouldShow: boolean
}

export { Dialogue, type DialogueProps }
