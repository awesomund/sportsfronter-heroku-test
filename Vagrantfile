# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  # All Vagrant configuration is done here. The most common configuration
  # options are documented and commented below. For a complete reference,
  # please see the online documentation at vagrantup.com.

  # Every Vagrant virtual environment requires a box to build off of:

  config.vm.box = "precise"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"


  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine:

  config.vm.network :forwarded_port, guest: 5000, host: 5000 # Django admin app

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network :private_network, ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network :public_network

  # If true, then any SSH connections made will enable agent forwarding.
  # Default value: false
  # config.ssh.forward_agent = true

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  # config.vm.synced_folder "../data", "/vagrant_data"


  # Use puppet to provision our virtual machine
  config.vm.provision :puppet do |puppet|
        puppet.manifests_path = "vagrant_config/puppet/manifests"
        puppet.module_path = "vagrant_config/puppet/modules"
        puppet.manifest_file  = "sportsfronter.pp"
  end

end
