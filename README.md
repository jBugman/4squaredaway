## Доступ

    Login: 4sq
    Password: dev1-


## Deployment

    cd /home/ubuntu/4squaredaway
    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt

    sudo apt-get install supervisor
    sudo ln -fs /home/ubuntu/4squaredaway/deploy/4sq.conf /etc/supervisor/conf.d/4sq.conf
    sudo supervisorctl reread
    sudo supervisorctl update

Flask-Assets (Stylus) requires `sudo npm install -g stylus` (nodejs package)
