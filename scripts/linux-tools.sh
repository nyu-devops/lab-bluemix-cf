#!/bin/bash
# Add the IBM Cloud CLI if not ARM architecture
if [ $(uname -m) != aarch64 ]; then
    echo "Installing IBM Cloud CLI..."
    curl -fsSL https://clis.cloud.ibm.com/install/linux | sh
    echo "alias ic=ibmcloud" >> /home/devops/.bashrc
    echo "Installing Cloud Foundry CLI..."
    ibmcloud cf install -f
else \
    echo "Sorry IBM Cloud does not support aarch64 architecture :("
fi;
