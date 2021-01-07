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

from typing import List

from grakn.rpc.transaction import TransactionType


def parse_bool(value: str) -> bool:
    return value == "true"


def parse_list(table) -> List[str]:
    return [table.headings[0]] + list(map(lambda row: row[0], table.rows))


def parse_transaction_type(value: str) -> TransactionType:
    return TransactionType.READ if value == "read" else TransactionType.WRITE

