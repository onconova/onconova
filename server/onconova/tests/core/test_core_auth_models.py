from django.test import TestCase

from onconova.core.auth.models import User


class TestUserModel(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.viewer_user = User.objects.create(username="viewer_user", access_level=1)
        cls.admin_user = User.objects.create(username="admin_user", access_level=4)

    def test_role_mapping(self):
        """Ensure the access_level correctly maps to the expected role."""
        user = self.viewer_user
        self.assertEqual(user.role, "Member")

        user.access_level = 2
        user.save()
        self.assertEqual(user.role, "Project Manager")

        user.access_level = 4
        user.save()
        self.assertEqual(user.role, "System Administrator")

    def test_generated_fields_permissions(self):
        """Verify permission fields are correctly assigned based on access_level."""
        user = self.viewer_user

        # Viewer should have only view permissions
        self.assertTrue(user.can_view_cases)
        self.assertTrue(user.can_view_cohorts)
        self.assertTrue(user.can_view_datasets)
        self.assertTrue(user.can_view_projects)

        # Upgrade to Project Manager (level 2)
        user.access_level = 2
        user.save()
        self.assertTrue(user.can_manage_projects)
        self.assertTrue(user.can_export_data)

        # Upgrade to Platform Manager (level 5)
        user.access_level = 3
        user.save()
        self.assertTrue(user.can_manage_users)
        self.assertTrue(user.can_export_data)
        self.assertTrue(user.can_delete_projects)

        # Upgrade to System Admin (level 4)
        user.access_level = 4
        user.save()
        self.assertTrue(user.is_system_admin)

    def test_access_level_boundaries(self):
        """Ensure access_level constraints are respected."""
        user = self.viewer_user

        # Test min boundary
        user.access_level = -1
        with self.assertRaises(Exception):
            user.save()

        # Test max boundary
        user.access_level = 8
        with self.assertRaises(Exception):
            user.save()

    def test_default_user_settings(self):
        """Ensure default user settings behave as expected."""
        user = self.viewer_user
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_system_admin)

    def test_admin_permissions(self):
        """Ensure admin users have all permissions."""
        admin_user = self.admin_user

        self.assertTrue(admin_user.is_system_admin)
        self.assertTrue(admin_user.can_manage_users)

    def test_superuser_permissions(self):
        """Ensure admin users have all permissions."""
        super_user = self.admin_user
        super_user.access_level = 0
        super_user.is_superuser = True
        super_user.save()

        self.assertTrue(super_user.is_system_admin)
        self.assertTrue(super_user.can_manage_users)
