# todo


- [ ] redo handler process (DONATS, TWITCH)

- [ ] remove process logic ? 

- [x]  разобратся по событиям которые прилетают почти

    - [x] twitch

    - [x] donats

- [ ] remove event

- [ ] mypy

- [ ] redo client (проебан);(((  redis_queue = "obs_events"

- [ ] test_twitch getter

- [x] test_donats getter

- [x] test_fixtures_for_queue getter

- [ ] test coverage

- [ ] tests tests

- [x] rebuld bs.gunlinux.ru -> queue (почти, падаю на хвост сендеру)

- [x] fix da_getter

- [x] rewrite da_worker




- [x] move sender ->  external object? module? or lib?

- [x] sender tests

- [x] doc queues

- [x] rewrite  donats alerts -> marshmallow

- [x] rewrite  final event to queue in marshmallow

# queue.twitch_mssg

Очередь для входящий сообщения с твитча
QueueMessageSchema
    -> TwitchMessageSchema

# queue.twitch_out

message = QueueMessageSchema().load({
            "event": "mssg",
            "data": message,
        })

# queue.da_events

payload = {
    "event": "da_message",
    "timestamp": datetime.timestamp(datetime.now()),
    "data": message_dict,
}

# redis_queue = "obs_events"


