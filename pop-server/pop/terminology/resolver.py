import urllib 

class CanonicalUrlResolver:

    def resolve_HL7_endpoint(self, canonical_url: str) -> str:
        RELEASE_VERSIONS = {
            'http://hl7.org/fhir/us/core': 'STU5.0.1',
            'http://hl7.org/fhir/us/vitals': 'STU1',
            'http://hl7.org/fhir/us/mcode': 'STU3',
            'http://hl7.org/fhir/uv/genomics-reporting': 'STU2',
            'http://hl7.org/fhir/': 'R4B',
            'http://terminology.hl7.org/': '',
        }
        for domain in RELEASE_VERSIONS:
            if canonical_url.startswith(domain):
                version = RELEASE_VERSIONS[domain]
                if 'ValueSet' in canonical_url:
                    return canonical_url.replace('/ValueSet/',f'/{version}/ValueSet-') + '.json'
                elif 'CodeSystem' in canonical_url :
                    return canonical_url.replace('/CodeSystem/',f'/{version}/CodeSystem-') + '.json'
                else:
                    return canonical_url.replace('http://hl7.org/fhir/',f'http://hl7.org/fhir/{version}/codesystem-') + '.json'
        else:
            raise KeyError(f'Unknown FHIR/HL7 resource requested in canonical URL: {canonical_url}')
    def resolve_LOINC_endpoint(self, canonical_url: str) -> str:
        valueset_name = canonical_url.replace('http://','https://').replace('https://loinc.org/','').replace('/','')  
        return f'http://fhir.loinc.org/ValueSet/$expand?url=http://loinc.org/vs/{valueset_name}&_format=json'

    def resolve_VSAC_endpoint(self, canonical_url: str) -> str:
        valueset_name = canonical_url.replace('https://vsac.nlm.nih.gov/valueset/','').split('/')[0]
        return f'https://cts.nlm.nih.gov/fhir/res/ValueSet/{valueset_name}/$expand?_format=json'

    def resolve_CTS_endpoint(self, canonical_url: str) -> str:
        return f'{canonical_url}/$expand?_format=json'

    def resolve_Simplifier_endpoint(self, canonical_url: str) -> str:
        valueset_name = canonical_url.replace('https://simplifier.net/pop','').replace('ValueSets/','',).replace('CodeSystems/','',)
        return f'https://simplifier.net/pop/{valueset_name}/$download?format=json'
    
    def resolve(self, canonical_url: str) -> str:
        # Validate the input canonical_url
        if not urllib.parse.urlparse(canonical_url).scheme:
            raise ValueError("Invalid URL: " + canonical_url)

        url_resolvers = {
            'loinc.org': self.resolve_LOINC_endpoint,
            'hl7.org': self.resolve_HL7_endpoint,
            'vsac.nlm.nih.gov': self.resolve_VSAC_endpoint,
            'cts.nlm.nih.gov': self.resolve_CTS_endpoint,
            'simplifier.net/pop': self.resolve_Simplifier_endpoint,
        }
        
        for url_domain, resolver in url_resolvers.items():
            if url_domain in canonical_url:
                return resolver(canonical_url)
        raise KeyError(f'Unknown resource requested in canonical URL: {canonical_url}')

resolve_canonical_url = CanonicalUrlResolver().resolve