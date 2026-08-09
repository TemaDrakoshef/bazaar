from grpc import ServicerContext

from src.generated.catalog.v1 import catalog_pb2, catalog_pb2_grpc


class CatalogServiceHandler(catalog_pb2_grpc.AuthServiceServicer):
    async def CreateProduct(
        self, request: catalog_pb2.CreateProductRequest, context: ServicerContext
    ) -> catalog_pb2.Product:
        pass

    # async def ReadProduct(self, request, context):
    #     """"""
    #     return

    # async def ReadListProducts(self, request, context):
    #     """"""
    #     return

    # async def UpdateProduct(self, request, context):
    #     """"""
    #     return

    # async def DeleteProduct(self, request, context):
    #     """"""
    #     return

    # async def CreateCategory(self, request, context):
    #     """Category CRUD"""
    #     return

    # async def ReadCategory(self, request, context):
    #     """"""
    #     return

    # async def ReadListCategories(self, request, context):
    #     """"""
    #     return

    # async def UpdateCategory(self, request, context):
    #     """"""
    #     return

    # async def DeleteCategory(self, request, context):
    #     """"""
    #     return
