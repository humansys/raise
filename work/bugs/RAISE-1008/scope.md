WHAT:      Daemon sustains ~50% CPU over days, spiking to 109%+ under memory pressure.
           3 contributing factors: (1) duplicate PTB Application in __main__.py:101-104 creates
           two httpx stacks + event loops, (2) start_polling() with default poll_interval=0.0
           creates tight loop on network errors, (3) httpx logs every getUpdates at INFO level.
WHEN:      After extended uptime (3.5+ days). Worsens under memory pressure (swap thrashing).
WHERE:     packages/rai-agent/src/rai_agent/daemon/__main__.py:101-104 (duplicate Application)
           packages/rai-agent/src/rai_agent/daemon/telegram.py:520 (start_polling without poll_interval)
EXPECTED:  Daemon should idle at <5% CPU with minimal memory footprint. Single PTB Application,
           guarded poll interval, suppressed verbose logs.
Done when: (1) Only one PTB Application instance exists, (2) poll_interval >= 2.0,
           (3) httpx polling logs suppressed to WARNING level.

TRIAGE:
  Bug Type:    Logic
  Severity:    S1-High
  Origin:      Code
  Qualifier:   Incorrect
