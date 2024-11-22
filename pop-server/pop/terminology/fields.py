from django.db import models 
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

