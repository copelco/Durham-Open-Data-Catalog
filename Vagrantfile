Vagrant.configure("2") do |config|
    # Every Vagrant virtual environment requires a box to build off of.
    config.vm.box = "precise32"

    # The url from where the 'config.vm.box' box will be fetched if it
    # doesn't already exist on the user's system.
    config.vm.box_url = "http://files.vagrantup.com/precise32.box"

    config.vm.network :private_network, ip: "192.168.50.5"

    ## For masterless, mount your file roots file root
    config.vm.synced_folder "salt/roots/", "/srv/"

    ## Set your salt configs here
    config.vm.provision :salt do |salt|
        ## Minion config is set to ``file_client: local`` for masterless
        salt.minion_config = "salt/minion"

        ## Installs our example formula in "salt/roots/salt"
        salt.run_highstate = true
    end
end
# salt-call --local state.highstate -l debug
# http://www.barrymorrison.com/2013/Mar/11/deploying-django-with-salt-stack/
# https://github.com/brutasse/states
# https://github.com/illumin-us-r3v0lution/django-saltstack/blob/master/salt/postgresql/init.sls
# https://github.com/uggedal/states
# https://github.com/kwo/salt-states