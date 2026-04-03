"""Tests for SessionManager and EventBus."""

from __future__ import annotations

from rai_agent.daemon.session import InMemorySessionManager, SessionState


class TestInMemorySessionManager:
    def test_create_returns_session_state(self) -> None:
        mgr = InMemorySessionManager()
        state = mgr.create("cli:emilio:default")
        assert isinstance(state, SessionState)
        assert state.session_key == "cli:emilio:default"
        assert state.seq == 0
        assert state.agent_session_id is None

    def test_get_returns_created_session(self) -> None:
        mgr = InMemorySessionManager()
        mgr.create("key-a")
        state = mgr.get("key-a")
        assert state is not None
        assert state.session_key == "key-a"

    def test_get_unknown_key_returns_none(self) -> None:
        mgr = InMemorySessionManager()
        assert mgr.get("does-not-exist") is None

    def test_remove_deletes_session(self) -> None:
        mgr = InMemorySessionManager()
        mgr.create("key-b")
        mgr.remove("key-b")
        assert mgr.get("key-b") is None

    def test_remove_nonexistent_is_noop(self) -> None:
        mgr = InMemorySessionManager()
        mgr.remove("ghost")  # must not raise

    def test_next_seq_is_monotonic(self) -> None:
        mgr = InMemorySessionManager()
        mgr.create("key-c")
        seqs = [mgr.next_seq("key-c") for _ in range(5)]
        assert seqs == [1, 2, 3, 4, 5]

    def test_next_seq_independent_per_session(self) -> None:
        mgr = InMemorySessionManager()
        mgr.create("s1")
        mgr.create("s2")
        mgr.next_seq("s1")
        mgr.next_seq("s1")
        assert mgr.next_seq("s2") == 1  # s2 unaffected by s1

    def test_next_seq_raises_for_unknown_session(self) -> None:
        mgr = InMemorySessionManager()
        try:
            mgr.next_seq("no-such-key")
            raise AssertionError("Expected KeyError")
        except KeyError:
            pass

    def test_create_duplicate_key_overwrites(self) -> None:
        mgr = InMemorySessionManager()
        mgr.create("dup")
        mgr.next_seq("dup")  # seq = 1
        mgr.create("dup")  # reset
        assert mgr.get("dup") is not None
        assert mgr.get("dup").seq == 0  # type: ignore[union-attr]


class TestEventBus:
    def test_get_bus_returns_same_instance(self) -> None:
        from rai_agent.daemon.events import get_bus

        bus1 = get_bus()
        bus2 = get_bus()
        assert bus1 is bus2

    def test_bus_is_not_none(self) -> None:
        from rai_agent.daemon.events import get_bus

        assert get_bus() is not None
