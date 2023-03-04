'use strict'

import React from 'react'

// eslint-disable-next-line @typescript-eslint/naming-convention
export default function Hero ({ name, image_url, score, koin_earned, hearts_earned }: HeroProps): JSX.Element {
  return (
    <div id="hero">
      <div className="portrait">
        <img src={image_url}></img>
      </div>
      <div className="column">
        <div className="name">{name}</div>
        <div id="score"><span>{score}</span> <span>(⚜️{koin_earned} x {hearts_earned}❤️)</span></div>
      </div>
    </div>
  )
}

interface HeroProps {
  name: string
  image_url: string
  score: number
  koin_earned: number
  hearts_earned: number
}

export { Hero, type HeroProps }
