import random 

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

UserModel = get_user_model()

class BaseModel(models.Model):
    """
    A base model class that provides common fields and methods for all models.

    This class provides common fields and methods that are used by all models in
    the application. The fields provided by this class include a unique identifier,
    creation and modification times, and the users who created and modified the
    data. The methods provided by this class include a description property that
    returns a human-readable description of the model instance, and a method to
    generate a unique identifier for a model instance.

    Attributes:
        auto_id: A unique identifier for the model instance.
        id: A human-readable identifier for the model instance.
        created_at: The date and time at which the model instance was created.
        updated_at: The date and time at which the model instance was last modified.
        created_by: The user who created the model instance.
        updated_by: The users who modified the model instance.
    """

    auto_id = models.BigAutoField(
        verbose_name=_('Database ID'),
        help_text=_('Automated incremental database identifier'),
        primary_key=True,
        editable=False,
    )
    id = models.CharField(
        max_length=64,
        unique=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    created_by = models.ForeignKey(
        help_text=_('The user who created the original data'),
        to=UserModel,
        on_delete=models.SET_NULL,
        null=True,
    )
    updated_by = models.ManyToManyField(
        help_text=_('The user(s) who updated the data since its creation'),
        to=UserModel,
        related_name='+'
    )

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        """
        Initializes the model instance.

        This method is the constructor for the model instance. It is called when a
        new instance is created. It calls the parent class's constructor and then
        checks if the instance has a primary key and identifier. If the instance
        does not have an identifier, it generates a unique identifier for the
        instance using the `_generate_unique_id` method.

        :param args: The positional arguments to be passed to the parent class
                     constructor.
        :param kwargs: The keyword arguments to be passed to the parent class
                       constructor.
        """
        super().__init__(*args, **kwargs)
        if not self.pk and not self.id:
            self.id = self._generate_unique_id()

    @property
    def description(self):
        """
        A human-readable description of the model instance.

        This property should be implemented by subclasses to provide a human-readable
        description of the model instance. The description should be a string that is
        suitable for display to users.

        Returns:
            str: A human-readable description of the model instance.
        """
        raise NotImplementedError("Subclasses must implement the description property")

    def _generate_unique_id(self):
        """
        Generates a unique identifier for a model instance.

        This method generates a unique identifier for a model instance by prepending
        the class name to a random string of 9 digits. The identifier is then checked
        to ensure that it is not a duplicate of an existing identifier in the database.
        If the identifier is a duplicate, a new one is generated and checked until a
        unique identifier is found.

        Raises:
            RuntimeError: If a unique identifier cannot be generated after 25 retries.

        Returns:
            str: A unique identifier for the model instance.
        """
        for _ in range(25):
            random_digits = ''.join(str(random.randint(1, 9)) for _ in range(9))
            new_id = f'POP-{self.__class__.__name__}-{random_digits}'
            if not self.__class__.objects.filter(id=new_id).exists():
                return new_id
        raise RuntimeError('Unable to generate a unique identifier after 25 retries.')

    def __str__(self):
        return self.description
