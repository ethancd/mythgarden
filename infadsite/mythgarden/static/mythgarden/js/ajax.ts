import Cookies from 'js-cookie'

import {
  getStrOrError
} from './staticUtils'
import renderApp from './react-script'

// fn: given a post url and a data object, make an xhr call to the server and return the response
async function post (url: string, data: object): Promise<Response> {
  const csrfToken = getStrOrError(Cookies.get('csrftoken'))

  return await new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', url)
    xhr.setRequestHeader('Content-Type', 'application/json')
    xhr.setRequestHeader('X-CSRFToken', csrfToken)
    xhr.send(JSON.stringify(data))

    xhr.onload = () => {
      if (xhr.status === 200) {
        resolve(JSON.parse(xhr.responseText))
      } else {
        reject(xhr.responseText)
      }
    }
  })
}

async function postAction (description: string): Promise<void> {
  await post('action', { description })
    .then((response: any) => {
      // console.log(response)

      if (response.error != null) {
        throw response
      }

      if (response.game_over != null) {
        window.location.href = '/'
        return
      }

      renderApp(response)
    }).catch((response: any) => {
      // console.log(response)
      // renderApp(response)
    })
}

export {
  post,
  postAction
}
