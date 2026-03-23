"""Tests for permission helpers."""
from app.utils.permissions import can_view, can_comment, can_edit, is_owner, is_admin_role


class TestPermissions:
    def test_owner_can_everything(self):
        assert can_view("owner")
        assert can_comment("owner")
        assert can_edit("owner")
        assert is_owner("owner")

    def test_edit_can_view_and_comment(self):
        assert can_view("edit")
        assert can_comment("edit")
        assert can_edit("edit")
        assert not is_owner("edit")

    def test_comment_can_view_and_comment(self):
        assert can_view("comment")
        assert can_comment("comment")
        assert not can_edit("comment")

    def test_view_can_only_view(self):
        assert can_view("view")
        assert not can_comment("view")
        assert not can_edit("view")

    def test_none_cannot_anything(self):
        assert not can_view(None)
        assert not can_comment(None)
        assert not can_edit(None)

    def test_admin_role(self):
        assert is_admin_role("admin")
        assert is_admin_role("superadmin")
        assert not is_admin_role("user")

    def test_unknown_permission(self):
        assert not can_view("unknown")
        assert not can_edit("unknown")
