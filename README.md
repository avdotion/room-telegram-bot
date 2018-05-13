# room-telegram-bot
The Room Bot with Queues and Raiting

## What the bot can do
* Display current date
* Display room score, specific person score
* Display persons activities in queue
* Display nightmentor
* Access to hot-managing with activities (every user can add, only admin can delete)

> All data stores in yaml file

## Configuration file example
```yaml
actions:
  []
user_scores:
  123456789: 0
  123456790: 0
  123456791: 0
  123456792: 0
```

## Goals
- [x] Code Engine for Room Bot
- [ ] Code "interface" as Telegram Bot (as an example)
- [ ] "Get Started" notes

### The _engine.py_ features
* Import/export data to `.yaml` config
* User Model (name, id, balance, admin features and etc)
* Action system (everybody can receive achievements, admin can approve them)
* Board (agenda) 
