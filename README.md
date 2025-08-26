# MOODSTRINGS

#### By: Guilherme Gumiero (@Gumierow) & Lucas Domingues (@PixeLarm12)

## Emotional recognition systems based on audio files transcriptions into MIDI files with AI

This is a final project's project of Information Systems, UNESP, course. Was made by two developers, Guilherme and Lucas, that loves technology and music.

## Useful commands

- Create `venv`: `python -m venv backend/venv`
- Execute virtual env: `. backend/venv/Scripts/activate`

## How to run

#### You need to install `Docker desktop` (if your OS is Windows) to use `docker-compose` and `docker`.

1. Clone our repo with `git clone git@github.com:PixeLarm12/moodstrings-app.git` using SSH or `git clone https://github.com/PixeLarm12/moodstrings-app.git` using HTTPS protocol (we barely recommend that uses SSH);
2. Access our application path, duplicate with `cp backend/.env.example backend/.env` and `cp frontend/.env.example frontend/.env` and `cp .env.example .env` and changes with your values;
3. Open the terminal into `moodstrings-app/` and run `docker-compose up --build` for the first time to build all containers correctly (or any new pip packages are necessary to install) and the following times you need to start app again, just `docker-compose up`. To stop containers running runs `docker-compose down`. Access terminal and you see the current both environments running. Python errors will be thrown everytime it need;
4. To install correctly all frontend packages, run `docker exec -it ms-front bash` then run `npm install`. After installation, type `exit` to quit frontend bash terminal.