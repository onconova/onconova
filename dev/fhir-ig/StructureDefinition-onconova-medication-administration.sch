<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt2">
  <sch:ns prefix="f" uri="http://hl7.org/fhir"/>
  <sch:ns prefix="h" uri="http://www.w3.org/1999/xhtml"/>
  <!-- 
    This file contains just the constraints for the profile CancerRelatedMedicationAdministration
    It includes the base constraints for the resource as well.
    Because of the way that schematrons and containment work, 
    you may need to use this schematron fragment to build a, 
    single schematron that validates contained resources (if you have any) 
  -->
  <sch:pattern>
    <sch:title>f:MedicationAdministration</sch:title>
    <sch:rule context="f:MedicationAdministration">
      <sch:assert test="count(f:extension[@url = 'http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-procedure-intent|4.0.0']) &lt;= 1">extension with URL = 'http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-procedure-intent|4.0.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-normalization-basis|4.0.0']) &lt;= 1">extension with URL = 'http://hl7.org/fhir/us/mcode/StructureDefinition/mcode-normalization-basis|4.0.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-cycles|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-cycles|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/ext-therapy-line-reference|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/ext-therapy-line-reference|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-adjunctive-role|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-adjunctive-role|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-is-primary-therapy|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-is-primary-therapy|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
    </sch:rule>
  </sch:pattern>
</sch:schema>
