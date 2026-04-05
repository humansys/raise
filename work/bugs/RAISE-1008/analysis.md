# RAISE-1008 Analysis

## Method: Document directly + 5 Whys (primary cause)

## Root Cause

Three independent code-level defects compound into sustained 50% CPU:

### C1: Duplicate PTB Application (primary — memory/swap pressure)

`build_daemon()` at __main__.py:101-104 creates a standalone `Application.builder().token(...).build()` 
solely to extract the `.bot` object. Then `TelegramTrigger` creates its own `Application` internally. 
Result: two httpx connection pools, two internal event loops, ~20-30 MB extra heap → swap pressure → 
kernel page faults → 65% system CPU.

**5 Whys:**
1. Why 50% CPU? → Swap thrashing from oversized daemon heap
2. Why oversized heap? → Two PTB Application instances 
3. Why two Applications? → build_daemon() creates one for .bot, TelegramTrigger creates another
4. Why extract .bot separately? → TelegramHandler built before TelegramTrigger
5. Why? → Sequencing error — trigger should be built first, bot passed to handler

### C2: poll_interval=0.0 (amplifier — tight loop on errors)

telegram.py:520 calls `start_polling()` with default `poll_interval=0.0`. Normal operation: long 
polling timeout=10s provides natural spacing. Under network errors: zero delay = tight retry loop.

### C3: Verbose httpx logs (minor — unnecessary I/O)

httpx logs every HTTP request at INFO level. 22K log records over 3.5 days, each allocating a 
Python object + I/O. No diagnostic value for routine getUpdates.

## Fix Approach

1. **Eliminate duplicate Application:** Reorder build_daemon() — construct TelegramTrigger first, 
   then pass `telegram_trigger.bot` to TelegramHandler. Remove standalone ptb_app.
2. **Set poll_interval=2.0:** Add guard interval to start_polling() call.
3. **Suppress httpx logs:** Set httpx logger to WARNING level in main().
