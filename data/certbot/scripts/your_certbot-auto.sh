#!/bin/sh

DOMAIN=""
WWW_DOMAIN=""
CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
EMAIL=""
if [ ! -f $CERT_PATH ]; then
    certbot certonly --webroot -w /var/www/certbot -d $DOMAIN -d $WWW_DOMAIN --non-interactive --agree-tos --email $EMAIL
fi

# Renewal loop
while :; do 
    certbot renew
    sleep 12h
done
