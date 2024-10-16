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
Slice reshape scatter CUDA implementation.
"""

import jinja2

from aitemplate.backend import registry
from aitemplate.backend.backend_spec import CUDASpec
from aitemplate.backend.common.tensor import slice_reshape_scatter_common

OUTPUT_DIM_DEF_TEMPLATE = jinja2.Template(
    """
{{indent}}int64_t {{dim_name}} = {{dim_value}};
"""
)

OUTPUT_SHAPE_DEF_TEMPLATE = jinja2.Template(
    """
{{dim_defs}}
{{indent}}  int64_t *{{output_name}}_shape[] = {
{{indent}}    {{output_dim_refs}}
{{indent}}  };
"""
)

TANH_DEF = jinja2.Template(
    """
#ifndef __HALF2_TO_UI
#define __HALF2_TO_UI(var) *(reinterpret_cast<unsigned int *>(&(var)))
#endif

#ifndef __HALF_TO_US
#define __HALF_TO_US(var) *(reinterpret_cast<unsigned short *>(&(var)))
#endif

__device__  half2 fast_tanh(half2 x) {
  #if defined(__CUDA_ARCH__) && (__CUDACC_VER_MAJOR__ >= 11) && (__CUDA_ARCH__ >= 750)

  asm volatile ( "tanh.approx.f16x2 %0, %1;" : "=r"(__HALF2_TO_UI(x)) : "r"(__HALF2_TO_UI(x)));
  return x;

  #else
  CUTLASS_NOT_IMPLEMENTED();
  #endif
}

__device__  half fast_tanh(half x) {
  #if defined(__CUDA_ARCH__) && (__CUDACC_VER_MAJOR__ >= 11) && (__CUDA_ARCH__ >= 750)

  asm volatile ( "tanh.approx.f16 %0, %1;" : "=h"(__HALF_TO_US(x)) : "h"(__HALF_TO_US(x)));
  return x;

  #else
  return half(cutlass::fast_tanh(float(x)));
  #endif
}

__device__  float fast_tanh(float x) {
    float y;
    half2* x_vec = (half2*)(&x);
    half2* y_vec = (half2*)(&y);
    y_vec[0] =  fast_tanh(x_vec[0]);
    return y;
}

__device__  float2 fast_tanh(float2 x) {
    float2 y;
    half2* x_vec = (half2*)(&x);
    half2* y_vec = (half2*)(&y);
    y_vec[0] = fast_tanh(x_vec[0]);
    y_vec[1] = fast_tanh(x_vec[1]);
    return y;
}

__device__  float4 fast_tanh(float4 x) {
    float4 y;
    half2* x_vec = (half2*)(&x);
    half2* y_vec = (half2*)(&y);
    y_vec[0] = fast_tanh(x_vec[0]);
    y_vec[1] = fast_tanh(x_vec[1]);
    y_vec[2] = fast_tanh(x_vec[2]);
    y_vec[3] = fast_tanh(x_vec[3]);
    return y;
}

"""
)

EXTRA_HEADER_TEMPLATE = jinja2.Template(
    """
{% if element_func_def %}
#include <cutlass/fast_math.h>
{% endif %}
"""
)


@registry.reg("cuda.slice_reshape_scatter.func_decl")
def gen_function_decl(func_attrs):
    """Generate function declaration.

    Parameters
    ----------
    func_attrs : Dict[str, Any]
        Stores the operation attributes.
    Returns
    -------
    str
        Rendered function declaration.
    """
    return slice_reshape_scatter_common.gen_function_decl(func_attrs, CUDASpec())


@registry.reg("cuda.slice_reshape_scatter.gen_function")
def gen_function(func_attrs, element_func=None):
    """Generates function body.

    Parameters
    ----------
    func_attrs : Dict[str, Any]
        Stores the operation attributes.
    element_func: str
        Attributes for ease of tanh concatenate fusion.

    Returns
    -------
    str
        Rendered function body.
    """
    # TODO: consider to profile elems_per_thread
    return slice_reshape_scatter_common.gen_function(
        func_attrs, CUDASpec(), TANH_DEF, element_func, EXTRA_HEADER_TEMPLATE
    )


@registry.reg("cuda.slice_reshape_scatter.func_call")
def gen_function_call(func_attrs, indent="  "):
    """Generates function call.

    Parameters
    ----------
    func_attrs : Dict[str, Any]
        Stores the operation attributes.
    indent : str, optional
        Indent for template, by default "  ".

    Returns
    -------
    str
        Rendered function call.
    """
    return slice_reshape_scatter_common.gen_function_call(
        func_attrs, CUDASpec(), indent
    )
