import React from 'react'
import RainbowText from "./rainbowText";

function AchievementsList ({ achievements, totalAchievements, show }: AchievementsListProps): JSX.Element {
  if (show) {
    const earnedCount = achievements.filter(a => a.isEarned).length
    return (
        <ul id='achievements'>
          <li><h2>Achievements {`(${earnedCount} / ${totalAchievements})`}</h2></li>
          {achievements.map((achievement) => {
            return achievement.isEarned
            ? <Achievement {...achievement} key={achievement.id}></Achievement>
            : <UnclaimedAchievement {...achievement} key={achievement.id}></UnclaimedAchievement>
          })
          }
        </ul>
    )
  } else {
    return (
     <ul id="achievements" style={{ display: 'none' }}></ul>
    )
  }
}

function Achievement({name, description, emoji, unlockedKnowledge}: AchievementProps): JSX.Element {
  return (
      <li className='achievement'>
        <div className='row'>
          <div className='icon'>{emoji}</div>
          <div className='column'>
            <span className='title'>{name}</span>
            <span className='description'>{description}</span>
          </div>
        </div>
        { unlockedKnowledge != null
          ? <div className='column knowledge'>
              <span className='title'>
                <RainbowText text={'knowledge granted:'} shading={0.2}></RainbowText>
              </span>
            {unlockedKnowledge.map((knowledge) => {
              return <span className='knowledge-description'>{knowledge}</span>
            })}
            </div>
          : null
        }
      </li>
  )
}

function UnclaimedAchievement ({name, description, progress}: AchievementProps): JSX.Element {
  return (
    <li className="achievement unclaimed">
      <div className='row'>
        <div className="icon">❓</div>
        <div className='column'>
          <span className="title">{name}</span>
          <span className="description">{description}</span>
          {progress && (
            <div className="progress-container">
              <div
                className="progress-bar"
                style={{ width: `${progress.percent * 100}%` }}
              />
              <span className="progress-label">{progress.label}</span>
            </div>
          )}
        </div>
      </div>
    </li>
  )
}

type AchievementProps = AchievementData

interface AchievementProgress {
  current: number
  target: number
  label: string
  percent: number
}

interface AchievementData {
  name: string
  description: string
  id: number
  isEarned: boolean
  emoji?: string
  unlockedKnowledge?: string[]
  progress?: AchievementProgress
}

interface AchievementsListProps {
  achievements: AchievementData[]
  show: boolean
  totalAchievements: number
}

export { AchievementsList, type AchievementData }