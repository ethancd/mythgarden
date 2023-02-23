import { createContext } from 'react'
import { post } from './ajax'
import { updatePage, passErrorToUser } from './script'

async function postAction (description: string) {
  await post('action', { description })
    .then((response: any) => {
      console.log(response)

      if (response.error) {
        throw response
      }

      if (response.game_over) {
        window.location.href = '/'
        return
      }

      updatePage(response)
    }).catch((response: any) => {
      console.log(response)
      passErrorToUser(response)
    })
}

export const PostAction = createContext(postAction)
