from django.db import models 

def _serialize_codeable_concept_field(data,fhir_type):
	fhir_type = fhir_type.lower()
	if fhir_type == 'code':
		return str(data.code)
	else:
		coding = construct_fhir_element('Coding',dict(
				code=data.code,
				system=data.system,
				display=data.display,
				version=data.version,
			)
		)            
		if fhir_type == 'coding':
			return coding
		elif fhir_type == 'codeableconcept':
			return construct_fhir_element('CodeableConcept',dict(coding=[coding]))
		else: 
			raise TypeError(f'Invalid serialization of ORM codeable concept to FHIR type <{fhir_type}>')    

class SingleCodedConceptField(models.ForeignKey): 

	def __init__(self, valueset, *args, **kwargs): 
		self.valueset = valueset
		kwargs.update({
			'to': f'terminology.{self.valueset}',
			'on_delete': models.PROTECT,
			'related_name': '+',
		})
		super().__init__( *args, **kwargs)
	
	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		kwargs.update({
			'valueset': self.valueset,
		})
		return name, path, args, kwargs 


	def formfield(self, **kwargs):
		from pop.common.widgets.widgets import SelectTree
		from pop.apps.valuesets.models import TreeStructure
		from django.apps import apps
		valueset = apps.get_model('valuesets',self.valueset)
		try:
			tree = TreeStructure.objects.get(model=self.valueset).tree
			tree = tree.replace('\\"',"'")
			queryset = None
		except:
			tree = None
			queryset = valueset.objects.all()

		defaults = {
			"widget": SelectTree(tree=tree, queryset=queryset, multiple=False),
		}
		defaults.update(kwargs)
		return super().formfield(**defaults)

	def value_as_fhir_from_object(self, obj, fhir_type):
		data = getattr(obj, self.name)
		if data: 
			return _serialize_codeable_concept_field(data, fhir_type)
		

class MultipleCodedConceptField(models.ManyToManyField):

	def __init__(self, valueset, *args, **kwargs): 
		self.valueset = valueset
		kwargs.update({
			'to': f'terminology.{self.valueset}',
			'related_name': '+',
		})
		super().__init__( *args, **kwargs)
	
	def deconstruct(self):
		name, path, args, kwargs = super().deconstruct()
		kwargs.update({
			'valueset': self.valueset,
		})
		return name, path, args, kwargs 
	
	def has_value_in_object(self, obj):
		return getattr(obj, self.name).count() > 0

	def value_as_fhir_from_object(self, obj, fhir_type):
		data = getattr(obj, self.name)
		if data.count()>0: 
			return [ _serialize_codeable_concept_field(concept, fhir_type) for concept in data.all() ]


class CodedConceptField(object):
	"""
	A CodeableConcept represents a value that is usually supplied by providing a
	reference to one or more terminologies or ontologies but may also be defined by
	the provision of text.
	"""
	def __new__(cls, valueset, multiple=False, *args, **kwargs):
		if multiple:
			return MultipleCodedConceptField(valueset, *args, **kwargs)
		else:
			return SingleCodedConceptField(valueset, *args, **kwargs) 

