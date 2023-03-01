import React from 'react'
import { Action, type ActionProps } from './action'
import { Building, type BuildingProps } from './building'
import Clock from './clock'
import { Dialogue, type DialogueProps } from './dialogue'
import { Hero, type HeroProps } from './hero'
import { Item, type ItemProps } from './item'
import List from './list'
import { Location, type LocationProps } from './location'
import { Message, type MessageProps } from './message'
import { Villager, type VillagerProps } from './villager'
import Wallet from './wallet'
// import Log from "./log";

import { isDeepEqual } from './staticUtils'

class App extends React.Component<Partial<AppProps>, AppState> {
  constructor (props: AppProps) {
    super(props)
    this.state = {
      combinedProps: props
    }
  }

  componentDidUpdate (prevProps: Readonly<Partial<AppProps>>, prevState: Readonly<AppState>): void {
    const combinedProps = { ...this.state.combinedProps, ...this.props }

    if (!isDeepEqual(combinedProps, this.state.combinedProps)) {
      this.setState({ combinedProps })
    }
  }

  render (): JSX.Element {
    const {
      hero,
      clock,
      wallet,
      inventory,
      actions,
      place,
      buildings,
      // eslint-disable-next-line @typescript-eslint/naming-convention
      local_item_tokens,
      messages,
      // eslint-disable-next-line @typescript-eslint/naming-convention
      villager_states,
      dialogue
    } = this.state.combinedProps

    console.log('rendering app')

    return (
      <div id="page">
        <section id="top-bar">
          <Hero {...hero}></Hero>
          <h1 id="logo">Mythgarden</h1>
          <Clock value={clock}></Clock>
        </section>

        <section id="main-area">
          <section id="sidebar">
            <List id='inventory'>
              {inventory?.map(item => Item(item))}
            </List>
            <Wallet value={wallet}></Wallet>
          </section>
          <List id='actions'>
            {actions?.map(action => Action(action))}
          </List>

          <section id="center-col">
            <Location {...place}>
              <List id='buildings'>
                {buildings?.map(building => Building(building))}
              </List>
            </Location>
            <List id='local-items'>
              {local_item_tokens?.map(item => Item(item))}
            </List>
            <section id='footer'>
              <List id='message-log'>
                {messages?.map(message => Message(message))}
              </List>
              {dialogue?.id != null &&
                <Dialogue {...dialogue} key={dialogue.id} shouldShow={true}></Dialogue>
              }
            </section>
          </section>

        </section>
        <List id='villagers'>
          {villager_states?.map(villager => Villager(villager))}
        </List>
      </div>
    )
  }
}

interface AppProps {
  actions: ActionProps[]
  buildings: BuildingProps[]
  clock: string
  dialogue: DialogueProps & { id?: number }
  hero: HeroProps
  inventory: ItemProps[]
  local_item_tokens: ItemProps[]
  messages: MessageProps[]
  place: LocationProps
  villager_states: VillagerProps[]
  wallet: string
}

interface AppState {
  combinedProps: AppProps
}

export { App, type AppProps }
