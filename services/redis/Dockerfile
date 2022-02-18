FROM redis:6.2.6

ADD https://raw.githubusercontent.com/redis/redis/unstable/redis.conf /usr/local/etc/redis/redis.conf
RUN sed -i 's/client-output-buffer-limit pubsub 32mb 8mb 60/client-output-buffer-limit pubsub 0 0 0 \nclient-output-buffer-limit slave 0 0 0/g' /usr/local/etc/redis/redis.conf && \
    chmod 644 /usr/local/etc/redis/redis.conf

CMD ["redis-server", "/usr/local/etc/redis/redis.conf"]