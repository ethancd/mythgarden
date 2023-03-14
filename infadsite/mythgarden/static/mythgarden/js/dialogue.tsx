'use strict'

import React, { useState, useContext } from 'react'
import colors from './_colors'
import { FilterizeColorContext } from "./lightColorLogic";

export default function Dialogue ({ name, imageUrl, fullText }: DialogueProps): JSX.Element {
  const [show, setShow] = useState(true)
  const filterizeColor = useContext(FilterizeColorContext)
  const backgroundColor = filterizeColor(colors.parchment)

  if (show) {
    return (
            <div id="dialogue" style={{ display: 'flex', backgroundColor }} onClick={() => { setShow(false) }}>
                <div className="speaker">
                  <div className="portrait">
                    <img src={imageUrl}></img>
                  </div>
                  <span className="name">{name}</span>
                </div>
                <span className="dialogue-text">{fullText}</span>
            </div>
    )
  } else {
    return (<div id="dialogue" style={{ display: 'none' }}></div>)
  }
}

interface DialogueProps {
  name: string
  imageUrl: string
  fullText: string
}

type DialogueData = DialogueProps & { id: number }

export { Dialogue, type DialogueProps, type DialogueData }
