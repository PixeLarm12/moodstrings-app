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
2. Access our application path, duplicate with `cp backend/.env.example backend/.env` and `cp frontend/.env.example frontend/.env` and changes with your values;
3. Open the terminal into `moodstrings-app/` and run `docker-compose up -d --build` for the first time to build all containers correctly and the following times you need to start app again, just `docker-compose up -d`. To stop containers running runs `docker-compose down`.