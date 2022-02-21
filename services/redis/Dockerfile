FROM redis:6.2.6

ADD https://raw.githubusercontent.com/redis/redis/unstable/redis.conf /usr/local/etc/redis/redis.conf
RUN sed -i 's/client-output-buffer-limit pubsub 32mb 8mb 60/client-output-buffer-limit pubsub 0 0 0 \nclient-output-buffer-limit slave 0 0 0/g' /usr/local/etc/redis/redis.conf && \
    sed -i 's/repl-diskless-sync-max-replicas 0/#repl-diskless-sync-max-replicas 0/g' /usr/local/etc/redis/redis.conf && \
    sed -i 's/appenddirname "appendonlydir"/#appenddirname "appendonlydir"/g' /usr/local/etc/redis/redis.conf && \
    sed -i 's/aof-timestamp-enabled no/#aof-timestamp-enabled no/g'  /usr/local/etc/redis/redis.conf && \
    sed -i 's/hash-max-listpack-entries 512/#hash-max-listpack-entries 512/g'  /usr/local/etc/redis/redis.conf && \
    sed -i 's/hash-max-listpack-value 64/#hash-max-listpack-value 64/g'  /usr/local/etc/redis/redis.conf && \
    sed -i 's/list-max-listpack-size -2/#list-max-listpack-size -2/g' /usr/local/etc/redis/redis.conf &&\
    chmod 644 /usr/local/etc/redis/redis.conf

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]