# Sportsfronter Backend

## Django Admin

### How to use the admin pages

Admin pages are located at `http://localhost:5000/admin/`.

Currently, you need to create a superuser to use the admin pages. This can be done by running `python manage.py createsuperuser` (in the "webapp" folder) and following the instructions.

## Adding new Python dependencies

Dependencies are described in `requirements.txt`. 
After installing a new one using `pip install`, you need to do the following:

       pip freeze > requirements.txt

## Database migrations with South
We use South for database migrations. The migrations scripts are located in event/migrations. For latest [documentation](http://south.readthedocs.org/en/latest/)

To create new migration script just do a change in models and then run following command:

* `./manage.py schemamigration event --auto` to generate migration script for event models.
* `./manage.py migrate event` to migrate to the latest migration script

Note: vagrant will run migrations when it starts up, so in most cases you do not have to run migrations unless you have changed any models.

## Testing

To run tests, go to the project root folder and run `./runtests.sh`


## Manual dev setup 

**Notice**: Not necessary if you use the Vagrant setup.

1. Clone from github:

    git clone git@github.com:iterate/sommer2013-sportsfronter.git

2. Install dependencies for setting up the development environment (Linux):

    sudo apt-get install postgresql libpq-dev  python-dev python-virtualenv

3. Setup virtual enviroment that simulate the Heroku env.:

    virtualenv venv --distribute
    source venv/bin/activate

   Within the sommer2013-sportsfronter run the following to install Python dependencies:

    pip install -r requirements.txt

4. Set up Postgres.
   You need to run postgreSQL locally on your dev.station. Setup a postgres user with

        username: sportsfronter
        password: sportsfronter-django
        database: sportsfornter


        sudo -u postgres psql postgres
            \password postgres
        sudo -u postgres createuser --superuser sportsfronter
        sudo -u postgres psql
            \password sportsfronter # Set this to  sportsfronter-django
        sudo -u postgres createdb -O sportsfronter sportsfronte sudo -u postgres createuser --superuser sportsfronter
        sudo -u postgres psql
        \password sportsfronter # Set this to  sportsfronter-django
        sudo -u postgres createdb -O sportsfronter sportsfronter

5. Set up Django locally
   Within this folder run and create an adminuser.

        python manage.py syncdb

   To start the Django-app locally run

       gunicorn -b 0.0.0.0:5000 sportsfronter.wsgi


   Go to http://0.0.0.0:5000/admin to test if the DJANGO app and admin runs and try to
login with your adminuser that you just created.