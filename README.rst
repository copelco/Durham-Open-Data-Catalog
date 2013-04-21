Durham, NC Open Data Catalog
============================

Open Data Catalog for Durham, NC. Based on `Open Data Philly`_, which is
powered by the `Open Data Catalog`_. Community run by the `Triangle Code for
America`_ brigade.

.. _Open Data Philly: http://www.opendataphilly.org/
.. _Open Data Catalog: https://github.com/azavea/Open-Data-Catalog/
.. _Triangle Code for America: https://plus.google.com/u/1/communities/102062378630945793665


Development
-----------

Below you will find basic setup and deployment instructions for the Durham ODC
project. To begin you should have the following applications installed on your
local development system::

- Python >= 2.6 (2.7 recommended)
- `pip >= 1.1 <http://www.pip-installer.org/>`_
- `virtualenv >= 1.7 <http://www.virtualenv.org/>`_
- `virtualenvwrapper >= 3.0 <http://pypi.python.org/pypi/virtualenvwrapper>`_
- Postgres >= 8.4 (9.1 recommended)
- git >= 1.7

The deployment uses SSH with agent forwarding so you'll need to enable agent
forwarding if it is not already by adding ``ForwardAgent yes`` to your SSH config.


Vagrant Testing
---------------

You can test the provisioning/deployment using `Vagrant <http://vagrantup.com/>`_.

After installing Vagrant, install `Salty Vagrant <https://github.com/saltstack/salty-vagrant>`_:

    vagrant plugin install vagrant-salt

Edit `salt/roots/pillar/users.sls` and add your user and ssh key, following
the examples. Later you'll be able to ssh to the vagrant system using that
userid and key.

Using the Vagrantfile you can start up the VM. This requires the ``precise32``
box::

    vagrant up

You can find out how ssh is set up by running:

    vagrant ssh_config

Example output::

    $ vagrant ssh-config
    Host default
      HostName 127.0.0.1
      User vagrant
      Port 2222

You can ssh in as any user with::

    ssh -p 2222 yourusername@127.0.0.1

where `yourusername` is a user you added to users.sls, and 2222 and
127.0.0.1 are changed to whatever vagrant reported.

You can also ssh in as `vagrant` by simply doing::

    vagrant ssh

and vagrant has sudo, so you can do anything you need that way.


If you change the salt files and want to update the virtual machine,
you can::

    ssh -p 2222 localhost sudo salt-call --local state.highstate [-l debug]

but it's easier to::

    vagrant reload

which will both provision and reboot.

You can provision a new server with the
``setup_server`` fab command. It takes a list of roles for this server
('app', 'db', 'lb') or you can say 'all'::

        fab vagrant setup_server:all

Then you have to do an initial deploy.  You also use this command to
deploy updates::

        fab vagrant deploy

or::

        fab vagrant deploy:<branchname>

The Vagrantfile arranges for port 80 in the vm to be accessible
as port 8089 on the host system. The fabfile sets up the configuration
to assume a hostname of `dev.example.com`. So to visit the running
web site:

1. Add `127.0.0.1 dev.example.com` to your `/etc/hosts` file (change the hostname
   if you changed it in the fabfile).

2. Visit `http://dev.example.com:8089/`
