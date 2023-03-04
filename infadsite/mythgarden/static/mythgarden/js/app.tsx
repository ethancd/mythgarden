import React from 'react'
import { Action, type ActionProps } from './action'
import { Building, type BuildingProps } from './building'
import Clock from './clock'
import { Dialogue, type DialogueProps } from './dialogue'
import EmptyItem from './emptyItem'
import { Hero, type HeroProps } from './hero'
import { Item, type ItemProps } from './item'
import List from './list'
import { Location, type LocationProps } from './location'
import { Message, type MessageProps } from './message'
import { Villager, type VillagerProps } from './villager'
import Wallet from './wallet'

import { isDeepEqual } from './staticUtils'

const MAX_ITEMS = 6

class App extends React.Component<Partial<AppProps>, AppState> {
  constructor (props: AppProps) {
    super(props)
    this.state = {
      combinedProps: props
    }
  }

  componentDidUpdate (prevProps: Readonly<Partial<AppProps>>, prevState: Readonly<AppState>): void {
    /*
     * Expect the server to only return models that have been updated on the most recent request.
     * Therefore, combine the previous props with new props for the next render, so existing data keeps being displayed.
     * Do set dialogue: null if dialogue isn't in the new props, so that the dialogue box disappears after one action.
     */
    const combinedProps = { ...this.state.combinedProps, dialogue: null, ...this.props }

    if (!isDeepEqual(combinedProps, this.state.combinedProps)) {
      this.setState({ combinedProps })
    }

    this.scrollToMessageBottom()
  }

  componentDidMount (): void {
    this.scrollToMessageBottom()
  }

  scrollToMessageBottom (): void {
    const messageContainer = document.getElementById('message-log') as HTMLElement
    messageContainer.scrollTop = messageContainer.scrollHeight
  }

  mapItemsWithEmptySlots (items: ItemProps[]): JSX.Element[] {
    const paddedItems = items.concat(Array(MAX_ITEMS - items.length).fill(null))

    return paddedItems.map((item, n) => item != null ? Item(item) : EmptyItem({ slotNumber: n }))
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
              {(inventory != null) ? this.mapItemsWithEmptySlots(inventory) : null}
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
              {(local_item_tokens?.length > 0) ? this.mapItemsWithEmptySlots(local_item_tokens) : null}
            </List>
            <section id='footer'>
              <List id='message-log'>
                {messages?.map(message => Message(message))}
              </List>
              {(dialogue != null ? <Dialogue {...dialogue}></Dialogue> : null)}
            </section>
          </section>

          <List id='villagers'>
            {villager_states?.map(villager => Villager(villager))}
          </List>
        </section>
      </div>
    )
  }
}

interface AppProps {
  actions: ActionProps[]
  buildings: BuildingProps[]
  clock: string
  dialogue: DialogueProps | null
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
