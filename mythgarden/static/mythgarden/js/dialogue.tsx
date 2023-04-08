'use strict'

import React, { useState, useContext } from 'react'
import colors from './_colors'
import {FilterizeColorContext, ImageFilterContext} from "./lightColorLogic";
import Affinity, {AffinityProps} from "./affinity";

export default function Dialogue ({ name, imageUrl, fullText, affinity }: DialogueProps): JSX.Element {
  const [show, setShow] = useState(true)
  const filterizeColor = useContext(FilterizeColorContext)
  const backgroundColor = filterizeColor(colors.parchment)

  const imageFilterStyle = useContext(ImageFilterContext)

  if (show) {
    return (
      <div id="dialogue" style={{ display: 'flex', backgroundColor }} onClick={() => { setShow(false) }}>
          <div className="speaker">
            <div className="row">
              <div className="portrait">
                <img src={imageUrl}></img>
                <div className='portrait-filter' style={imageFilterStyle}></div>
              </div>
              <div className="column">
                { affinity != null
                  ? <Affinity {...affinity}></Affinity>
                  : null
                }
              </div>
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
  affinity?: AffinityProps
}

type DialogueData = Omit<DialogueProps, 'affinity'> & { id: number }

export { Dialogue, type DialogueProps, type DialogueData }
