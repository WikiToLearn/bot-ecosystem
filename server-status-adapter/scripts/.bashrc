if [[ "$SSH_CONNECTION" != "" ]] ; then
    LOGIN_FROM=$(echo $SSH_CONNECTION | awk '{ print $1 }')
else
    LOGIN_FROM="Local Console"
fi
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
    $SERVER_ADAPTER_HOST/loginNotify
