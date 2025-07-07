import { Injectable } from "@angular/core";
import { DataResource } from "pop-api-client";
import { TreeNode } from "primeng/api";
import OpenAPISpecification from "../../../../../../../openapi.json";

@Injectable({
  providedIn: 'root'
})
export class DatasetComposeService {

    public resourceItems: TreeNode<any>[] = [
        this.constructResourceTreeNode(DataResource.PatientCase, 'Patient case', {exclude: ['pseudoidentifier']}),
        this.constructResourceTreeNode(DataResource.NeoplasticEntity, 'Neoplastic Entities'),
        {key: 'Stagings', label: 'Stagings', children: [
            this.constructResourceTreeNode(DataResource.TnmStaging, 'TNM Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.FigoStaging, 'FIGO Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.BinetStaging, 'Binet Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.RaiStaging, 'Rai Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.BreslowDepth, 'Breslow Depths', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.ClarkStaging, 'Clark Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.IssStaging, 'ISS Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.RissStaging, 'RISS Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.GleasonGrade, 'Gleason Grades', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.InssStage, 'INSS Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.InrgssStage, 'INRGSS Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.WilmsStage, 'Wilms Stagings', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.RhabdomyosarcomaClinicalGroup, 'Rhabdomyosarcoma Groups', {exclude: ['stagingDomain']}),
            this.constructResourceTreeNode(DataResource.LymphomaStaging, 'Lymphoma Stagings', {exclude: ['stagingDomain']}),
        ]},
        this.constructResourceTreeNode(DataResource.RiskAssessment, 'Risk Assessments'),
        this.constructResourceTreeNode(DataResource.TherapyLine, 'Therapy Lines'),
        this.constructResourceTreeNode(DataResource.SystemicTherapy, 'Systemic Therapies', {exclude: ['medications'], children: [
            this.constructResourceTreeNode(DataResource.SystemicTherapyMedication, 'Medications', {isRoot: false}),
        ]}),
        this.constructResourceTreeNode(DataResource.Surgery, 'Surgeries'),
        this.constructResourceTreeNode(DataResource.Radiotherapy, 'Radiotherapies', {exclude: ['dosages', 'settings'], children: [
            this.constructResourceTreeNode(DataResource.RadiotherapyDosage, 'Dosages', {isRoot: false}),
            this.constructResourceTreeNode(DataResource.RadiotherapySetting, 'Settings', {isRoot: false})
        ]}),
        this.constructResourceTreeNode(DataResource.TreatmentResponse, 'Treatment Responses'),
        this.constructResourceTreeNode(DataResource.GenomicVariant, 'Genomic Variants'),
        {key: 'GenomicSignatures', label: 'Genomic Signatures', children: [
            this.constructResourceTreeNode(DataResource.TumorMutationalBurden, 'Tumor Mutational Burdens', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.MicrosatelliteInstability, 'Microsatellite Instabilities', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.LossOfHeterozygosity, 'Losses of Heterozygosity', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.HomologousRecombinationDeficiency, 'Homologous Recombination Deficiencies', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.TumorNeoantigenBurden, 'Tumor Neoantigen Burdens', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.AneuploidScore, 'Aneuploid Score', {exclude: ['category']}),
        ]},
        this.constructResourceTreeNode(DataResource.AdverseEvent, 'Adverse Events', {exclude: ['suspectedCauses', 'mitigations'], children: [
            this.constructResourceTreeNode(DataResource.AdverseEventSuspectedCause, 'Suspected Causes', {isRoot: false}),
            this.constructResourceTreeNode(DataResource.AdverseEventMitigation, 'Mitigations', {isRoot: false})
        ]}),
        {key: 'TumorBoards', label: 'Tumor Boards', children: [
            this.constructResourceTreeNode(DataResource.UnspecifiedTumorBoard, 'Unspecified Tumor Boards', {exclude: ['category']}),
            this.constructResourceTreeNode(DataResource.MolecularTumorBoard, 'Molecular Tumor Boards', {exclude: ['category', 'therapeuticRecommendations'], children: [
                this.constructResourceTreeNode(DataResource.MolecularTherapeuticRecommendation, 'Therapeutic Recommendations', {isRoot: false}),
            ]}),
        ]},
        this.constructResourceTreeNode(DataResource.PerformanceStatus, 'Performance Status'),
        this.constructResourceTreeNode(DataResource.Lifestyle, 'Lifestyle'),
        this.constructResourceTreeNode(DataResource.FamilyHistory, 'Family History'),
        this.constructResourceTreeNode(DataResource.ComorbiditiesAssessment, 'Comorbidities'),
        this.constructResourceTreeNode(DataResource.Vitals, 'Vitals'),
    ]
    
    
        private constructResourceTreeNode(resource: DataResource, label: string, options: {children?: any[], exclude?: string[], isRoot?: boolean} = {children: [], exclude: [], isRoot: true}){
            // Get the schema definition of the entity from the OpenAPISpecification object
            const schemas = OpenAPISpecification.components.schemas
            // Get a list of all fields/properties in that resource
            const properties = schemas[resource].properties || {};
            const propertyNodes = Object.entries(properties)
                .filter(
                    ([propertyKey,_]) => !this.createMetadataItems('').map(
                        item => item['field']).includes(propertyKey) && !['caseId', 'description','anonymized'].includes(propertyKey)
                ).flatMap(
                    ([propertyKey,property]:[string, any]) => {
                        const title: string = property.title
                        const description: string = property.description
                        if (property.anyOf && property.anyOf[property.anyOf.length-1].type === 'null') {
                            property = property.anyOf[0];
                        }
                        if (property.items) {
                            property = property.items;       
                        }
    
                        let propertyType: string;
                        if (property.type === undefined && property.$ref) {
                            propertyType = property.$ref.split('/').pop();
                        } else {
                            propertyType = property.type;
                        }     
                        return this.createTreeNode(resource, title, propertyKey, propertyType, description);
                    }
                )
                    
            const isRoot =  options?.isRoot ?? true
            const treeNode = {
                key: resource, 
                label: label, 
                children: isRoot ? [
                    {key: `${resource}-properties`, label: "Properties", children: propertyNodes.filter(
                        ((item: any) => !resource.includes(item.field) && !options?.exclude?.includes(item.field))
                    )},
                    {key: `${resource}-metadata`, label: "Metadata", children: this.createMetadataItems(resource)},
                ] : propertyNodes
            }
            treeNode.children = isRoot ? [treeNode.children[0], ...(options?.children || []), treeNode.children[1]] : treeNode.children
            return treeNode
        }
    
        private createTreeNode(resource: string, label: string, field: string, type: string, description: string | null = null) {
            let defaultTransform;
            switch (type) {
                case 'CodedConcept':
                    defaultTransform = 'GetCodedConceptDisplay';
                    break
                default:
                    defaultTransform = null;
                    break
            }        
            return {
                key: `${resource}-${field}`, 
                label: label, 
                field: field, 
                type: type, 
                data: {
                    resource: resource, 
                    field: field,
                    transform: defaultTransform,
                },
                description: description,
            }
        }
    
        private createMetadataItems(schema: string) {
            return [
                this.createTreeNode(schema, 'Database ID', 'id', 'string'),
                this.createTreeNode(schema, 'Date created', 'createdAt', 'date'),
                this.createTreeNode(schema, 'Date updated', 'updatedAt', 'date'),
                this.createTreeNode(schema, 'Created by', 'createdBy', 'User'),
                this.createTreeNode(schema, 'Updated by', 'updatedBy', 'User'),
                this.createTreeNode(schema, 'External source', 'externalSource', 'string'),
                this.createTreeNode(schema, 'External source ID', 'externalSourceId', 'string'),
            ]
        }
    
}