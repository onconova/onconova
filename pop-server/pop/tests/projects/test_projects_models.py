from datetime import datetime
from django.test import TestCase 
from pop.tests import factories

from pop.projects.models import ProjectMembership

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
        cls.unauthorized_user = factories.UserFactory(access_level=1)
        cls.authorized_user = factories.UserFactory(access_level=1)
        cls.grant = factories.ProjectDataManagerGrantFactory.create(member=cls.authorized_user)
        cls.grant.save()

    def test_auhtorized_user_is_granted_right(self):
        self.assertTrue(self.authorized_user.can_manage_cases)

    def test_unauhtorized_user_is_not_granted_right(self):
        self.assertFalse(self.unauthorized_user.can_manage_cases)