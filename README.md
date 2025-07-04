# Бесмысленный и бесполезный бот, но на стримах позволяет покекат

## Бот разделен на сервисы

* donats_getter:

    - Собирает события от donations alerts(донаты, follow youtube, follow twitch, награды за баллы канала)
    - Кладет их в очереди: 
        events_queue.push(new_message) # локальные события 
        work_queue.push(new_message)   # события для donats_worker
        beer_queue.push(new_message)   # события для beer consumer

* donats_worker:
    - обрабатывает сообщения - если фолоу или донат кладет сообщения в очередь twitch_sender

* twitch_getter
    - читает сообщения с твитч читает
    - может в сиде реакции кидать сообщения в twitch_sender

* twitch_sender
    - просто пишет в чат, потому что может. все из своей очереди (технически команды)

* twitch_worker
    - обрабатывает сообщения может их роутить если увидел что то похожее на команду

* beer_consumer
    - собирает донаты с donation alerts, отправляет их в сервис учетов донатов  


* local_events:
    - сервис запущеный на моей машине, выдергивает евенты и может запускать кастомные скрипты, которые могут общаться с локальным obs, запускать любые команды - вроде отключения мыши


## план работ

- [ ] Починить local_events
- [ ] забирать события твитча (подписки, траты балов каналов, follow) напрямую с твитча, потому что
сейчас события забираются в donation alerts(как прокси), а он имеет обыкновение не работать и события теряются

```
cp services/local_events.service ~/.config/systemd/user/local_events.service
systemctl --user daemon-reload
systemctl --user enable local_events.service
systemctl --user start local_events.service
systemctl --user status local_events.service
```

