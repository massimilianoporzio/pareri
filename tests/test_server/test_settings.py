"""Test coverage for development settings utility functions."""


def test_custom_show_toolbar_covers_all_branches(monkeypatch):
    """Tests _custom_show_toolbar function for both branches."""
    from server.settings.environments import development  # noqa: PLC0415

    class DummyUser:
        def __init__(self, is_superuser):
            self.is_superuser = is_superuser

    class DummyRequest:
        def __init__(self, is_superuser):
            self.user = DummyUser(is_superuser)

    # Covers both True and False branches
    assert development._custom_show_toolbar(DummyRequest(True)) is True  # noqa: FBT003, SLF001
    assert development._custom_show_toolbar(DummyRequest(False)) is False  # noqa: FBT003, SLF001
