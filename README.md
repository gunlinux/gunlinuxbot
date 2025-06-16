```
cp services/local_events.service ~/.config/systemd/user/local_events.service
systemctl --user daemon-reload
systemctl --user enable local_events.service
systemctl --user start local_events.service
systemctl --user status local_events.service
```

