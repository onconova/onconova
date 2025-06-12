from datetime import datetime
from django.test import TestCase 
from pop.tests import factories
from pop.research.models.project import ProjectMembership

class ProjectModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.project = factories.ProjectFactory()
        cls.project.save()

    def test_project_membership(self):
        for user in self.project.members.all():
            membership = ProjectMembership.objects.filter(project=self.project, member=user).first()
            self.assertTrue(membership)
            self.assertTrue(membership.project == self.project)
            self.assertTrue(membership.date_joined == datetime.now().date())


class ProjectDataManagerGrantModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.unauthorized_user = factories.UserFactory.create(access_level=1)

        cls.authorized_user = factories.UserFactory.create(access_level=1)
        cls.grant = factories.ProjectDataManagerGrantFactory.create(member=cls.authorized_user)
        cls.authorized_user.refresh_from_db() 

        cls.revoked_user = factories.UserFactory.create(access_level=1)
        cls.grant = factories.ProjectDataManagerGrantFactory.create(member=cls.revoked_user, revoked=True)
        cls.revoked_user.refresh_from_db() 
        
    def test_auhtorized_user_is_granted_right(self):
        self.assertTrue(self.authorized_user.can_manage_cases)

    def test_unauhtorized_user_is_not_granted_right(self):
        self.assertFalse(self.unauthorized_user.can_manage_cases)
        
    def test_auhtorized_user_is_revoked_right(self):
        self.assertFalse(self.revoked_user.can_manage_cases)