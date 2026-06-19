$env:APP_ENV = if ($env:APP_ENV) { $env:APP_ENV } else { 'dev' }
$env:APP_VERSION = if ($env:APP_VERSION) { $env:APP_VERSION } else { '0.1.0' }
python wsgi.py
