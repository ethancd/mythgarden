'use strict'

import React from 'react'

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Location ({ name, image_url, children }: React.PropsWithChildren<LocationProps>): JSX.Element {
  return (
        <>
            <div className="location">{ name }</div>
            <img className="landscape" src={image_url}></img>
            {children}
        </>
  )
}

interface LocationProps {
  name: string
  image_url: string
}

export { Location, type LocationProps }
