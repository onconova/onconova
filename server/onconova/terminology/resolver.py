import urllib


class CanonicalUrlResolver:

    def resolve_HL7_endpoint(self, canonical_url: str) -> str:
        """Resolve a HL7 canonical URL to a URL that can be used to download the
        corresponding ValueSet or CodeSystem resource.

        Args:
            canonical_url (str): The canonical URL to resolve.

        Returns:
            str: The URL that can be used to download the corresponding ValueSet or CodeSystem resource.
        """
        RELEASE_VERSIONS = {
            "http://hl7.org/fhir/us/core": "STU5.0.1",
            "http://hl7.org/fhir/us/vitals": "STU1",
            "http://hl7.org/fhir/us/mcode": "STU3",
            "http://hl7.org/fhir/uv/genomics-reporting": "STU2",
            "http://hl7.org/fhir/": "R4B",
            "http://terminology.hl7.org/": "",
        }
        for domain in RELEASE_VERSIONS:
            if canonical_url.startswith(domain):
                version = RELEASE_VERSIONS[domain]
                if "http://terminology.hl7.org/" in canonical_url:
                    canonical_url = canonical_url.replace(
                        "http://terminology.hl7.org/CodeSystem/",
                        "https://hl7.org/fhir/codesystem-",
                    )
                    canonical_url = canonical_url.replace(
                        "http://terminology.hl7.org/ValueSet/",
                        "https://hl7.org/fhir/valueset-",
                    )
                if "ValueSet" in canonical_url:
                    return (
                        canonical_url.replace("/ValueSet/", f"/{version}/ValueSet-")
                        + ".json"
                    )
                elif "CodeSystem" in canonical_url:
                    return (
                        canonical_url.replace("/CodeSystem/", f"/{version}/CodeSystem-")
                        + ".json"
                    )
                else:
                    return (
                        canonical_url.replace(
                            "http://hl7.org/fhir/",
                            f"http://hl7.org/fhir/{version}/codesystem-",
                        )
                        + ".json"
                    )
        else:
            raise KeyError(
                f"Unknown FHIR/HL7 resource requested in canonical URL: {canonical_url}"
            )

    def resolve_LOINC_endpoint(self, canonical_url: str) -> str:
        """Resolve a LOINC canonical URL to a URL that can be used to download the
        corresponding ValueSet resource.

        Args:
            canonical_url (str): The canonical URL to resolve.

        Returns:
            str: The URL that can be used to download the corresponding ValueSet resource.
        """
        valueset_name = (
            canonical_url.replace("http://", "https://")
            .replace("https://loinc.org/", "")
            .replace("/", "")
        )
        return f"http://fhir.loinc.org/ValueSet/$expand?url=http://loinc.org/vs/{valueset_name}&_format=json"

    def resolve_VSAC_endpoint(self, canonical_url: str) -> str:
        """Resolve a VSAC canonical URL to a URL that can be used to download the
        corresponding ValueSet resource.

        Args:
            canonical_url (str): The canonical URL to resolve.

        Returns:
            str: The URL that can be used to download the corresponding ValueSet resource.
        """
        valueset_name = canonical_url.replace(
            "https://vsac.nlm.nih.gov/valueset/", ""
        ).split("/")[0]
        return f"https://cts.nlm.nih.gov/fhir/res/ValueSet/{valueset_name}/$expand?_format=json"

    def resolve_CTS_endpoint(self, canonical_url: str) -> str:
        """Resolve a CTS canonical URL to a URL that can be used to download the
        corresponding ValueSet or CodeSystem resource.

        Args:
            canonical_url (str): The canonical URL to resolve.

        Returns:
            str: The URL that can be used to download the corresponding ValueSet or CodeSystem resource.
        """
        return f"{canonical_url}/$expand?_format=json"

    def resolve_Simplifier_endpoint(self, canonical_url: str) -> str:
        """Resolve a Simplifier canonical URL to a URL that can be used to download the
        corresponding ValueSet resource.

        Args:
            canonical_url (str): The canonical URL to resolve.

        Returns:
            str: The URL that can be used to download the corresponding ValueSet resource.
        """
        valueset_name = (
            canonical_url.replace("https://simplifier.net/onconova", "")
            .replace(
                "ValueSets/",
                "",
            )
            .replace(
                "CodeSystems/",
                "",
            )
        )
        return f"https://simplifier.net/onconova/{valueset_name}/$download?format=json"

    def resolve(self, canonical_url: str) -> str:
        """Resolve a canonical URL to a URL that can be used to download the
        corresponding ValueSet or CodeSystem resource.

        Args:
            canonical_url (str): The canonical URL to resolve.

        Returns:
            str: The URL that can be used to download the corresponding ValueSet or CodeSystem resource.
        """
        # Validate the input canonical_url
        if not urllib.parse.urlparse(canonical_url).scheme:  # type: ignore
            raise ValueError("Invalid URL: " + canonical_url)

        url_resolvers = {
            "loinc.org": self.resolve_LOINC_endpoint,
            "hl7.org": self.resolve_HL7_endpoint,
            "vsac.nlm.nih.gov": self.resolve_VSAC_endpoint,
            "cts.nlm.nih.gov": self.resolve_CTS_endpoint,
            "simplifier.net/onconova": self.resolve_Simplifier_endpoint,
        }

        for url_domain, resolver in url_resolvers.items():
            if url_domain in canonical_url:
                return resolver(canonical_url)
        raise KeyError(f"Unknown resource requested in canonical URL: {canonical_url}")


resolve_canonical_url = CanonicalUrlResolver().resolve
