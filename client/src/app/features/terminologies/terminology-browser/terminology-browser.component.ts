import {
  Component,
  computed,
  effect,
  inject,
  linkedSignal,
  signal,
} from '@angular/core';
import { CommonModule, Location } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { rxResource, toSignal } from '@angular/core/rxjs-interop';
import { map, catchError, of, expand, reduce, EMPTY } from 'rxjs';

import { TerminologyService } from 'onconova-api-client';
import { CodedConceptEx } from './coded-concept-extended';

import { MessageService, TreeNode } from 'primeng/api';
import { IconFieldModule } from 'primeng/iconfield';
import { InputIconModule } from 'primeng/inputicon';
import { InputTextModule } from 'primeng/inputtext';
import { ButtonModule } from 'primeng/button';
import { ChipModule } from 'primeng/chip';
import { TableModule, TableLazyLoadEvent } from 'primeng/table';
import { SkeletonModule } from 'primeng/skeleton';
import { DividerModule } from 'primeng/divider';
import { TooltipModule } from 'primeng/tooltip';
import { SelectButton } from 'primeng/selectbutton';
import { TreeModule } from 'primeng/tree';

export interface TerminologyInfo {
  name: string;
  label: string;
  description?: string;
}

export interface TerminologyGroup {
  label: string;
  icon: string;
  items: TerminologyInfo[];
}

export const KNOWN_TERMINOLOGIES: TerminologyGroup[] = [
  {
    label: 'Demographics & Patient',
    icon: 'pi pi-user',
    items: [
      { name: 'AdministrativeGender', label: 'Administrative Gender' },
      { name: 'CauseOfDeath', label: 'Cause of Death' },
    ],
  },
  {
    label: 'Cancer Classification',
    icon: 'pi pi-sitemap',
    items: [
      { name: 'CancerTopography', label: 'Cancer Topography (ICD-O-3)', description: 'Primary cancer topography codes from ICD-O-3' },
      { name: 'CancerTopographyGroup', label: 'Cancer Topography Groups' },
      { name: 'CancerMorphology', label: 'Cancer Morphology (ICD-O-3)', description: 'Cancer morphology codes from ICD-O-3' },
      { name: 'CancerMorphologyPrimary', label: 'Cancer Morphology (Primary)' },
    ],
  },
  {
    label: 'TNM Staging',
    icon: 'pi pi-sort-amount-up',
    items: [
      { name: 'TNMStagingMethod', label: 'TNM Staging Method' },
      { name: 'TNMStage', label: 'TNM Stage' },
      { name: 'TNMPrimaryTumorCategory', label: 'Primary Tumor (T)' },
      { name: 'TNMRegionalNodesCategory', label: 'Regional Nodes (N)' },
      { name: 'TNMDistantMetastasesCategory', label: 'Distant Metastases (M)' },
      { name: 'TNMGradeCategory', label: 'Histopathological Grade (G)' },
      { name: 'TNMResidualTumorCategory', label: 'Residual Tumor (R)' },
      { name: 'TNMLymphaticInvasionCategory', label: 'Lymphatic Invasion (L)' },
      { name: 'TNMVenousInvasionCategory', label: 'Venous Invasion (V)' },
      { name: 'TNMPerineuralInvasionCategory', label: 'Perineural Invasion (Pn)' },
      { name: 'TNMSerumTumorMarkerLevelCategory', label: 'Serum Tumor Marker (S)' },
    ],
  },
  {
    label: 'Specialized Staging',
    icon: 'pi pi-chart-bar',
    items: [
      { name: 'FIGOStagingMethod', label: 'FIGO Staging Method' },
      { name: 'FIGOStage', label: 'FIGO Stage' },
      { name: 'BinetStage', label: 'Binet Stage (CLL)' },
      { name: 'RaiStagingMethod', label: 'Rai Staging Method' },
      { name: 'RaiStage', label: 'Rai Stage (CLL)' },
      { name: 'ClarkLevel', label: 'Clark Level (Melanoma)' },
      { name: 'MyelomaISSStage', label: 'Myeloma ISS Stage' },
      { name: 'MyelomaRISSStage', label: 'Myeloma R-ISS Stage' },
      { name: 'NeuroblastomaINSSStage', label: 'Neuroblastoma INSS Stage' },
      { name: 'NeuroblastomaINRGSSStage', label: 'Neuroblastoma INRGSS Stage' },
      { name: 'GleasonGradeGroupStage', label: 'Gleason Grade Group (Prostate)' },
      { name: 'WilmsTumorStage', label: "Wilms Tumor Stage" },
      { name: 'RhabdomyosarcomaClinicalGroup', label: 'Rhabdomyosarcoma Clinical Group' },
      { name: 'LymphomaStagingMethod', label: 'Lymphoma Staging Method' },
      { name: 'LymphomaStage', label: 'Lymphoma Stage' },
      { name: 'LymphomaStageValueModifier', label: 'Lymphoma Stage Modifier' },
    ],
  },
  {
    label: 'Treatment',
    icon: 'pi pi-heart',
    items: [
      { name: 'AntineoplasticAgent', label: 'Antineoplastic Agent (Drug)' },
      { name: 'AdjunctiveTherapyRole', label: 'Adjunctive Therapy Role' },
      { name: 'TreatmentTerminationReason', label: 'Treatment Termination Reason' },
      { name: 'DosageRoute', label: 'Dosage Route' },
      { name: 'SurgicalProcedure', label: 'Surgical Procedure' },
      { name: 'ProcedureOutcome', label: 'Procedure Outcome' },
      { name: 'RadiotherapyTreatmentLocation', label: 'Radiotherapy Treatment Location' },
      { name: 'RadiotherapyModality', label: 'Radiotherapy Modality' },
      { name: 'RadiotherapyTechnique', label: 'Radiotherapy Technique' },
      { name: 'CancerTreatmentResponseObservationMethod', label: 'Treatment Response Method' },
      { name: 'CancerTreatmentResponse', label: 'Treatment Response' },
    ],
  },
  {
    label: 'Anatomy & Body Sites',
    icon: 'pi pi-map-marker',
    items: [
      { name: 'ObservationBodySite', label: 'Observation Body Site' },
      { name: 'BodyLocationQualifier', label: 'Body Location Qualifier' },
      { name: 'LateralityQualifier', label: 'Laterality Qualifier' },
    ],
  },
  {
    label: 'Genomics',
    icon: 'pi pi-share-alt',
    items: [
      { name: 'Gene', label: 'Gene' },
      { name: 'MolecularConsequence', label: 'Molecular Consequence' },
      { name: 'Zygosity', label: 'Zygosity' },
      { name: 'VariantInheritance', label: 'Variant Inheritance' },
      { name: 'StructuralVariantAnalysisMethod', label: 'Structural Variant Analysis Method' },
      { name: 'MicrosatelliteInstabilityState', label: 'Microsatellite Instability State' },
    ],
  },
  {
    label: 'Family History & Risk',
    icon: 'pi pi-users',
    items: [
      { name: 'FamilyMemberType', label: 'Family Member Type' },
      { name: 'CancerRiskAssessmentMethod', label: 'Risk Assessment Method' },
    ],
  },
  {
    label: 'Conditions',
    icon: 'pi pi-book',
    items: [
      { name: 'ICD10Condition', label: 'ICD-10 Condition', description: 'ICD-10 conditions and comorbidities' },
    ],
  },
];

@Component({
  templateUrl: './terminology-browser.component.html',
  imports: [
    CommonModule,
    FormsModule,
    IconFieldModule,
    InputIconModule,
    InputTextModule,
    ButtonModule,
    ChipModule,
    TableModule,
    SkeletonModule,
    DividerModule,
    TooltipModule,
    SelectButton,
    TreeModule,
  ],
})
export class TerminologyBrowserComponent {
  readonly #terminologyService = inject(TerminologyService);
  readonly #router = inject(Router);
  readonly #location = inject(Location);
  readonly #activatedRoute = inject(ActivatedRoute);
  readonly #messageService = inject(MessageService);

  readonly #inputQueryParams = toSignal(this.#activatedRoute.queryParams);

  // ─── URL-backed state ──────────────────────────────────────────────────────

  readonly selectedTerminologyName = linkedSignal<string | undefined>(
    () => this.#inputQueryParams()?.['terminology'] || undefined
  );
  readonly conceptQuery = linkedSignal<string>(
    () => this.#inputQueryParams()?.['query'] || ''
  );
  readonly selectedConceptCode = linkedSignal<string | undefined>(
    () => this.#inputQueryParams()?.['code'] || undefined
  );
  readonly conceptOffset = linkedSignal<number>(
    () => parseInt(this.#inputQueryParams()?.['offset'] || '0', 10)
  );
  readonly conceptSearchMode = linkedSignal<'name' | 'code'>(
    () => (this.#inputQueryParams()?.['mode'] === 'code' ? 'code' : 'name')
  );
  readonly conceptLimit = signal(50);

  // Local state
  readonly terminologyFilter = signal('');
  readonly viewMode = signal<'list' | 'tree'>('list');

  /** Tree-expanded state: set of expanded node keys */
  treeExpandedKeys: { [key: string]: boolean } = {};

  /** Currently-selected node in tree view (PrimeNG selection binding) */
  readonly selectedTreeNode = signal<TreeNode<CodedConceptEx> | null>(null);

  /** Placeholder rows while the concept list is loading */
  readonly skeletonRows = Array(12).fill({});

  // Debounce handle for search input
  private _queryDebounce: ReturnType<typeof setTimeout> | null = null;

  // Input binding for the concept search field (initialized lazily from URL)
  protected conceptQueryInput = this.#inputQueryParams()?.['query'] || '';

  // ─── Terminology catalog ───────────────────────────────────────────────────

  readonly knownTerminologies = KNOWN_TERMINOLOGIES;

  readonly filteredGroups = computed(() => {
    const filter = this.terminologyFilter().toLowerCase();
    if (!filter) return this.knownTerminologies;
    return this.knownTerminologies
      .map(g => ({
        ...g,
        items: g.items.filter(
          t =>
            t.label.toLowerCase().includes(filter) ||
            t.name.toLowerCase().includes(filter)
        ),
      }))
      .filter(g => g.items.length > 0);
  });

  readonly selectedTerminologyInfo = computed<TerminologyInfo | undefined>(() => {
    const name = this.selectedTerminologyName();
    if (!name) return undefined;
    for (const g of this.knownTerminologies) {
      const found = g.items.find(i => i.name === name);
      if (found) return found;
    }
    return { name, label: name };
  });

  // ─── Concept list resource ─────────────────────────────────────────────────

  readonly concepts = rxResource({
    request: () => {
      const term = this.selectedTerminologyName();
      if (!term) return undefined;
      return {
        terminologyName: term,
        query:
          this.conceptSearchMode() === 'name'
            ? this.conceptQuery() || undefined
            : undefined,
        codes:
          this.conceptSearchMode() === 'code' && this.conceptQuery()
            ? [this.conceptQuery()]
            : undefined,
        limit: this.conceptLimit(),
        offset: this.conceptOffset(),
      };
    },
    loader: ({ request }) =>
      this.#terminologyService.getTerminologyConcepts(request!).pipe(
        catchError((err: any) => {
          this.#messageService.add({
            severity: 'error',
            summary: 'Error loading concepts',
            detail: err?.error?.detail,
          });
          return of({ count: 0, items: [] });
        })
      ),
  });

  readonly conceptTotal = computed(() => this.concepts.value()?.count ?? 0);
  readonly conceptItems = computed(() => this.concepts.value()?.items ?? []);

  // ─── Tree mode: full concept load ─────────────────────────────────────────

  readonly allConceptsForTree = rxResource({
    request: () => {
      const term = this.selectedTerminologyName();
      if (!term || this.viewMode() !== 'tree') return undefined;
      return { terminologyName: term };
    },
    loader: ({ request }) => {
      // Server enforces NINJA_PAGINATION_MAX_LIMIT = 50; fetch all pages
      const pageSize = 50;
      return this.#terminologyService.getTerminologyConcepts({
        terminologyName: request!.terminologyName,
        limit: pageSize,
        offset: 0,
      }).pipe(
        expand((result, index) => {
          const loaded = (index + 1) * pageSize;
          if (loaded >= result.count) return EMPTY;
          return this.#terminologyService.getTerminologyConcepts({
            terminologyName: request!.terminologyName,
            limit: pageSize,
            offset: loaded,
          });
        }),
        reduce(
          (acc, result) => ({
            count: result.count,
            items: [...acc.items, ...result.items],
          }),
          { count: 0, items: [] as import('onconova-api-client').CodedConcept[] }
        ),
        catchError(() => of({ count: 0, items: [] }))
      );
    },
  });

  readonly treeNodes = computed<TreeNode<CodedConceptEx>[]>(() => {
    const items = this.allConceptsForTree.value()?.items ?? [];
    if (!items.length) return [];

    const nodeMap = new Map<string, TreeNode<CodedConceptEx>>();

    // Create a TreeNode for each concept
    for (const c of items) {
      nodeMap.set(c.code, {
        key: c.code,
        label: c.display ?? c.code,
        data: c,
        children: [],
        leaf: false,
        expanded: this.treeExpandedKeys[c.code] ?? false,
      });
    }

    const roots: TreeNode<CodedConceptEx>[] = [];
    for (const c of items as CodedConceptEx[]) {
      const node = nodeMap.get(c.code)!;
      if (c.parent && nodeMap.has(c.parent)) {
        nodeMap.get(c.parent)!.children!.push(node);
      } else {
        roots.push(node);
      }
    }

    // Mark leaves
    for (const [, n] of nodeMap) {
      n.leaf = (n.children?.length ?? 0) === 0;
    }

    return roots;
  });

  // ─── Concept detail resource (for direct URL navigation to a code) ─────────

  readonly conceptDetailResource = rxResource({
    request: () => {
      const code = this.selectedConceptCode();
      const term = this.selectedTerminologyName();
      if (!code || !term) return undefined;
      // Only fetch if not already present in the loaded page
      if (this.conceptItems().some(c => c.code === code)) return undefined;
      return { terminologyName: term, codes: [code] };
    },
    loader: ({ request }) =>
      this.#terminologyService.getTerminologyConcepts(request!).pipe(
        map(r => r.items[0]),
        catchError(() => of(undefined))
      ),
  });

  readonly selectedConcept = computed<CodedConceptEx | undefined>(() => {
    const code = this.selectedConceptCode();
    if (!code) return undefined;
    return (
      this.conceptItems().find(c => c.code === code) ??
      this.conceptDetailResource.value()
    );
  });

  readonly selectedConceptProperties = computed<{ key: string; value: string }[]>(
    () => {
      const props = this.selectedConcept()?.properties;
      if (!props) return [];
      return Object.entries(props).map(([key, value]) => ({
        key,
        value: typeof value === 'object' ? JSON.stringify(value) : String(value),
      }));
    }
  );

  // ─── Parent concept (for detail panel) ───────────────────────────────────

  readonly parentConceptResource = rxResource({
    request: () => {
      const concept = this.selectedConcept();
      const term = this.selectedTerminologyName();
      if (!concept?.parent || !term) return undefined;
      // check if already loaded
      const existing = this.conceptItems().find(c => c.code === concept.parent) ??
                        this.allConceptsForTree.value()?.items.find(c => c.code === concept.parent);
      if (existing) return undefined;
      return { terminologyName: term, codes: [concept.parent] };
    },
    loader: ({ request }) =>
      this.#terminologyService.getTerminologyConcepts(request!).pipe(
        map(r => r.items[0]),
        catchError(() => of(undefined))
      ),
  });

  readonly parentConcept = computed<CodedConceptEx | undefined>(() => {
    const concept = this.selectedConcept();
    if (!concept?.parent) return undefined;
    return (
      this.conceptItems().find(c => c.code === concept.parent) ??
      this.allConceptsForTree.value()?.items.find(c => c.code === concept.parent) ??
      this.parentConceptResource.value()
    );
  });

  // ─── URL sync effect ───────────────────────────────────────────────────────

  readonly #syncUrl = effect(() => {
    const tree = this.#router.createUrlTree([], {
      relativeTo: this.#activatedRoute,
      queryParams: {
        terminology: this.selectedTerminologyName() || undefined,
        query: this.conceptQuery() || undefined,
        mode: this.conceptSearchMode() !== 'name' ? this.conceptSearchMode() : undefined,
        offset: this.conceptOffset() || undefined,
        code: this.selectedConceptCode() || undefined,
      },
      queryParamsHandling: 'merge',
    });
    this.#location.go(tree.toString());
  });

  // ─── UI helpers & actions ──────────────────────────────────────────────────

  readonly searchModeOptions = [
    { label: 'Name', value: 'name' },
    { label: 'Code', value: 'code' },
  ];

  selectTerminology(name: string) {
    if (this.selectedTerminologyName() === name) return;
    this.selectedTerminologyName.set(name);
    this.selectedConceptCode.set(undefined);
    this.conceptOffset.set(0);
    this.conceptQueryInput = '';
    this.conceptQuery.set('');
    this.viewMode.set('list');
    this.treeExpandedKeys = {};
    this.selectedTreeNode.set(null);
  }

  selectConcept(concept: CodedConceptEx) {
    this.selectedConceptCode.set(
      concept.code === this.selectedConceptCode() ? undefined : concept.code
    );
  }

  closeConcept() {
    this.selectedConceptCode.set(undefined);
  }

  onSearchModeChange(mode: 'name' | 'code') {
    this.conceptSearchMode.set(mode);
    this.conceptOffset.set(0);
  }

  onConceptQueryInput(value: string) {
    if (this._queryDebounce) clearTimeout(this._queryDebounce);
    this._queryDebounce = setTimeout(() => {
      this.conceptQuery.set(value);
      this.conceptOffset.set(0);
    }, 350);
  }

  setViewMode(mode: 'list' | 'tree') {
    this.viewMode.set(mode);
    this.selectedTreeNode.set(null);
    if (mode === 'tree') {
      this.conceptQueryInput = '';
      this.conceptQuery.set('');
    }
  }

  navigateToParent() {
    const parent = this.selectedConcept()?.parent;
    if (parent) this.selectedConceptCode.set(parent);
  }

  onTreeNodeSelect(event: { node: TreeNode<CodedConceptEx> }) {
    this.selectedTreeNode.set(event.node);
    if (event.node.data) this.selectConcept(event.node.data);
  }

  onTreeNodeExpand(event: { node: TreeNode<CodedConceptEx> }) {
    if (event.node.key) this.treeExpandedKeys[event.node.key] = true;
  }

  onTreeNodeCollapse(event: { node: TreeNode<CodedConceptEx> }) {
    if (event.node.key) delete this.treeExpandedKeys[event.node.key];
  }

  expandAll() {
    const expand = (nodes: TreeNode<CodedConceptEx>[]) => {
      for (const n of nodes) {
        if (!n.leaf) {
          n.expanded = true;
          if (n.key) this.treeExpandedKeys[n.key] = true;
          if (n.children?.length) expand(n.children);
        }
      }
    };
    expand(this.treeNodes());
  }

  collapseAll() {
    const collapse = (nodes: TreeNode<CodedConceptEx>[]) => {
      for (const n of nodes) {
        n.expanded = false;
        if (n.key) delete this.treeExpandedKeys[n.key];
        if (n.children?.length) collapse(n.children);
      }
    };
    collapse(this.treeNodes());
  }

  onLazyLoad(event: TableLazyLoadEvent) {
    const first = event.first ?? 0;
    const rows = event.rows ?? this.conceptLimit();
    this.conceptOffset.set(first);
    this.conceptLimit.set(rows);
  }

  copyToClipboard(text: string) {
    navigator.clipboard.writeText(text).then(() => {
      this.#messageService.add({
        severity: 'success',
        summary: 'Copied',
        detail: `"${text}" copied to clipboard`,
        life: 2000,
      });
    });
  }
}
