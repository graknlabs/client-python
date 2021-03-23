#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
from typing import Iterator

import grakn_protocol.common.concept_pb2 as concept_proto

from grakn.api.concept.thing.relation import Relation, RemoteRelation
from grakn.api.concept.type.relation_type import RelationType
from grakn.api.concept.type.role_type import RoleType
from grakn.common.rpc.request_builder import relation_add_player_req, relation_remove_player_req, \
    relation_get_players_req, relation_get_players_by_role_type_req, relation_get_relating_req
from grakn.concept.proto import concept_proto_builder, concept_proto_reader
from grakn.concept.thing.thing import _Thing, _RemoteThing
from grakn.concept.type.role_type import _RoleType


class _Relation(Relation, _Thing):

    def __init__(self, iid: str, relation_type: RelationType):
        super(_Relation, self).__init__(iid)
        self._type = relation_type

    @staticmethod
    def of(thing_proto: concept_proto.Thing):
        return _Relation(concept_proto_reader.iid(thing_proto.iid), concept_proto_reader.type_(thing_proto.type))

    def as_remote(self, transaction):
        return _RemoteRelation(transaction, self.get_iid(), self.get_type())

    def get_type(self) -> "RelationType":
        return self._type


class _RemoteRelation(RemoteRelation, _RemoteThing):

    def __init__(self, transaction, iid: str, relation_type: RelationType):
        super(_RemoteRelation, self).__init__(transaction, iid)
        self._type = relation_type

    def as_remote(self, transaction):
        return _RemoteRelation(transaction, self.get_iid(), self.get_type())

    def get_type(self) -> "RelationType":
        return self._type

    def add_player(self, role_type, player):
        self.execute(relation_add_player_req(self.get_iid(), concept_proto_builder.role_type(role_type), concept_proto_builder.thing(player.get_iid())))

    def remove_player(self, role_type, player):
        self.execute(relation_remove_player_req(self.get_iid(), concept_proto_builder.role_type(role_type), concept_proto_builder.thing(player.get_iid())))

    def get_players(self, role_types=None):
        return [concept_proto_reader.thing(t) for rp in self.stream(relation_get_players_req(self.get_iid(), concept_proto_builder.types(role_types)))
                for t in rp.relation_get_players_res_part.things]

    def get_players_by_role_type(self):
        stream = [role_player for res_part in self.stream(relation_get_players_by_role_type_req(self.get_iid()))
                  for role_player in res_part.relation_get_players_by_role_type_res_part.role_types_with_players]

        role_player_dict = {}
        for role_player in stream:
            role = concept_proto_reader.type_(role_player.role_type)
            player = concept_proto_reader.thing(role_player.player)
            if role not in role_player_dict:
                role_player_dict[role] = []
            role_player_dict[role].append(player)
        return role_player_dict

    def get_relating(self) -> Iterator[RoleType]:
        return [_RoleType.of(rt) for rp in self.stream(relation_get_relating_req(self.get_iid()))
                for rt in rp.relation_get_relating_res_part.role_types]
