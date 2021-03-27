FROM osgeo/proj

# https://stackoverflow.com/questions/52065842/python-docker-ascii-codec-cant-encode-character
ENV LANG C.UTF-8

# Copy in the current project
WORKDIR /elevation
COPY . .

# Build dependencies
RUN apt-get update
RUN apt-get install -y python3-pip libgeos-dev libspatialindex-dev
RUN pip3 install Cython numpy
RUN pip3 install -r requirements.txt --no-binary pygeos --no-binary shapely
