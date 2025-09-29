<?xml version="1.0" encoding="UTF-8"?>
<sch:schema xmlns:sch="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt2">
  <sch:ns prefix="f" uri="http://hl7.org/fhir"/>
  <sch:ns prefix="h" uri="http://www.w3.org/1999/xhtml"/>
  <!-- 
    This file contains just the constraints for the profile CancerPatient
    It includes the base constraints for the resource as well.
    Because of the way that schematrons and containment work, 
    you may need to use this schematron fragment to build a, 
    single schematron that validates contained resources (if you have any) 
  -->
  <sch:pattern>
    <sch:title>f:Patient</sch:title>
    <sch:rule context="f:Patient">
      <sch:assert test="count(f:extension[@url = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race|6.1.0']) &lt;= 1">extension with URL = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-race|6.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity|6.1.0']) &lt;= 1">extension with URL = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-ethnicity|6.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex|6.1.0']) &lt;= 1">extension with URL = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-birthsex|6.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-sex|6.1.0']) &lt;= 1">extension with URL = 'http://hl7.org/fhir/us/core/StructureDefinition/us-core-sex|6.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-overall-survival|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-overall-survival|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-age|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-age|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-age-at-diagnosis|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-age-at-diagnosis|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-data-completion-rate|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-data-completion-rate|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-cause-of-death|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-cause-of-death|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-end-of-records|0.1.0']) &lt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-end-of-records|0.1.0': maximum cardinality of 'extension' is 1</sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern>
    <sch:title>f:Patient/f:meta</sch:title>
    <sch:rule context="f:Patient/f:meta">
      <sch:assert test="count(f:id) &lt;= 1">id: maximum cardinality of 'id' is 1</sch:assert>
      <sch:assert test="count(f:versionId) &lt;= 1">versionId: maximum cardinality of 'versionId' is 1</sch:assert>
      <sch:assert test="count(f:lastUpdated) &lt;= 1">lastUpdated: maximum cardinality of 'lastUpdated' is 1</sch:assert>
      <sch:assert test="count(f:source) &lt;= 1">source: maximum cardinality of 'source' is 1</sch:assert>
    </sch:rule>
  </sch:pattern>
  <sch:pattern>
    <sch:title>f:Patient/f:name</sch:title>
    <sch:rule context="f:Patient/f:name">
      <sch:assert test="count(f:extension[@url = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-anonymized-entry|0.1.0']) &gt;= 1">extension with URL = 'http://luisfabib.github.io/onconova/StructureDefinition/onconova-ext-anonymized-entry|0.1.0': minimum cardinality of 'extension' is 1</sch:assert>
    </sch:rule>
  </sch:pattern>
</sch:schema>
