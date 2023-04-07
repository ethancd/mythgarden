import React from "react";
import colors from './_colors';

enum WaitClass {
  Trivial = 'trivial',
  TrivialPlus = 'trivialPlus',
  SmallMinus = 'smallMinus',
  Small = 'small',
  SmallPlus = 'smallPlus',
  MediumMinus = 'mediumMinus',
  Medium = 'medium',
  MediumPlus = 'mediumPlus',
  LongMinus = 'longMinus',
  Long = 'long'
}

const WAIT_TO_COLOR = {
  [WaitClass.Trivial]: '#4d0',
  [WaitClass.TrivialPlus]: '#8d0',
  [WaitClass.SmallMinus]: '#ad0',
  [WaitClass.Small]: '#dd0',
  [WaitClass.SmallPlus]: '#db0',
  [WaitClass.MediumMinus]: '#da0',
  [WaitClass.Medium]: '#d80',
  [WaitClass.MediumPlus]: '#d60',
  [WaitClass.LongMinus]: '#d30',
  [WaitClass.Long]: '#d00'
}

export default function Duration ({ amount, waitClass }: DurationProps): JSX.Element {
  if (amount > 120) throw new Error('Unexpected action of greater than 2 hours')

  if (amount > 60) {
    return (
      <div className="cost duration">
        <DurationDial amount={60} waitClass={waitClass}></DurationDial>
        <DurationDial amount={amount - 60} waitClass={waitClass}></DurationDial>
      </div>
    )
  } else {
    return (
      <div className="cost duration">
          <DurationDial amount={amount} waitClass={waitClass}></DurationDial>
      </div>
    )
  }
}

function DurationDial ({ amount, waitClass }: DurationProps): JSX.Element {
  const degrees = amount * 6;
  const color = waitClass != null ? WAIT_TO_COLOR[waitClass] : colors.defaultGray;

  return (
    <div className={`dial`}
         style={{background: `conic-gradient(from 0deg, ${color} ${degrees}deg, #ccc 0)`}}>
      <span className="hour hand"></span>
      <span className="minute hand"
            style={{transform: `rotate(${180+degrees}deg)`}}
      ></span>
      <span className="center-arbor"></span>
    </div>
  )
}

interface DurationProps {
  amount: number
  waitClass?: WaitClass
}

export { Duration, WaitClass }