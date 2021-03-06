/*
 * Copyright 2016 Intel Corporation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "oc-dev-addr.h"

extern "C" {
#include <string.h>
}

std::string c_OCDevAddr(napi_env env, napi_value source,
                        OCDevAddr *destination) {
  std::string returnValue;
  J2C_ASSIGN_MEMBER_VALUE_RETURN((env), destination, source, OCTransportAdapter,
                                 adapter, napi_number, "addr", uint32,
                                 uint32_t);
  J2C_ASSIGN_MEMBER_VALUE_RETURN((env), destination, source, OCTransportFlags,
                                 flags, napi_number, "addr", uint32, uint32_t);
  J2C_ASSIGN_MEMBER_VALUE_RETURN((env), destination, source, uint32_t, ifindex,
                                 napi_number, "addr", uint32, uint32_t);
  J2C_ASSIGN_MEMBER_VALUE_RETURN((env), destination, source, uint16_t, port,
                                 napi_number, "addr", uint32, uint32_t);
  char *addr = nullptr;
  J2C_GET_STRING_RETURN(env, addr, source, false, "addr");
  if (strlen(addr) > MAX_ADDR_STR_SIZE) {
    returnValue =
        LOCAL_MESSAGE("OCDevAddr field 'addr' exceeds size MAX_ADDR_STR_SIZE");
  } else {
    strcpy(destination->addr, addr);
  }
  delete addr;
  return returnValue;
}

std::string js_OCDevAddr(napi_env env, OCDevAddr *source,
                         napi_value *destination) {
  NAPI_CALL_RETURN(env, napi_create_object(env, destination));
  C2J_SET_NUMBER_MEMBER_RETURN(env, *destination, source, adapter);
  C2J_SET_NUMBER_MEMBER_RETURN(env, *destination, source, flags);
  C2J_SET_NUMBER_MEMBER_RETURN(env, *destination, source, ifindex);
  C2J_SET_NUMBER_MEMBER_RETURN(env, *destination, source, port);
  C2J_SET_PROPERTY_RETURN(env, *destination, "addr", string_utf8, source->addr,
                          strlen(source->addr));
  return std::string();
}
