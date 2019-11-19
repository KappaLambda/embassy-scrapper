# Scrapper for London Greek Embassy

Scrapper for London Greek Embassy's appointment reservation site. Logs every available date for all appointment categories in a csv file. Sends an email to notify about availability on Military Affairs.

## Requirements

* Ubuntu 16.04
* Python 3.6.5
* Pyenv
* Pyenv virtualenv plugin

## Installation

```
$ git clone https://github.com/pyenv/pyenv.git ~/.pyenv
$ git clone https://github.com/pyenv/pyenv-virtualenv.git $(pyenv root)/plugins/pyenv-virtualenv
$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
$ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
$ echo 'eval "$(pyenv init -)"' >> ~/.bashrc
$ exec "$SHELL"
$ pyenv install 3.6.5
$ pyenv virtualenv 3.6.5 scrapper
$ git clone https://github.com/KappaLambda/embassy-scrapper.git
$ cd embassy-scrapper/
$ pyenv local scrapper
$ pip install -r requirements.txt
```

## Usage

Edit `mailgun.conf` with your MAILGUN_DOMAIN_NAME, your MAILGUN_API_KEY, and your desired RECEIVER_EMAIL.

Use crontab to run scrapper.py at intervals. The following example executes scrapper every 15 minutes.

```
$ crontab -e
*/15 * * * * /home/vagrant/.pyenv/shims/python /srv/www/embassy-scrapper/scrapper.py
```
