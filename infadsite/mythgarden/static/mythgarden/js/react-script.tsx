import React from 'react'
import ReactDOM from 'react-dom/client'
import { App, type AppProps } from './app'

const root = ReactDOM.createRoot(document.getElementById('app-root') as Element)
const appDataElement = document.getElementById('app-data') as Element
const appData = JSON.parse(appDataElement.textContent as string)
root.render(
  <React.StrictMode>
    <App {...appData} />
  </React.StrictMode>
)

export default function renderApp (appData: AppProps): void {
  root.render(
        <React.StrictMode>
            <App {...appData} />
        </React.StrictMode>
  )
}
