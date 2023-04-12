import React from 'react'

function AchievementsList ({ achievements }: AchievementsListProps): JSX.Element {
  // console.log(achievements)
  return (
      <ul id='achievements'>
        {achievements != null
          ? achievements.map(achievement => {
            return (
              <Achievement {...achievement} key={achievement.id}></Achievement>
            )
          })
          : null
        }
      </ul>
  )
}

function Achievement({name, description, emoji}: AchievementProps): JSX.Element {
  return (
      <li className='achievement'>
        <div className='icon'>{emoji}</div>
        <span className='name'>{name}</span>
        <span className='description'>{description}</span>
      </li>
  )
}

type AchievementProps = AchievementData;

interface AchievementData {
  name: string
  description: string
  emoji: string
  id: number
}

interface AchievementsListProps {
  achievements: AchievementData[]
}

export { AchievementsList, type AchievementData }