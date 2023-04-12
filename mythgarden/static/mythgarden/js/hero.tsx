'use strict'

import React, {useContext} from 'react'
import TypeableName from "./typeableName";
import {ImageFilterContext} from "./lightColorLogic";
import RainbowText from "./rainbowText";
import {AchievementData} from "./achievementsList";

export default function Hero ({ name, isDefaultName, imageUrl, score, highScore, luckPercent, koinEarned, heartsEarned }: HeroProps): JSX.Element {
  const { backgroundColor, opacity } = useContext(ImageFilterContext)

  return (
    <div id="hero">
      <div className="portrait hero-portrait">
        <img src={imageUrl}></img>
        <div className='portrait-filter' style={{ backgroundColor, opacity }}></div>
      </div>
      <div className="column">
        <TypeableName {...{ name, isDefaultName }}></TypeableName>
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
  isDefaultName: boolean
  imageUrl: string
  score: number
  highScore: number
  koinEarned: number
  heartsEarned: number
  boostLevel: number
  luckPercent: string
}

type HeroProps = Omit<HeroData, 'boostLevel'>

export { Hero, type HeroData, type HeroProps }
