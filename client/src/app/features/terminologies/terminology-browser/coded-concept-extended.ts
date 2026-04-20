import { CodedConcept } from 'onconova-api-client';

/**
 * Extends the auto-generated CodedConcept interface with fields that the
 * server already returns but are absent from the current OpenAPI spec.
 *
 * TODO: Remove this file once the spec is regenerated with these fields.
 */
export interface CodedConceptEx extends CodedConcept {
  /** Code of the immediate parent concept in the terminology hierarchy. */
  parent?: string;
  /** Formal definition from the code system. */
  definition?: string;
}
