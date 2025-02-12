from uuid import UUID
from pop.core.models import BaseModel, User
from pop.tests.common import AbstractModelMixinTestCase
from django.test import TestCase 



class BaseModelTestCase(AbstractModelMixinTestCase):
    mixin = BaseModel

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpassword', access_level=6)

    def test_init_with_id(self):
        instance = self.model(id='test123')
        self.assertEqual(instance.id, 'test123')

    def test_init_without_id(self):
        instance = self.model()
        self.assertIsInstance(instance.id, UUID)

    def test_description_not_implemented(self):
        instance = self.model()
        with self.assertRaises(NotImplementedError):
            str(instance)



class TestUserModel(TestCase):

    def create_user(self, username, access_level):
        """Helper function to create a user with a specific access level."""
        return User.objects.create(username=username, access_level=access_level)

    def test_role_mapping(self):
        """Ensure the access_level correctly maps to the expected role."""
        user = self.create_user(username="viewer_user", access_level=1)
        self.assertEqual(user.role, "Viewer")

        user.access_level = 3
        user.save()
        self.assertEqual(user.role, "Data Analyst")

        user.access_level = 6
        user.save()
        self.assertEqual(user.role, "System Administrator")

    def test_generated_fields_permissions(self):
        """Verify permission fields are correctly assigned based on access_level."""
        user = self.create_user(username="test_user", access_level=1)

        # Viewer should have only view permissions
        self.assertTrue(user.can_view_cases)
        self.assertTrue(user.can_view_projects)
        self.assertFalse(user.can_import_data)
        self.assertFalse(user.can_manage_cases)

        # Upgrade user to Data Contributor (level 2)
        user.access_level = 2
        user.save()
        self.assertTrue(user.can_import_data)
        self.assertTrue(user.can_manage_cases)
        self.assertFalse(user.can_export_data)

        # Upgrade user to Data Analyst (level 3)
        user.access_level = 3
        user.save()
        self.assertTrue(user.can_export_data)
        self.assertFalse(user.can_manage_projects)

        # Upgrade to Project Manager (level 4)
        user.access_level = 4
        user.save()
        self.assertTrue(user.can_manage_projects)
        self.assertTrue(user.can_access_sensitive_data)
        
        # Upgrade to Platform Manager (level 5)
        user.access_level = 5
        user.save()     
        self.assertTrue(user.can_audit_logs)
        self.assertTrue(user.can_manage_users)

        # Upgrade to System Admin (level 6)
        user.access_level = 6
        user.save()
        self.assertTrue(user.is_system_admin)

    def test_access_level_boundaries(self):
        """Ensure access_level constraints are respected."""
        user = self.create_user(username="test_user", access_level=1)

        # Test min boundary
        user.access_level = 0
        with self.assertRaises(Exception):
            user.save()

        # Test max boundary
        user.access_level = 8
        with self.assertRaises(Exception):
            user.save()

    def test_default_user_settings(self):
        """Ensure default user settings behave as expected."""
        user = self.create_user(username="new_user", access_level=1)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_system_admin)

    def test_admin_permissions(self):
        """Ensure admin users have all permissions."""
        admin_user = self.create_user(username="admin_user", access_level=6)
        
        self.assertTrue(admin_user.is_system_admin)
        self.assertTrue(admin_user.can_manage_users)
        self.assertTrue(admin_user.can_audit_logs)