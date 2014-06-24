# Sportsfronter Puppet setup

exec {'apt_update':
  command => '/usr/bin/apt-get update',
}

package {['libpq-dev', 'python-dev', 'python-pip' ]:
  ensure  => installed,
  require => Exec['apt_update'],
  notify  => Exec['install_django']
}

package { 'filewatcher':
    ensure   => 'installed',
    provider => 'gem',
}

file { '/vagrant/webapp/sportsfronter/settings_dev.py':
  ensure => present,
  source => '/vagrant/webapp/sportsfronter/settings_dev_renamethisfile.py'
}

exec { 'install_django':
  command => '/usr/bin/pip install -r /vagrant/webapp/requirements.txt',
  require => Package['python-pip'],
}

# Sync models to database:
exec {'setup_django_models':
  cwd     => '/vagrant/webapp',
  command => '/usr/bin/python manage.py syncdb --noinput',
  require => [Exec['install_django']],
}

exec {'setup_django_migrations':
  cwd     => '/vagrant/webapp',
  command => '/usr/bin/python manage.py migrate',
  require => [Exec['setup_django_models']],
}

exec {'setup_django_create_superuser':
  cwd     => '/vagrant/webapp',
  command => '/usr/bin/python manage.py migrate',
  require => [Exec['setup_django_models']],
}

class { 'postgresql::server':
  config_hash => {
    'ip_mask_deny_postgres_user' => '0.0.0.0/32',
    'ip_mask_allow_all_users'    => '0.0.0.0/0',
    'listen_addresses'           => '*',
    #'ipv4acls'                   => ['hostssl all johndoe 192.168.0.0/24 cert'],
    'manage_pg_hba_conf'         => false,
    'postgres_password'          => 'TPSrep0rt!',
  },
}

# For some reasons it runs the reload before /etc/init.d/postgresql is available => enforce the right order
Package['postgresql-server'] -> Exec['reload_postgresql']

postgresql::db { 'sportsfronter':
  user     => 'sportsfronter',
  password => 'sportsfronter-django'
}

# Exec setup django after the DB is installed
Postgresql::Db['sportsfronter'] ~> Exec['setup_django_models']

# Upstart job definition for the backend app
file {'/etc/init/sportsfronter-backend.conf':
  ensure => file,
  source => '/vagrant/vagrant_config/puppet/files/etc/init/sportsfronter-backend.conf'
}

service {'sportsfronter-backend':
  ensure  => running,
  require => [File['/etc/init/sportsfronter-backend.conf'], Exec['setup_django_models']],
}
