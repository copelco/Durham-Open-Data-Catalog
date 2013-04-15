app-packages:
    pkg.installed:
        - pkgs:
            - python2.7
            - python-all-dev
            - python-setuptools
            - python-pip
            - python-virtualenv
            - libpq-dev
            - libevent-1.4-2
            - libevent-core-1.4-2
            - libevent-extra-1.4-2
            - libevent-dev
            - libmemcached-dev
            - libjpeg8
            - libjpeg8-dev
            - libfreetype6
            - libfreetype6-dev
            - zlib1g
            - zlib1g-dev
            - libxml2-dev
            - libxslt1-dev
            - libgeos-c1

memcached:
    pkg:
        - installed
    service:
        - running
        - enable: True

supervisor:
    pkg:
        - installed
    service:
        - running
        - enable: True

postfix:
    pkg:
        - installed
    service:
        - running
        - enable: True
