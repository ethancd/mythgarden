import React from 'react'
import List from './list'
import Hero from './hero'
import Clock from './clock'
import Wallet from './wallet'
import Item from './item'
import { Action, type ActionProps } from './action'
import Location from './location'
import Building from './building'
import Villager from './villager'
import Dialogue from './dialogue'
// import Log from "./log";

import { isDeepEqual } from './staticUtils'

class App extends React.Component<AppProps, AppState> {
  constructor (props: AppProps) {
    super(props)
    this.state = {
      combinedProps: props
    }
  }

  componentDidUpdate (prevProps: Readonly<AppProps>, prevState: Readonly<AppState>): void {
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
      // eslint-disable-next-line @typescript-eslint/naming-convention
      villager_states,
      dialogue
    } = this.state.combinedProps

    console.log('rendering app')
    console.log(clock)
    return (
            <div className="page">
                <section className="top-bar">
                <div className="horizontal game-info">
                    <Hero {...hero}></Hero>
                    <li className="stats">
                        <ul className="vertical stats">
                            <Clock value={clock}></Clock>
                            <Wallet value={wallet}></Wallet>
                        </ul>
                    </li>
                </div>
                </section>

                <section className="main-area">
                    <section className="sidebar left">
                        <List orientation='vertical' id='inventory'>
                            {inventory?.map(item => Item(item))}
                        </List>
                        <List orientation='vertical' id='actions'>
                            {actions?.map(action => Action(action))}
                        </List>
                    </section>

                    <section className="canvas">
                        <Location {...place}>
                            <List orientation='horizontal' id='buildings'>
                                {buildings?.map(building => Building(building))}
                            </List>
                            <List orientation='horizontal' id='local-items'>
                                {local_item_tokens?.map(item => Item(item))}
                            </List>
                        </Location>
                    </section>

                    <section className='sidebar right'>
                        <List orientation='vertical' id='villagers'>
                            {villager_states?.map(villager => Villager(villager))}
                        </List>
                    </section>
                </section>
                <section className='footer'>
                    {/* <Log></Log> */}
                    { dialogue?.id != null &&
                        <Dialogue {...dialogue} key={dialogue.id} shouldShow={true}></Dialogue>
                    }
                </section>
            </div>
    )
  }
}

interface AppProps {
  actions?: ActionProps[]
  buildings?: BuildingProps[]
  clock?: ClockProps
  dialogue?: DialogueProps
  hero?: HeroProps
  inventory?: ItemProps[]
  local_item_tokens?: ItemProps[]
  place?: LocationProps
  villager_states?: VillagerProps[]
  wallet?: WalletProps
}

interface AppState {
  combinedProps: AppProps
}

export { App, type AppProps }
