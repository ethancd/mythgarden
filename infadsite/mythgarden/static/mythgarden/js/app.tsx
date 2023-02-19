
<!--
expected models:
    hero:
        name
        portrait:
            url
        score
        koin_earned
        hearts_earned
    clock:
        display
    wallet
        display
    place:
        name
        image:
            url
    inventory[]:
        name
        rarity
    actions[]:
        description
        display_cost
    buildings[]:
        name
    villager_states[]:
        affinity
        villager
            name
    local_item_tokens[]:
        name
        has_been_watered
        rarity
    message: string
-->

import React from "react";
import Inventory from "./inventory";

export default class App extends React.Component<any, any> {
    render() {
        return (
            <div class="page">
                <section className="top-bar">
                <div className={"horizontal game-info"}>
                    <Player className='player-info'>
                        <Avatar></Avatar>
                        <div className="player-name"></div>
                        <Score></Score>
                    </Player>
                    <Clock></Clock>
                    <Wallet></Wallet>
                </div>

                <Message></Message>
                </section>

                <section class="main-area">
                    <section class="sidebar">
                        <Inventory className={'vertical'}></Inventory>
                        <ActionsList></ActionsList>
                    </section>

                    <section class="canvas">
                        <Location>
                            <span className="location-name"></span>
                            <img className="landscape" src="{{ place.image.url }}"></img>
                            <BuildingList></BuildingList>
                            <Inventory className={'horizontal'}></Inventory>
                        </Location>
                    </section>
                    <section class='sidebar'>
                        <VillagerList></VillagerList>
                    </section>
                    <section class={'sidebar'}>
                        <Log></Log>
                    </section>

                    <DialogueBox></DialogueBox>

                </section>
            </div>
        )
    }
}

