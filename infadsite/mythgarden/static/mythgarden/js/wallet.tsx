'use strict'

import React, { useContext } from 'react'
import { ColorModContext } from './app'
import colors from './_colors'
import Color from 'color'

export default function Wallet ({ value }: WalletProps): JSX.Element {
  const { darkenBy, desaturateBy } = useContext(ColorModContext)

  const baseColor = Color(colors.dollarBillGreen)
  const backgroundColor = baseColor.darken(darkenBy).desaturate(desaturateBy).hex()

  return (
        <div id="wallet" style={{ backgroundColor }}>{value}</div>
  )
}

interface WalletProps {
  value: string
}

export { Wallet, type WalletProps }
