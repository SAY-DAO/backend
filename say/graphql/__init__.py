import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType
from sqlalchemy_continuum import version_class

from say.models import Need as NeedModel


NeedVersion = version_class(NeedModel)


class NeedVersionQl(SQLAlchemyObjectType):
    class Meta:
        model = NeedVersion
        interfaces = (relay.Node,)

        # use `only_fields` to only expose specific fields ie "name"
        # only_fields = ("name",)
        # use `exclude_fields` to exclude specific fields ie "last_name"
        exclude_fields = ("imageUrl",)


class Query(graphene.ObjectType):
    node = relay.Node.Field()

    need_versions = graphene.List(NeedVersionQl)

    def resolve_need_versions(self, info):
        query = NeedVersionQl.get_query(info)  # SQLAlchemy query
        return query.all()


schema = graphene.Schema(query=Query)
