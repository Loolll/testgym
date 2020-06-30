#!/bin/sh
runuser -l web -c 'uwsgi --emperor /etc/uwsgi/vassals --uid www-data --gid www-data'
