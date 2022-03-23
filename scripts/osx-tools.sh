#!/bin/bash
# Add the IBM Cloud CLI
echo "Installing IBM Cloud CLI for macOS..."
curl -fsSL https://clis.cloud.ibm.com/install/osx | sh
echo "Installing Cloud Foundry CLI..."
ibmcloud cf install -f