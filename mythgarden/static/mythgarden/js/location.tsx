'use strict'

import React, {useContext} from 'react'
import {ImageFilterContext} from './lightColorLogic'
import {ActivityData} from "./activitiesList";
import {ArrowData} from "./arrowsList";
import RainbowText from "./rainbowText";
import ToastContainer from "./toastContainer";
import HistoryButton from "./historyButton";
import {type MessageProps} from "./message";

export default function Location ({ name, imageUrl, messages, onShowHistory, children }: React.PropsWithChildren<LocationProps>): JSX.Element {
  const { backgroundColor, opacity } = useContext(ImageFilterContext)

  return (
        <div id='location'>
            {/*<h2 className="name">{name}</h2>*/}
            <h2 className="name"><RainbowText text={name} shading={0.5}></RainbowText></h2>
            <div className='landscape-filter' style={{
              backgroundColor,
              opacity,
            }}></div>
            <div className='darkness-filter'></div>
            <img className="landscape" src={imageUrl}></img>

            {/* Toast notifications overlay */}
            <ToastContainer messages={messages} />

            {/* History button */}
            <HistoryButton onClick={onShowHistory} />

            {children}
        </div>
  )
}

interface LocationData {
  name: string
  imageUrl: string
  hasInventory: boolean
  activities: ActivityData[]
  arrows: ArrowData[]
}

type LocationProps = Omit<LocationData, 'hasInventory'> & {
  messages: MessageProps[]
  onShowHistory: () => void
}

export { Location, type LocationProps, type LocationData }
