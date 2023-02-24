import React from 'react'
import ReactDOM from 'react-dom/client'
import { App, type AppProps } from './app'

const root = ReactDOM.createRoot(document.getElementById('app-root'))
const appData = JSON.parse(document.getElementById('app-data').textContent)
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
