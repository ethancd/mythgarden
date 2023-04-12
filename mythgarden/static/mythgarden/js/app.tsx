import React, {SyntheticEvent} from 'react'
import { TouchBackend } from 'react-dnd-touch-backend'
import { DndProvider } from 'react-dnd'

import {type ActionData, ActionPillProps} from './action'
import {Building, type BuildingData} from './building'
import { Clock, type ClockData } from './clock'
import { Dialogue, type DialogueData} from './dialogue'
import { Hero, type HeroData } from './hero'
import { Item, type ItemData } from './item'
import List from './list'
import {Location, type LocationData} from './location'
import { Message, type MessageProps } from './message'
import Section from './section'
import { Sun, Moon } from './sky'
import {Villager, VillagerData } from './villager'
import {VillagersList} from "./villagersList";
import Wallet from './wallet'

import { isDeepEqual } from './staticUtils'
import { FilterizeColorContext, ImageFilterContext, filterFuncFactory, getImageFilter, getColorFilterByTime } from './lightColorLogic'
import colors from './_colors'
import Gallery from "./gallery";
import {postAction} from "./ajax";
import {ItemsList} from "./itemsList";
import {BuildingsList} from "./buildingsList";
import {ArrowsList} from "./arrowsList";
import {ActivitiesList} from "./activitiesList";
import {GiftPreview} from "./draggableGift";
import RainbowText from "./rainbowText";
import {AchievementData, AchievementsList} from "./achievementsList";

const TALK_ACTION = 'TALK'
const TRAVEL_ACTION = 'TRAVEL'

const WATER_ACTION = 'WATER'
const PLANT_ACTION = 'PLANT'
const HARVEST_ACTION = 'HARVEST'
const BUY_ACTION = 'BUY'
const SELL_ACTION = 'SELL'
const STOW_ACTION = 'STOW'
const RETRIEVE_ACTION = 'RETRIEVE'

const ITEM_ACTIONS = [WATER_ACTION, PLANT_ACTION, HARVEST_ACTION, BUY_ACTION, SELL_ACTION, STOW_ACTION, RETRIEVE_ACTION]

class App extends React.Component<Partial<AppProps>, AppState> {
  constructor (props: AppProps) {
    super(props)
    this.state = {
      combinedProps: props,
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

  marshalActionDictionary (actions: ActionData[]): ActionRecord {
    const actionDictionary = {} as ActionRecord

    actions.forEach(action => {
      const hasEntity = action.entityType != null && action.entityId != null
      const isGiftAction = action.giftReceiverId != null

      const key = hasEntity
        ? isGiftAction
          ? `gift-${action.entityId}`
          : `${action.entityType}-${action.entityId}`
        : 'no-entity'

      const {emoji, costAmount, costType, waitClass} = action

      actionDictionary[key] = {emoji, costAmount, costType, waitClass}
    })

    return actionDictionary;
  }

  marshalGiftReceiverIds (actions: ActionData[]): Set<number> {
    const giftReceiverIds = new Set<number>()

    actions.forEach(action => {
      if (action.giftReceiverId != null) {
        giftReceiverIds.add(action.giftReceiverId)
      }
    })

    return giftReceiverIds
  }

  getComponentTarget(e: React.SyntheticEvent) {
    const componentClasses = ['action', 'local-activity', 'item', 'villager', 'building', 'hero-portrait', 'gallery', 'arrow']
    const componentClassSelector = componentClasses.map(c => '.' + c).join(', ')
    const componentDomNode = (e.target as HTMLElement).closest(componentClassSelector) as HTMLElement

    return componentDomNode
  }

  hasClass(element: HTMLElement, className: string) {
    return element.classList.contains(className);
  }

  marshalActivityClickData(dataset: DOMStringMap) {
    const entityId = this.grabId(dataset) || ''
    const actionType = dataset.actionType == null ? null : dataset.actionType

    return {
      entityId,
      actionType
    }
  }

  grabId(dataset: DOMStringMap): number|null {
    const entityId = dataset.entityId == null ? null : parseInt(dataset.entityId)

    return entityId
  }

  findMatchingAction(actionType: string, entityId: number): ActionData | undefined {
    const matchingAction = this.state.combinedProps.actions.find(action => {
      return action.uniqueDigest === `${actionType}-${entityId}`
    })

    return matchingAction
  }

  fireActionIfAvailable(actionType: string, target: HTMLElement) {
    const entityId = this.grabId(target.dataset)
    if (entityId == null) return

    const matchingAction = this.findMatchingAction(actionType, entityId)
    if (matchingAction == null) return

    void postAction(matchingAction.uniqueDigest)
  }

  fireActionWithEmptyIdIfAvailable(actionType: string) {
    const matchingAction = this.state.combinedProps.actions.find(action => {
      return action.uniqueDigest === `${actionType}-`  // load-bearing hyphen at the end there
    })
    if (matchingAction == null) return

    void postAction(matchingAction.uniqueDigest)
  }

  handleClick (e: SyntheticEvent): void {
    this.clearActiveUX()

    const target = this.getComponentTarget(e)
    if (target == null) return

    if (this.hasClass(target, 'hero-portrait')) {
      // click hero-portrait = toggle gallery open/closed
      if (!this.state.showGallery) {
        this.showGallery()
      }
    }

    if (this.hasClass(target, 'villager')) {
      this.fireActionIfAvailable(TALK_ACTION, target)
    }

    if (this.hasClass(target, 'building')) {
      this.fireActionIfAvailable(TRAVEL_ACTION, target)
    }

    if (this.hasClass(target, 'arrow')) {
      this.fireActionIfAvailable(TRAVEL_ACTION, target)
    }

    if (this.hasClass(target, 'local-activity')) {
      const { actionType, entityId} = this.marshalActivityClickData(target.dataset)

      if (actionType == null || entityId == null) return

      if (entityId == '') {  // expect these location activities to often have no entity id
        this.fireActionWithEmptyIdIfAvailable(actionType)
      } else {
        this.fireActionIfAvailable(actionType, target)
      }
    }

    if (this.hasClass(target, 'item')) {
      // relying on assumption that any item has only ONE action available at a time (excluding gift actions)
      ITEM_ACTIONS.forEach(actionType => {
        this.fireActionIfAvailable(actionType, target)
      })
    }
  }

  showGallery (): void {
    this.setState({ showGallery: true })
  }

  clearActiveUX (): void {
    this.setState({ showGallery: false })
  }

  render (): JSX.Element {
    const {
      achievements,
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
      dialogue,
      speaker
    } = this.state.combinedProps

    const { showGallery } = this.state

    const colorFilter = getColorFilterByTime(clock.time)
    const imageFilter = getImageFilter(colorFilter)
    const filterFn = filterFuncFactory(colorFilter)

    const actionDictionary = this.marshalActionDictionary(actions)
    const giftReceiverIds = this.marshalGiftReceiverIds(actions)

    return (
      <FilterizeColorContext.Provider value={ filterFn }>
        <ImageFilterContext.Provider value={imageFilter}>
        <DndProvider backend={TouchBackend} options={{enableMouseEvents: true}}>
        <Section id="page" baseColor={colors.whiteYellow} handleClick={this.handleClick.bind(this)}>

          <Section id="top-bar" baseColor={colors.skyBlue}>
            <Hero {...hero}></Hero>
            <Gallery {...{show: showGallery, currentPortraitUrl: hero.imageUrl, portraitUrls} }></Gallery>
            <AchievementsList achievements={achievements}></AchievementsList>
            <h1 id="logo"><RainbowText text={'Mythgarden'}></RainbowText></h1>
            <Clock display={clock.display} time={clock.time} boostLevel={hero.boostLevel} luckPercent={hero.luckPercent}></Clock>
            <div id='sky-container'>
                <Sun time={clock.time}></Sun>
                <Moon time={clock.time} dayNumber={clock.dayNumber}></Moon>
            </div>
          </Section>

          <div id="main-area">
            <section id="sidebar">
              <ItemsList
                id='inventory'
                baseColor={colors.yellowLeather}
                items={inventory}
                actionDictionary={actionDictionary}
                giftable={true}
              ></ItemsList>
              <GiftPreview></GiftPreview>
              <Wallet value={wallet}></Wallet>
            </section>

            <section id="center-col">
              <Location {...{...place, colorFilter, actionDictionary}}>
                <ActivitiesList activities={place.activities}
                                actionDictionary={actionDictionary}
                ></ActivitiesList>

                <ArrowsList arrows={place.arrows}
                actionDictionary={actionDictionary}
                ></ArrowsList>

                <BuildingsList
                  buildings={buildings}
                  actionDictionary={actionDictionary}
                ></BuildingsList>
              </Location>

              {place.hasInventory
                ? <ItemsList
                  id='local-items'
                  baseColor={colors.sandyBrown}
                  items={localItemTokens}
                  actionDictionary={actionDictionary}
                  giftable={false}
                ></ItemsList>
                : null
              }

              <section id='footer'>
                <List id='message-log' baseColor={colors.parchment}>
                  {messages?.map(message => Message({ ...message }))}
                </List>
              </section>
            </section>
            <section id='far-sidebar'>
              <VillagersList villagers={villagerStates}
                           actionDictionary={actionDictionary}
                           giftReceiverIds={giftReceiverIds}
              ></VillagersList>
              {(dialogue != null ? <Dialogue {...dialogue} affinity={speaker?.affinity} key={dialogue.id}></Dialogue> : null)}
            </section>
          </div>
        </Section>
          </DndProvider>
          </ImageFilterContext.Provider>
      </FilterizeColorContext.Provider>
    )
  }
}

type ActionRecord = Record<string, ActionPillProps>

interface AppProps {
  achievements: AchievementData[]
  actions: ActionData[]
  buildings: BuildingData[]
  clock: ClockData
  dialogue: DialogueData | null
  hero: HeroData
  inventory: ItemData[]
  localItemTokens: ItemData[]
  messages: MessageProps[]
  place: LocationData
  villagerStates: VillagerData[]
  wallet: string
  portraitUrls: string[]
  speaker: VillagerData | null
}

interface AppState {
  combinedProps: AppProps
  showGallery: boolean
}

export { App, type AppProps }
