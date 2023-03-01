'use strict'

import React from 'react'

export default function Wallet ({ value }: WalletProps): JSX.Element {
  return (
        <div className="wallet">{value}</div>
  )
}

interface WalletProps {
  value: string
}

export { Wallet, type WalletProps }
