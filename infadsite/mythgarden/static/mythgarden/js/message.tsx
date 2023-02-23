'use strict'

import React, { useState } from 'react'

export default function Message ({ value, shouldShow }) {
  console.log(shouldShow)
  const [show, setShow] = useState(shouldShow)

  console.log(show)

  console.log(value.length)
  if (show) {
    return (
            <p className="message" style={{ display: 'block' }} onClick={() => { setShow(false) }}>
                {value}
            </p>
    )
  } else {
    return (<p className="message" style={{ display: 'none' }}></p>)
  }
}
