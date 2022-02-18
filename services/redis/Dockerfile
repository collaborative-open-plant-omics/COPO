FROM redis:6.2.6

CMD ["bash","-c", "redis-cli config set client-output-buffer-limit 'pubsub 0 0 0' && redis-cli config set client-output-buffer-limit 'slave 0 0 0'"]