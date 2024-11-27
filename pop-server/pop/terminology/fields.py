from django.db import models
from django.core.exceptions import FieldError

from pop.terminology.models import CodedConcept

class CodedConceptField(object):
	"""
	A CodeableConcept represents a value that is usually supplied by providing a
	reference to one or more terminologies or ontologies but may also be defined by
	the provision of text.
	"""
	def __new__(cls, terminology: CodedConcept, multiple: bool=False, *args, **kwargs):
		if multiple:
			return models.ManyToManyField(
				to = f'terminology.{terminology.__name__}',
				related_name = '+',
   				*args, **kwargs,
			)
		else:
			return models.ForeignKey(
	   			to = f'terminology.{terminology.__name__}',
				on_delete = models.PROTECT,
				related_name = '+', 
				*args, **kwargs,
			) 

class DescendsFrom(models.Lookup):
	lookup_name = "descendsfrom"

	def get_prep_lookup(self):
		"""
		Prepares the right-hand side (rhs) of the lookup before executing a query.

		This method ensures that the lookup is only applied to fields of type
		CodedConceptField by checking the alias of the left-hand side (lhs). If the
		rhs is an instance of a Django model, it converts rhs to the primary key of
		that model. It then calls the parent class's get_prep_lookup method for any
		additional preparation.

		Raises:
			FieldError: If the lookup is not applied to a CodedConceptField field.
		"""
		if not 'terminology' in self.lhs.alias:
			raise FieldError(f"Lookup {self.lookup_name} is only supported for CodedConceptField fields.")
		if isinstance(self.rhs, models.Model):
			self.rhs = self.rhs.pk 
		return super().get_prep_lookup()
	
	def as_sql(self, compiler, connection):
		"""
		Converts the lookup into SQL.

		This method is overridden from the Lookup class to create a recursive
		CTE query that traverses the parent-child relationships of the
		CodedConceptField.

		Args:
			compiler: The SQLCompiler instance.
			connection: The database connection.

		Returns:
			A tuple of the SQL query and parameters.

		"""
		# Get the left-hand and right-hand sides of the lookup
		lhs, lhs_params = self.process_lhs(compiler, connection)
		rhs, rhs_params = self.process_rhs(compiler, connection)

		# Construct the parameters
		params = lhs_params + rhs_params

		# Get the table name of the left-hand side
		table = lhs.split('.')[0].strip('"')

		# Construct the recursive CTE query
		recursive_cte = f"""
		WITH RECURSIVE descendants AS (
			SELECT auto_id
			FROM {table}
			WHERE auto_id = {rhs}
			UNION ALL
			SELECT t.auto_id
			FROM {table} AS t
			INNER JOIN descendants AS d ON t.parent_id = d.auto_id
		)
		SELECT auto_id FROM descendants
		"""

		# Return the SQL query and parameters
		return "%s IN (%s)" % (lhs, recursive_cte), params
models.ForeignKey.register_lookup(DescendsFrom)
