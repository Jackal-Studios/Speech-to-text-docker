FROM ubuntu:latest
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg 
RUN python3 -m pip install -U \
    pickle5 \
    aiogram \
    google-cloud-speech


WORKDIR /home/speechtotextbot/
COPY ./pythonfiles/main.py ./pythonfiles/
#COPY ./db/my_ids.picke ./db/