'use strict'

import React, { useContext } from 'react'
import colors from './_colors'
import {FilterizeColorContext} from "./lightColorLogic";

export default function Wallet ({ value }: WalletProps): JSX.Element {
  const filterizeColor = useContext(FilterizeColorContext)
  const backgroundColor = filterizeColor(colors.whiteYellow)

  return (
        <div id="wallet" style={{
          backgroundColor,
          backgroundImage: `url("/static/mythgarden/images/leather-texture.png")`
        }}><span>{value}</span></div>
  )
}

interface WalletProps {
  value: string
}

export { Wallet, type WalletProps }
