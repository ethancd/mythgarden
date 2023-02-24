'use strict'

import React from 'react'

export default function Wallet ({ value }: WalletProps): JSX.Element {
  return (
        <li className="wallet">{value}</li>
  )
}

interface WalletProps {
  value: string
}

export { Wallet, type WalletProps }
