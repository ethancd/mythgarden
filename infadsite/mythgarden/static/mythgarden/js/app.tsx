import React from "react";
import List from "./list";
import Hero from "./hero";
import Clock from "./clock";
import Wallet from "./wallet";
import Item from "./item";
import Action from "./action";
import Location from "./location";
import Building from "./building";
import Villager from "./villager";
import Dialogue from "./dialogue";
// import Log from "./log";

export default class App extends React.Component<any, any> {
    constructor(props) {
        super(props);
    }

    shouldShowDialogue() {
        return this.props.dialogue.id != null;
    }

    render() {
        const {
            hero,
            clock,
            wallet,
            items,
            actions,
            place,
            buildings,
            local_item_tokens,
            villager_states,
            dialogue
        } = this.props;

        return (
            <div class="page">
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

                <section class="main-area">
                    <section class="sidebar left">
                        <List orientation='vertical' id='inventory'>
                            {items.map(item => Item(item))}
                        </List>
                        <List orientation='vertical' id='actions'>
                            {actions.map(action => Action(action))}
                        </List>
                    </section>

                    <section class="canvas">
                        <Location {...place}>
                            <List orientation='horizontal' id='buildings'>
                                {buildings.map(building => Building(building))}
                            </List>
                            <List orientation='horizontal' id='local-items'>
                                {local_item_tokens.map(item => Item(item))}
                            </List>
                        </Location>
                    </section>

                    <section class='sidebar right'>
                        <List orientation='vertical' id='villagers'>
                            {villager_states.map(villager => Villager(villager))}
                        </List>
                    </section>
                </section>
                <section class='footer'>
                    {/*<Log></Log>*/}
                    <Dialogue {...dialogue} key={dialogue.id} shouldShow={this.shouldShowDialogue()}></Dialogue>
                </section>
            </div>
        )
    }
}

