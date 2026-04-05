# RAISE-1008 Fix Plan

Port from S1066.1 (release/3.0.0). 3 tasks, all in rai-agent daemon.

## T1: Make SessionDispatcher handler deferrable

File: `packages/rai-agent/src/rai_agent/daemon/dispatcher.py`

Change `handler` from required constructor arg to optional with `set_handler()` method.
This breaks the circular dependency: dispatcher can be created before handler exists.

Test: dispatcher without handler raises on dispatch, works after set_handler().

## T2: Eliminate duplicate PTB Application + add poll_interval

File: `packages/rai-agent/src/rai_agent/daemon/__main__.py`

Reorder build_daemon():
1. Create dispatcher (no handler yet)
2. Create TelegramTrigger (builds the ONLY Application)
3. Create TelegramHandler using `telegram_trigger.bot`
4. Wire handler into dispatcher via `set_handler()`
5. Remove standalone `ptb_app` creation

File: `packages/rai-agent/src/rai_agent/daemon/telegram.py`

Add `poll_interval=2.0` to `start_polling()` call.

Test: build_daemon() creates only one Application. poll_interval is set.

## T3: Suppress httpx polling logs

File: `packages/rai-agent/src/rai_agent/daemon/__main__.py`

In main(), after basicConfig, add:
```python
logging.getLogger("httpx").setLevel(logging.WARNING)
```

Test: httpx logger level is WARNING after main() setup.
