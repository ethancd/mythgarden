'use strict'

import React, {SyntheticEvent, useEffect, useState} from 'react'
import { postUserData } from './ajax'

export default function Hero ({ name, isDefaultName, imageUrl, score, highScore, koinEarned, heartsEarned }: HeroProps): JSX.Element {
  const DEBOUNCE_DELAY_MS = 2000
  const [typedName, setTypedName] = useState(isDefaultName ? '' : name);

  useEffect(() => {
    const timeoutId = setTimeout(() => postUserData({name: typedName}), DEBOUNCE_DELAY_MS);
    return () => clearTimeout(timeoutId);
  }, [typedName]);

  const onKeyDown = (e: any) => {
    if (e.key === 'Enter' || e.key === 'Tab') {
      e.preventDefault();
      e.target.blur();
    }
  }

  return (
    <div id="hero">
      <div className="portrait">
        <img src={imageUrl}></img>
      </div>
      <div className="column">
        <div className="name">
          <textarea
            onKeyDown={onKeyDown}
            onChange={e => setTypedName(e.target.value)}
            value={typedName}
            maxLength={16}
            rows={1}
            placeholder={isDefaultName ? name : ''}></textarea>
        </div>
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
}

type HeroProps = Omit<HeroData, 'boostLevel'>

export { Hero, type HeroData }
