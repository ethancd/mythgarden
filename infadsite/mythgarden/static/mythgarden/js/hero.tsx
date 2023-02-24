'use strict'

import React from 'react'

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Hero ({ name, portrait_url, score, koin_earned, hearts_earned }: HeroProps): JSX.Element {
  return (
        <li className="player-info">
            <div className="player-avatar">
                <img src={ portrait_url }></img>
            </div>
            <div>
                <div className="player-name">{name}</div>
                <div className="score-cont">
                    <span className="score">{score} (⚜️{koin_earned} x {hearts_earned}❤️)</span>
                </div>
            </div>
        </li>
  )
}

interface HeroProps {
  name: string
  portrait_url: string
  score: number
  koin_earned: number
  hearts_earned: number
}

export { Hero, type HeroProps }
