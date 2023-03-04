# Image for a Python 3 development environment
FROM rofrano/nyu-devops-base:sp23

# Set up the Python development environment
WORKDIR /app
COPY requirements.txt .
RUN sudo python -m pip install --upgrade pip wheel && \
    sudo pip install -r requirements.txt

# Install user mode tools
COPY .devcontainer/scripts/install-tools.sh /tmp/
RUN cd /tmp; bash ./install-tools.sh
