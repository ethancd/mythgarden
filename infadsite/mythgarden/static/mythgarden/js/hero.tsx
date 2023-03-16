'use strict'

import React from 'react'

export default function Hero ({ name, imageUrl, score, highScore, koinEarned, heartsEarned }: HeroProps): JSX.Element {
  return (
    <div id="hero">
      <div className="portrait">
        <img src={imageUrl}></img>
      </div>
      <div className="column">
        <div className="name">{name}</div>
        <div id="score">
          <span>{score}</span> <span>(⚜️{koinEarned} x {heartsEarned}❤️)</span>
          {highScore > 0 ? <span id='high-score'> High Score: {highScore}</span> : null }
        </div>
      </div>
    </div>
  )
}

interface HeroData {
  name: string
  imageUrl: string
  score: number
  highScore: number
  koinEarned: number
  heartsEarned: number
  boostLevel: number
}

type HeroProps = Omit<HeroData, 'boostLevel'>

export { Hero, type HeroData }
