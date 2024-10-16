#  Copyright (c) Meta Platforms, Inc. and affiliates.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
"""
testing module
"""

from aitemplate.testing import benchmark_ait, benchmark_pt
from aitemplate.testing.detect_target import detect_target
from aitemplate.testing.profile import profile_callable

__all__ = ["benchmark_pt", "benchmark_ait", "detect_target", "profile_callable"]
