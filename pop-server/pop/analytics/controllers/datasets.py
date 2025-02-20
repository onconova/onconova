from django.shortcuts import get_object_or_404


from ninja import Query
from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.schemas import Paginated, ModifiedResourceSchema

from pop.analytics.models import Dataset
from pop.analytics.schemas.datasets import (
    Dataset as DatasetSchema, DatasetCreate as DatasetCreateSchema, DatasetFilters
)

@api_controller(
    "/datasets", 
    auth=[JWTAuth()], 
    tags=["Datasets"]
)
class DatasetsController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[DatasetSchema],
        },
        permissions=[perms.CanViewDatasets],
        operation_id='getDatasets',
    )
    @paginate()
    def get_all_datasets_matching_the_query(self, query: Query[DatasetFilters]): # type: ignore
        queryset = Dataset.objects.all().order_by('-created_at')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        permissions=[perms.CanManageDatasets],
        operation_id='createDataset',
    )
    def create_dataset(self, payload: DatasetCreateSchema): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)
        

    @route.get(
        path='/{datasetId}', 
        response={
            200: DatasetSchema,
            404: None,
        },
        permissions=[perms.CanViewDatasets],
        operation_id='getDatasetById',
    )
    def get_dataset_by_id(self, datasetId: str):
        return get_object_or_404(Dataset, id=datasetId)
        

    @route.delete(
        path='/{datasetId}', 
        response={
            204: None, 
            404: None,
        },
        permissions=[perms.CanManageDatasets],
        operation_id='deleteDatasetById',
    )
    def delete_dataset(self, datasetId: str):
        get_object_or_404(Dataset, id=datasetId).delete()
        return 204, None
    
    
    @route.put(
        path='/{datasetId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        permissions=[perms.CanManageDatasets],
        operation_id='updateDataset',
    )
    def update_dataset(self, datasetId: str, payload: DatasetCreateSchema): # type: ignore
        return payload.model_dump_django(instance=get_object_or_404(Dataset, id=datasetId), user=self.context.request.user)
        

