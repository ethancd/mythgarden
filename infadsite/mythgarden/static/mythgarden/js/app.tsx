import React, {SyntheticEvent} from 'react'
import { Action, type ActionProps } from './action'
import { ActionsList } from './actionsList'
import { type ActionClickData } from './actionStem'
import { Building, type BuildingProps } from './building'
import { Clock, type ClockData } from './clock'
import { Dialogue, type DialogueData} from './dialogue'
import EmptyItem from './emptyItem'
import { Hero, type HeroData } from './hero'
import { Item, type ItemProps } from './item'
import List from './list'
import {Location, type LocationData} from './location'
import { Message, type MessageProps } from './message'
import Section from './section'
import { Sun, Moon } from './sky'
import {Villager, VillagerData } from './villager'
import {VillagersList} from "./villagersList";
import Wallet from './wallet'

import { isDeepEqual } from './staticUtils'
import { FilterizeColorContext, filterFuncFactory, getColorFilterByTime } from './lightColorLogic'
import colors from './_colors'
import Gallery from "./gallery";

const MAX_ITEMS = 6

class App extends React.Component<Partial<AppProps>, AppState> {
  constructor (props: AppProps) {
    super(props)
    this.state = {
      combinedProps: props,
      activeGiftId: null,
      activeVillagerNames: [],
      showGallery: false,
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

  // might be nice to move this to a MessagesList component and just do it on render there
  scrollToMessageBottom (): void {
    const messageContainer = document.getElementById('message-log') as HTMLElement
    messageContainer.scrollTop = messageContainer.scrollHeight
  }

  // might be nice to move this to an ItemsList component
  mapItemsWithEmptySlots (items: ItemProps[]): JSX.Element[] {
    const paddedItems = items.concat(Array(MAX_ITEMS - items.length).fill(null))

    return paddedItems.map((item, n) => item != null ? Item(item) : EmptyItem({ slotNumber: n }))
  }

  getComponentTarget(e: React.SyntheticEvent<Element, Event>) {
    const componentClasses = ['action', 'action-stem', 'item', 'villager', 'hero-portrait', 'gallery']
    const componentClassSelector = componentClasses.map(c => '.' + c).join(', ')
    const componentDomNode = (e.target as HTMLElement).closest(componentClassSelector) as HTMLElement

    return componentDomNode
  }

  hasClass(element: HTMLElement, className: string) {
    return element.classList.contains(className);
  }

  marshalActionClickData(dataset: DOMStringMap): ActionClickData {
    const giftId = dataset.giftId == null ? null : parseInt(dataset.giftId)
    const villagerNames = dataset.villagerNames == null ? [] : dataset.villagerNames.split(',')

    return {
      giftId,
      villagerNames
    }
  }

  handleClick (e: SyntheticEvent): void {
    this.clearActiveUX()

    const target = this.getComponentTarget(e)
    if (target == null) return

    if (this.hasClass(target, 'action-stem')) {
      const actionClickData = this.marshalActionClickData(target.dataset)
      this.highlightTargetVillagers(actionClickData)
    }

    if (this.hasClass(target, 'hero-portrait')) {
      // click hero-portrait = toggle gallery open/closed
      if (!this.state.showGallery) {
        this.showGallery()
      }
    }
  }

  highlightTargetVillagers (actionClickData: ActionClickData): void {
    const {
      giftId,
      villagerNames
    } = actionClickData

    console.log('setting!')

    this.setState({ activeGiftId: giftId, activeVillagerNames: villagerNames })
  }

  showGallery (): void {
    this.setState({ showGallery: true })
  }

  clearActiveUX (): void {
    this.setState({ activeGiftId: null, activeVillagerNames: [], showGallery: false })
  }

  render (): JSX.Element {
    const {
      hero,
      portraitUrls,
      clock,
      wallet,
      inventory,
      actions,
      place,
      buildings,
      localItemTokens,
      messages,
      villagerStates,
      dialogue
    } = this.state.combinedProps

    const { activeGiftId, activeVillagerNames, showGallery } = this.state

    const colorFilter = getColorFilterByTime(clock.time)
    const filterFn = filterFuncFactory(colorFilter)

    return (
      <FilterizeColorContext.Provider value={ filterFn }>
        <Section id="page" baseColor={colors.whiteYellow} handleClick={this.handleClick.bind(this)}>

          <Section id="top-bar" baseColor={colors.skyBlue}>
            <Hero {...hero}></Hero>
            <Gallery {...{show: showGallery, currentPortraitUrl: hero.imageUrl, portraitUrls} }></Gallery>
            <h1 id="logo">Mythgarden</h1>
            <Clock display={clock.display} time={clock.time} boostLevel={hero.boostLevel}></Clock>
            <div id='sky-container'>
                <Sun time={clock.time}></Sun>
                <Moon time={clock.time} dayNumber={clock.dayNumber}></Moon>
            </div>
          </Section>

          <div id="main-area">
            <section id="sidebar">
              <List id='inventory' baseColor={colors.yellowLeather}>
                {(inventory != null) ? this.mapItemsWithEmptySlots(inventory) : null}
              </List>

              <Wallet value={wallet}></Wallet>
            </section>

            <ActionsList actions={actions} villagerCount={villagerStates.length}></ActionsList>

            <section id="center-col">
              <Location {...{...place, colorFilter}}>
                {/* might be nice to have a BuildingsList component so we can give individual buildings a filterable bg color */}
                <List id='buildings' baseColor={colors.lavenderPurpleTranslucent}>
                  {buildings?.map(building => Building(building))}
                </List>
              </Location>

              {place.hasInventory
                ? <List id='local-items' baseColor={colors.sandyBrown}>
                    {this.mapItemsWithEmptySlots(localItemTokens)}
                  </List>
                : null
              }

              <section id='footer'>
                <List id='message-log' baseColor={colors.parchment}>
                  {messages?.map(message => Message({ ...message }))}
                </List>
                {(dialogue != null ? <Dialogue {...dialogue} key={dialogue.id}></Dialogue> : null)}
              </section>
            </section>

            <VillagersList villagers={villagerStates}
                           activeGiftId={activeGiftId}
                           activeVillagerNames={activeVillagerNames}></VillagersList>
          </div>
        </Section>
      </FilterizeColorContext.Provider>
    )
  }
}

interface AppProps {
  actions: ActionProps[]
  buildings: BuildingProps[]
  clock: ClockData
  dialogue: DialogueData | null
  hero: HeroData
  inventory: ItemProps[]
  localItemTokens: ItemProps[]
  messages: MessageProps[]
  place: LocationData
  villagerStates: VillagerData[]
  wallet: string
  portraitUrls: string[]
}

interface AppState {
  combinedProps: AppProps
  activeGiftId: number|null
  activeVillagerNames: string[]
  showGallery: boolean
}

export { App, type AppProps }
