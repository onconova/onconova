

from __future__ import unicode_literals
from functools import wraps
import warnings
from django.core.management.color import no_style
from django.db import connection, models
from django.test import SimpleTestCase


class CaseExtension(SimpleTestCase):

    _models = tuple()

    @classmethod
    def append_model(cls, model):
        cls._models += (model, )

    def _pre_setup(self):
        super(CaseExtension, self)._pre_setup()
        self._map_models('create_table')

    def _post_teardown(self):
        # If we don't remove them in reverse order, then if we created table A
        # after table B and it has a foreignkey to table B, then trying to
        # remove B first will fail on some configurations, as documented
        # in issue #1
        self._map_models('delete_table', reverse=True)
        super(CaseExtension, self)._post_teardown()

    def _map_models(self, method_name, reverse=False):
        for model in (reversed(self._models) if reverse else self._models):
            try:
                getattr(model, method_name)()
            except AttributeError:
                raise TypeError("{0} doesn't support table method {1}".format(model, method_name))
            
class FakeModel(models.Model):
    """
        FakeModel

        Base class for all fake model.
    """

    class Meta:
        abstract = True
        app_label = 'django_fake_models'

    @classmethod
    def create_table(cls):
        """
        create_table

        Manually create a temporary table for model in test data base.
        :return:
        """
        try:
            schema_editor = getattr(connection, 'schema_editor', None)
            if schema_editor:
                with schema_editor() as schema_editor:
                        schema_editor.create_model(cls)
            else:
                raw_sql, _ = connection.creation.sql_create_model(
                    cls,
                    no_style(),
                    [])
                cls.delete_table()
                cursor = connection.cursor()
                try:
                    cursor.execute(*raw_sql)
                finally:
                    cursor.close()
        except:
            pass

    @classmethod
    def delete_table(cls):
        """
        delete_table

        Manually delete a temporary table for model in test data base.
        :return:
        """
        schema_editor = getattr(connection, 'schema_editor', None)
        if schema_editor:
            with connection.schema_editor() as schema_editor:
                schema_editor.delete_model(cls)
        else:
            cursor = connection.cursor()
            try:
                with warnings.catch_warnings():
                    warnings.filterwarnings('ignore', 'unknown table')
                    cursor.execute('DROP TABLE IF EXISTS {0}'.format(cls._meta.db_table))
            finally:
                cursor.close()

    @classmethod
    def fake_me(cls, source):
        """
        fake_me

        Class or method decorator

        Class decorator: create temporary table for all tests in SimpleTestCase.
        Method decorator: create temporary model only for given test method.
        :param source: SimpleTestCase or test function
        :return:
        """
        if source and type(source) == type and issubclass(source, SimpleTestCase):
            return cls._class_extension(source)
        elif hasattr(source, '__call__'):
            return cls._decorator(source)
        else:
            raise AttributeError('source - must be a SimpleTestCase subclass of function')

    @classmethod
    def _class_extension(cls, source):
        if not issubclass(source, CaseExtension):
            @wraps(source, assigned=('__module__', '__name__',), updated=[])
            class __wrap_class__ (source, CaseExtension):
                pass
            source = __wrap_class__
        source.append_model(cls)
        return source

    @classmethod
    def _decorator(cls, source):
        @wraps(source)
        def __wrapper__(*args, **kwargs):
            try:
                cls.create_table()
                return source(*args, **kwargs)
            finally:
                cls.delete_table()
        return __wrapper__