#!/bin/bash
if [[ "SSH_CONNECTION" == "" ]]
then
    echo "Only from SSH"  1>&2
    exit 1
fi

if [[ "$SSH_ORIGINAL_COMMAND" == "" ]]
then
    echo "This is not your game"  1>&2
    exit 1
fi
is_number_re='^[0-9]+$'

command=$(echo "$SSH_ORIGINAL_COMMAND" | awk '{ print $1 }')
host=$(echo "$SSH_ORIGINAL_COMMAND" | awk '{ print $2 }')
port=$(echo "$SSH_ORIGINAL_COMMAND" | awk '{ print $3 }')
four_arg=$(echo "$SSH_ORIGINAL_COMMAND" | awk '{ print $4 }')

if [[ "$four_arg" != "" ]]
then
    echo "Not allowed args after the third" 1>&2
    exit 1
fi
if [[ "$command" != "nc" ]]
then
    echo "You can only use 'nc'" 1>&2
    exit 1
fi

if ! [[ $port =~ $is_number_re ]]
then
    echo "You can numeric ports" 1>&2
    exit 1
fi

LOGIN_FROM=$(echo $SSH_CONNECTION | awk '{ print $1 }')

screen_bot_notify=""
if whereis screen &> /dev/null ;  then
    screen_bot_notify="/usr/bin/screen -mdS pushnotify "
fi

$screen_bot_notify curl -v \
    -X POST \
    --connect-timeout 5 \
    --max-time 100 \
    --retry 5 \
    --retry-delay 1 \
    --retry-max-time 60 \
    --data-urlencode "username=$(id -un)" \
    --data-urlencode "hostname=$(hostname -f)" \
    --data-urlencode "loginfrom=$LOGIN_FROM" \
    --data-urlencode "to_host=$host" \
    --data-urlencode "to_port=$port" \
    $SERVER_ADAPTER_HOST/proxyCommand


exec $SSH_ORIGINAL_COMMAND
