import ConfigParser
import os
import re
import yaml

from argyle import rabbitmq, postgres, nginx, system
from argyle.base import upload_template
from argyle.postgres import create_db_user, create_db
from argyle.supervisor import supervisor_command, upload_supervisor_app_conf
from argyle.system import service_command, start_service, stop_service, restart_service

from fabric.api import cd, env, get, hide, local, put, require, run, settings, sudo, task
from fabric.contrib import files, console, project

# Directory structure
PROJECT_ROOT = os.path.dirname(__file__)
CONF_ROOT = os.path.join(PROJECT_ROOT, 'conf')
SERVER_ROLES = ['app', 'lb', 'db']
env.project = 'OpenDataCatalog'
env.project_user = 'opendata'
env.repo = u'git@github.com:copelco/Durham-Open-Data-Catalog.git'
env.shell = '/bin/bash -c'
env.disable_known_hosts = True
env.port = 22
env.forward_agent = True

# Additional settings for argyle
env.ARGYLE_TEMPLATE_DIRS = (
    os.path.join(CONF_ROOT, 'templates')
)


@task
def vagrant():
    env.environment = 'production'
    env.hosts = ['127.0.0.1']
    env.port = 2222
    env.branch = 'master'
    env.server_name = 'dev.example.com'
    setup_path()


@task
def production():
    env.environment = 'production'
    env.hosts = ['50.17.226.149']
    env.branch = 'master'
    env.server_name = 'opendatadurham.org'
    setup_path()


def setup_path():
    env.home = '/home/%(project_user)s/' % env
    env.root = os.path.join(env.home, 'www', env.environment)
    env.code_root = os.path.join(env.root, env.project)
    env.project_root = os.path.join(env.code_root, env.project)
    env.virtualenv_root = os.path.join(env.root, 'env')
    env.log_dir = os.path.join(env.root, 'log')
    env.db = '%s_%s' % (env.project, env.environment)
    env.vhost = '%s_%s' % (env.project, env.environment)
    env.settings = 'local_settings'
    load_secrets()


def load_secrets():
    stream = open(os.path.join(PROJECT_ROOT, "secrets.yaml"), 'r')
    secrets = yaml.load(stream)
    env_secrets = secrets[env.environment]
    for key, val in env_secrets.iteritems():
        setattr(env, key, val)


@task
def salt_reload():
    sudo('salt-call --local state.highstate -l debug')


def know_github():
    """Make sure github.com is in the server's ssh known_hosts file"""
    KEYLINE = "|1|t0+3ewjYdZOrDwi/LvvAw/UiGEs=|8TzF6lRm2rdxaXDcByTBWbUIbic= ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAq2A7hRGmdnm9tUDbO9IDSwBK6TbQa+PXYPCPy6rbTrTtw7PHkccKrpp0yVhp5HdEIcKr6pLlVDBfOLX9QUsyCOV0wzfjIJNlGEYsdlLJizHhbn2mUjvSAHQqZETYP81eFzLQNnPHt4EVVUh7VfDESU84KezmD5QlWpXLmvU31/yMf+Se8xhHTvKSCZIFImWwoG6mbUoWf9nzpIoaSjB+weqqUUmpaaasXVal72J+UX2B+2RPW3RcT0eOzQgqlJL3RKrTJvdsjE3JEAvGq3lGHSZXy28G3skua2SmVi/w4yCE6gbODqnTWlg7+wC604ydGXA8VJiS5ap43JXiUFFAaQ=="
    files.append("/etc/ssh/ssh_known_hosts", KEYLINE, use_sudo=True)


@task
def setup_server(*roles):
    """Install packages and add configurations for server given roles."""
    require('environment')

    roles = list(roles)

    if not roles:
        abort("setup_server requires one or more server roles, e.g. setup_server:app or setup_server:all")

    if roles == ['all', ]:
        roles = SERVER_ROLES
    if 'base' not in roles:
        roles.insert(0, 'base')
    if 'app' in roles:
        # Create project directories and install Python requirements
        project_run('mkdir -p %(root)s' % env)
        project_run('mkdir -p %(log_dir)s' % env)
        # FIXME: update to SSH as normal user and use sudo
        # we ssh as the project_user here to maintain ssh agent
        # forwarding, because it doesn't work with sudo. read:
        # http://serverfault.com/questions/107187/sudo-su-username-while-keeping-ssh-key-forwarding
        with settings(user=env.project_user):
            if not files.exists(env.code_root):
                run('git clone --quiet %(repo)s %(code_root)s' % env)
            with cd(env.code_root):
                run('git checkout %(branch)s' % env)
                run('git pull')
        # Install and create virtualenv
        # TODO: pip is installed by salt, should not need to test for it here
        # TODO: we should make sure we install virtualenv as well
        with settings(hide('everything'), warn_only=True):
            test_for_pip = run('which pip')
        if not test_for_pip:
            sudo("easy_install -U pip")
        with settings(hide('everything'), warn_only=True):
            test_for_virtualenv = run('which virtualenv')
        if not test_for_virtualenv:
            sudo("pip install -U virtualenv")
        if not files.exists(env.virtualenv_root):
            project_run('virtualenv -p python2.7 --quiet --clear --distribute %s' % env.virtualenv_root)
            # TODO: Why do we need this next part?
            path_file = os.path.join(env.virtualenv_root, 'lib', 'python2.7', 'site-packages', 'project.pth')
            files.append(path_file, env.project_root, use_sudo=True)
            sudo('chown %s:%s %s' % (env.project_user, env.project_user, path_file))
        update_requirements()
        upload_local_settings()
        syncdb()
        upload_supervisor_app_conf(app_name=u'gunicorn')
        upload_supervisor_app_conf(app_name=u'group')
        # Restart services to pickup changes
        supervisor_command('reload')
        supervisor_command('stop %(environment)s:*' % env)
        supervisor_command('start %(environment)s:*' % env)
    if 'lb' in roles:
        nginx.remove_default_site()
        nginx.upload_nginx_site_conf(site_name=u'%(project)s-%(environment)s.conf' % env)


def project_run(cmd):
    """ Uses sudo to allow developer to run commands as project user."""
    sudo(cmd, user=env.project_user)


@task
def update_requirements():
    """Update required Python libraries."""
    require('environment')
    project_run(u'HOME=%(home)s %(virtualenv)s/bin/pip install --quiet --use-mirrors -r %(requirements)s' % {
        'virtualenv': env.virtualenv_root,
        'requirements': os.path.join(env.code_root, 'requirements', 'base.txt'),
        'home': env.home,
    })


@task
def manage_run(command):
    """Run a Django management command on the remote server."""
    require('environment')
    manage_base = u"%(virtualenv_root)s/bin/django-admin.py " % env
    if '--settings' not in command:
        command = u"%s --settings=%s" % (command, env.settings)
    project_run(u'%s %s' % (manage_base, command))


@task
def manage_shell():
    """Drop into the remote Django shell."""
    manage_run("shell")


@task
def syncdb():
    """Run syncdb and South migrations."""
    manage_run('syncdb --noinput')
    manage_run('migrate --noinput')


@task
def collectstatic():
    """Collect static files."""
    manage_run('collectstatic --noinput')


def match_changes(changes, match):
    pattern = re.compile(match)
    return pattern.search(changes) is not None


@task
def deploy(branch=None):
    """Deploy to a given environment."""
    require('environment')
    if branch is not None:
        env.branch = branch
    requirements = False
    migrations = False
    # Fetch latest changes
    with cd(env.code_root):
        with settings(user=env.project_user):
            run('git fetch origin')
        # Look for new requirements or migrations
        changes = run("git diff origin/%(branch)s --stat-name-width=9999" % env)
        requirements = match_changes(changes, r"requirements/")
        migrations = match_changes(changes, r"/migrations/")
        if requirements or migrations:
            supervisor_command('stop %(environment)s:*' % env)
        with settings(user=env.project_user):
            run("git reset --hard origin/%(branch)s" % env)
    upload_local_settings()
    if requirements:
        update_requirements()
        # New requirements might need new tables/migrations
        syncdb()
    elif migrations:
        syncdb()
    collectstatic()
    supervisor_command('restart %(environment)s:*' % env)


@task
def upload_local_settings():
    """Upload local_settings.py template to server."""
    require('environment')
    dest = os.path.join(env.project_root, 'local_settings.py')
    upload_template('django/local_settings.py', dest, use_sudo=True)
    with settings(warn_only=True):
        sudo('chown %s:%s %s' % (env.project_user, env.project_user, dest))


@task
def get_db_dump(clean=True):
    """Get db dump of remote enviroment."""
    require('environment')
    dump_file = '%(environment)s.sql' % env
    temp_file = os.path.join(env.home, dump_file)
    flags = '-Ox'
    if clean:
        flags += 'c'
    sudo('pg_dump %s %s > %s' % (flags, env.db, temp_file), user=env.project_user)
    get(temp_file, dump_file)


@task
def load_db_dump(dump_file):
    """Load db dump on a remote environment."""
    require('environment')
    temp_file = os.path.join(env.home, '%(environment)s.sql' % env)
    put(dump_file, temp_file, use_sudo=True)
    sudo('psql -d %s -f %s' % (env.db, temp_file), user=env.project_user)


@task
def salt_bootstrap():
    salt_base = os.path.join(PROJECT_ROOT, "salt/")
    minion_file = os.path.join(salt_base, "minion")
    put(minion_file, "/etc/salt/minion", use_sudo=True)
    salt_root = os.path.join(salt_base, 'roots/')
    project.rsync_project(local_dir=salt_root, remote_dir="/tmp/salt",
                          delete=True)
    sudo('rm -rf /srv/*')
    sudo('mv /tmp/salt/* /srv/')
    sudo('chown root:root -R /srv/')
    sudo('salt-call --local state.highstate -l debug')
