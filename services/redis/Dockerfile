FROM library/redis

RUN redis-cli config set client-output-buffer-limit "pubsub 0 0 0"
RUN redis-cli config set client-output-buffer-limit "slave 0 0 0"

