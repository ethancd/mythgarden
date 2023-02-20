'use strict';

import React from "react";

export default function Hero({ name, portrait_url, score, koin_earned, hearts_earned }) {
    return (
        <li className="player-info">
            <div className="player-avatar">
                <img src={ portrait_url }></img>
            </div>
            <div>
                <div className="player-name">{name}</div>
                <div className="score-cont">
                    <span className="score">{score} (⚜️{koin_earned} x {hearts_earned}❤️)</span>
                </div>
            </div>
        </li>
    )
}