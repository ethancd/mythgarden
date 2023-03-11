'use strict'

import React from 'react'

export default function Hero ({ name, imageUrl, score, koinEarned, heartsEarned }: HeroProps): JSX.Element {
  return (
    <div id="hero">
      <div className="portrait">
        <img src={imageUrl}></img>
      </div>
      <div className="column">
        <div className="name">{name}</div>
        <div id="score"><span>{score}</span> <span>(⚜️{koinEarned} x {heartsEarned}❤️)</span></div>
      </div>
    </div>
  )
}

interface HeroProps {
  name: string
  imageUrl: string
  score: number
  koinEarned: number
  heartsEarned: number
}

export { Hero, type HeroProps }
