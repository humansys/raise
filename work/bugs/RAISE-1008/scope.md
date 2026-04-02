WHAT:      Daemon sustains ~50% CPU due to duplicate PTB Application, missing poll_interval, swap pressure
WHEN:      rai-agent daemon after days of uptime — 37h CPU over 3.5 days
WHERE:     __main__.py:101-104 (duplicate Application), start_polling (poll_interval=0.0),
           httpx logging (22K INFO lines), no systemd memory limits
EXPECTED:  Daemon idles at <5% CPU under normal load
Done when: CPU usage under sustained operation is <5% average

TRIAGE:
  Bug Type:    Logic
  Severity:    S1-High
  Origin:      Code
  Qualifier:   Incorrect

STATUS: Valid — 4 contributing factors identified with forensic evidence.
