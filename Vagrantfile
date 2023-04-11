# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  config.vm.box = "bento/ubuntu-21.04"
  config.vm.hostname = "ubuntu"

  # Forward Flask ports
  config.vm.network "forwarded_port", guest: 8080, host: 8080, host_ip: "127.0.0.1"
  # Forward CouchDB ports
  # config.vm.network "forwarded_port", guest: 5984, host: 5984, host_ip: "127.0.0.1"
    
  config.vm.network "private_network", ip: "192.168.56.10"

  # Fix Windows execute bit problem (not needed for Mac users)
  config.vm.synced_folder ".", "/vagrant", mount_options: ["dmode=755,fmode=644"]

  ############################################################
  # Provider for VirtualBox on Intel only
  ############################################################
  config.vm.provider "virtualbox" do |vb|
    # Customize the amount of memory on the VM:
    vb.memory = "1024"
    vb.cpus = 2
    # Fixes some DNS issues on some networks
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  end

  ############################################################
  # Provider for Docker on Intel or ARM (aarch64)
  ############################################################
  config.vm.provider :docker do |docker, override|
    override.vm.box = nil
    docker.image = "rofrano/vagrant-provider:debian"
    docker.remains_running = true
    docker.has_ssh = true
    docker.privileged = true
    docker.volumes = ["/sys/fs/cgroup:/sys/fs/cgroup:rw"]
    docker.create_args = ["--cgroupns=host"]
    # Uncomment to force arm64 for testing images on Intel
    # docker.create_args = ["--cgroupns=host", "--platform=linux/arm64"]     
  end

  # Copy your .gitconfig file so that your git credentials are correct
  if File.exists?(File.expand_path("~/.gitconfig"))
    config.vm.provision "file", source: "~/.gitconfig", destination: "~/.gitconfig"
  end

  # Copy your ssh keys for github so that your git credentials work
  if File.exists?(File.expand_path("~/.ssh/id_rsa"))
    config.vm.provision "file", source: "~/.ssh/id_rsa", destination: "~/.ssh/id_rsa"
  end

  # Copy your .vimrc file so that your VI editor looks right
  if File.exists?(File.expand_path("~/.vimrc"))
    config.vm.provision "file", source: "~/.vimrc", destination: "~/.vimrc"
  end

  # Copy your IBM Cloud API Key if you have one
  if File.exists?(File.expand_path("~/.bluemix/apikey.json"))
    config.vm.provision "file", source: "~/.bluemix/apikey.json", destination: "~/.bluemix/apikey.json"
  end
  
  ######################################################################
  # Create a Python 3 development environment
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    echo "****************************************"
    echo " INSTALLING PYTHON 3 ENVIRONMENT..."
    echo "****************************************"
    
    # Install Python 3 and dev tools 
    apt-get update
    apt-get install -y python3-dev python3-pip python3-venv apt-transport-https
    apt-get upgrade python3

    # Add useful utilities
    apt-get install -y git vim tree make zip curl wget jq procps net-tools
    
    # Need PostgreSQL development library to compile on arm64
    apt-get install -y gcc libpq-dev
      
    # Create a Python3 Virtual Environment and Activate it in .profile
    sudo -H -u vagrant sh -c 'python3 -m venv ~/venv'
    sudo -H -u vagrant sh -c 'echo ". ~/venv/bin/activate" >> ~/.profile'
    
    # Install app dependencies in virtual environment as vagrant user
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && pip install -U pip wheel'
    sudo -H -u vagrant sh -c '. ~/venv/bin/activate && cd /vagrant && pip install -r requirements.txt'
  SHELL

  ######################################################################
  # Add PostgreSQL docker container
  ######################################################################
  # docker run -d --name postgres -p 5432:5432 -v psql_data:/var/lib/postgresql/data postgres
  config.vm.provision :docker do |d|
    d.pull_images "postgres:alpine"
    d.run "postgres:alpine",
       args: "-d --name postgres -p 5432:5432 -v psql_data:/var/lib/postgresql/data -e POSTGRES_PASSWORD=postgres"
  end

  ######################################################################
  # Add a test database after Postgres is provisioned
  ######################################################################
  config.vm.provision "shell", inline: <<-SHELL
    # Create testdb database using postgres cli
    echo "Pausing for 60 seconds to allow PostgreSQL to initialize..."
    sleep 60
    echo "Creating test database"
    docker exec postgres psql -c "create database testdb;" -U postgres
    # Done
  SHELL
  
  # ######################################################################
  # # Add CouchDB docker container
  # ######################################################################
  # # docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass couchdb
  # config.vm.provision "docker" do |d|
  #   d.pull_images "couchdb"
  #   d.run "couchdb",
  #     args: "--restart=always -d --name couchdb -p 5984:5984 -v couchdb:/opt/couchdb/data -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass"
  # end

  ######################################################################
  # Setup a Bluemix and Kubernetes environment
  ######################################################################
  # config.vm.provision "shell", path: ".devcontainer/scripts/install-tools.sh"
  config.vm.provision "shell", inline: <<-SHELL
    # Create as the user vagrant
    sudo -H -u vagrant sh -c 'bash /vagrant/.devcontainer/scripts/install-tools.sh'
  SHELL

  ############################################################
  # Install Kubernetes CLI and Helm
  ############################################################
  config.vm.provision "shell", inline: <<-SHELL
    # Install kubectl
    curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/$(dpkg --print-architecture)/kubectl"
    install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
    rm kubectl
    echo "alias kc='/usr/local/bin/kubectl'" >> /home/vagrant/.bash_aliases
    chown vagrant:vagrant /home/vagrant/.bash_aliases
    # Install helm
    curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
  SHELL

  # ######################################################################
  # # Setup a Bluemix and Kubernetes environment
  # ######################################################################
  # config.vm.provision "shell", inline: <<-SHELL
  #   echo "\n************************************"
  #   echo " Installing IBM Cloud CLI..."
  #   echo "************************************\n"
  #   # Install IBM Cloud CLI as Vagrant user
  #   sudo -H -u vagrant sh -c '
  #   curl -fsSL https://clis.cloud.ibm.com/install/linux | sh && \
  #   ibmcloud cf install && \
  #   echo "alias ic=ibmcloud" >> ~/.bashrc
  #   '

  #   # Show completion instructions
  #   sudo -H -u vagrant sh -c "echo alias ic=/usr/local/bin/ibmcloud >> ~/.bash_aliases"
  #   echo "\n************************************"
  #   echo "If you have an IBM Cloud API key in ~/.bluemix/apiKey.json"
  #   echo "You can login with the following command:"
  #   echo "\n"
  #   echo "ibmcloud login -a https://cloud.ibm.com --apikey @~/.bluemix/apikey.json -r us-south"
  #   echo "ibmcloud target --cf -o <your_org_here> -s dev"
  #   echo "\n************************************"
  #   # Show the GUI URL for Couch DB
  #   echo "\n"
  #   echo "CouchDB Admin GUI can be found at:\n"
  #   echo "http://127.0.0.1:5984/_utils"
  # SHELL

end
