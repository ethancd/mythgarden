'use strict'

import React from 'react'

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Location ({ name, image_url, children }: React.PropsWithChildren<LocationProps>): JSX.Element {
  return (
        <div id='location'>
            <h2 className="name">{ name }</h2>
            <img className="landscape" src={image_url}></img>
            {children}
        </div>
  )
}

interface LocationProps {
  name: string
  image_url: string
}

export { Location, type LocationProps }
