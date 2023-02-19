'use strict';

import React from "react";
import { post } from './ajax';

function Action({ description, emoji, display_cost, updatePage, passErrorToUser }) {
    function executeAction() {
        post('action', {description})
            .then((response: any) => {
                console.log(response)

                if (response.error) {
                    throw response;
                }

                if (response.game_over) {
                    window.location.href = '/';
                    return;
                }

                updatePage(response);

            }).catch((response: any) => {
                console.log(response)
                passErrorToUser(response);
            });
    }

    return (
        <li
            onClick={executeAction}
            className='action'
        >
            <span className='type-emoji'>{emoji}</span>&nbsp;
            <span className="description">{description}</span>
            <span className="cost">{display_cost}</span>
        </li>
    )
}

function ActionsList({ actions, updatePage, passErrorToUser }) {
    return (
        <ul className="vertical actions">
            {actions.map(action => {
                return Action({...action, updatePage, passErrorToUser})
            })}
        </ul>
    )
}

export {
    Action,
    ActionsList,
}