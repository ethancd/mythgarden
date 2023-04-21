# Mythgarden
Mythgarden is a time-loop farming-sim RPG that you can play in your browser. Think Stardew Valley + Groundhog Day, with a quirky vibe and an arcade feel.
## Gallery
<div style="display:flex;">
<img width="500" alt="Screen Shot 2023-04-02 at 2 08 44 PM" src="https://user-images.githubusercontent.com/1863479/229380272-5368126f-9fbd-4f68-88c9-704769423ccb.png">
<img width="500" alt="Screen Shot 2023-04-02 at 2 09 08 PM" src="https://user-images.githubusercontent.com/1863479/229380294-f6d853f0-27b3-4fa4-a5b9-cd11cd9dc3a2.png">
<img width="500" alt="Screen Shot 2023-04-02 at 2 13 09 PM" src="https://user-images.githubusercontent.com/1863479/229380324-9ca3533c-c7a6-4e99-b38e-983a0e30c82f.png">
<img width="500" alt="Screen Shot 2023-04-02 at 2 12 34 PM" src="https://user-images.githubusercontent.com/1863479/229380315-412aadf3-3975-4ab7-b50f-f08e1d80bbca.png">
</div>

## Tech Stack
Mythgarden was built using a Django backend and a React frontend with Typescript.

## Code flow / State machine
- **Initial page load**
  - [mythgarden.ashkie.com][ashkie] -> [urls.py](mythgarden/urls.py) -> [views.home](mythgarden/views.py) -> [action_generator.py](mythgarden/game_logic/action_generator.py) -> [home.html](mythgarden/templates/mythgarden/home.html) -> [app.tsx](mythgarden/static/mythgarden/js/app.tsx)
- **Player requests action**
  - [action.tsx](mythgarden/js/action.tsx) -> [ajax.tsx](mythgarden/js/ajax.tsx) -> [views.action](mythgarden/views.py)
- **Server executes player action**
  - [action_executor.py](mythgarden/game_logic/action_executor.py)
- **Server fires any time-based game events**
  - [event_operator.py](mythgarden/game_logic/event_operator.py)
- **Server updates state in database**
- **New state is returned to browser**
  - [views.action](mythgarden/views.py)

[ashkie]: https://mythgarden.ashkie.com
