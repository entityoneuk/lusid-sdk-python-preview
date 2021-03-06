# lusid.AllocationsApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_allocation**](AllocationsApi.md#get_allocation) | **GET** /api/allocations/{scope}/{code} | [EXPERIMENTAL] Fetch a given allocation.
[**list_allocations**](AllocationsApi.md#list_allocations) | **GET** /api/allocations | [EXPERIMENTAL] Fetch the last pre-AsAt date version of each allocation in scope (does not fetch the entire history).
[**upsert_allocations**](AllocationsApi.md#upsert_allocations) | **POST** /api/allocations | [EXPERIMENTAL] Upsert; update existing allocations with given ids, or create new allocations otherwise.


# **get_allocation**
> Allocation get_allocation(scope, code, as_at=as_at, property_keys=property_keys)

[EXPERIMENTAL] Fetch a given allocation.

### Example

* OAuth Authentication (oauth2):
```python
from __future__ import print_function
import time
import lusid
from lusid.rest import ApiException
from pprint import pprint
configuration = lusid.Configuration()
# Configure OAuth2 access token for authorization: oauth2
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# Defining host is optional and default to http://localhost/api
configuration.host = "http://localhost/api"
# Create an instance of the API class
api_instance = lusid.AllocationsApi(lusid.ApiClient(configuration))
scope = 'scope_example' # str | The scope to which the allocation belongs.
code = 'code_example' # str | The allocation's unique identifier.
as_at = '2013-10-20T19:20:30+01:00' # datetime | The asAt datetime at which to retrieve the allocation. Defaults to return the latest version of the allocation if not specified. (optional)
property_keys = ['property_keys_example'] # list[str] | A list of property keys from the \"Allocations\" domain to decorate onto the allocation.              These take the format {domain}/{scope}/{code} e.g. \"Allocations/system/Name\". (optional)

try:
    # [EXPERIMENTAL] Fetch a given allocation.
    api_response = api_instance.get_allocation(scope, code, as_at=as_at, property_keys=property_keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AllocationsApi->get_allocation: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **scope** | **str**| The scope to which the allocation belongs. | 
 **code** | **str**| The allocation&#39;s unique identifier. | 
 **as_at** | **datetime**| The asAt datetime at which to retrieve the allocation. Defaults to return the latest version of the allocation if not specified. | [optional] 
 **property_keys** | [**list[str]**](str.md)| A list of property keys from the \&quot;Allocations\&quot; domain to decorate onto the allocation.              These take the format {domain}/{scope}/{code} e.g. \&quot;Allocations/system/Name\&quot;. | [optional] 

### Return type

[**Allocation**](Allocation.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The allocation matching the given identifier. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_allocations**
> PagedResourceListOfAllocation list_allocations(as_at=as_at, page=page, sort_by=sort_by, start=start, limit=limit, filter=filter, property_keys=property_keys)

[EXPERIMENTAL] Fetch the last pre-AsAt date version of each allocation in scope (does not fetch the entire history).

### Example

* OAuth Authentication (oauth2):
```python
from __future__ import print_function
import time
import lusid
from lusid.rest import ApiException
from pprint import pprint
configuration = lusid.Configuration()
# Configure OAuth2 access token for authorization: oauth2
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# Defining host is optional and default to http://localhost/api
configuration.host = "http://localhost/api"
# Create an instance of the API class
api_instance = lusid.AllocationsApi(lusid.ApiClient(configuration))
as_at = '2013-10-20T19:20:30+01:00' # datetime | The asAt datetime at which to retrieve the allocation. Defaults to return the latest version of the allocation if not specified. (optional)
page = 'page_example' # str | The pagination token to use to continue listing allocations from a previous call to list allocations.              This value is returned from the previous call. If a pagination token is provided the sortBy, filter, effectiveAt, and asAt fields              must not have changed since the original request. Also, if set, a start value cannot be provided. (optional)
sort_by = ['sort_by_example'] # list[str] | Allocation the results by these fields. Use use the '-' sign to denote descending allocation e.g. -MyFieldName. (optional)
start = 56 # int | When paginating, skip this number of results. (optional)
limit = 56 # int | When paginating, limit the number of returned results to this many. (optional)
filter = 'filter_example' # str | Expression to filter the result set.  Currently Allocations can be filtered by Id (e.g.              \"Id eq 'ALLOC001'), Allocated Order Id (e.g. AllocatedOrderId eq 'ORD001'), Quantity (e.g. \"Quantity lt 100\"),              LUSID Instrument Id (e.g. \"LusidInstrumentId eq 'LUID_12345678'\") or by Property (Read more about filtering results from LUSID here:              https://support.lusid.com/filtering-results-from-lusid). (optional)
property_keys = ['property_keys_example'] # list[str] | A list of property keys from the \"Allocations\" domain to decorate onto each allocation.                  These take the format {domain}/{scope}/{code} e.g. \"Allocations/system/Name\". (optional)

try:
    # [EXPERIMENTAL] Fetch the last pre-AsAt date version of each allocation in scope (does not fetch the entire history).
    api_response = api_instance.list_allocations(as_at=as_at, page=page, sort_by=sort_by, start=start, limit=limit, filter=filter, property_keys=property_keys)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AllocationsApi->list_allocations: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **as_at** | **datetime**| The asAt datetime at which to retrieve the allocation. Defaults to return the latest version of the allocation if not specified. | [optional] 
 **page** | **str**| The pagination token to use to continue listing allocations from a previous call to list allocations.              This value is returned from the previous call. If a pagination token is provided the sortBy, filter, effectiveAt, and asAt fields              must not have changed since the original request. Also, if set, a start value cannot be provided. | [optional] 
 **sort_by** | [**list[str]**](str.md)| Allocation the results by these fields. Use use the &#39;-&#39; sign to denote descending allocation e.g. -MyFieldName. | [optional] 
 **start** | **int**| When paginating, skip this number of results. | [optional] 
 **limit** | **int**| When paginating, limit the number of returned results to this many. | [optional] 
 **filter** | **str**| Expression to filter the result set.  Currently Allocations can be filtered by Id (e.g.              \&quot;Id eq &#39;ALLOC001&#39;), Allocated Order Id (e.g. AllocatedOrderId eq &#39;ORD001&#39;), Quantity (e.g. \&quot;Quantity lt 100\&quot;),              LUSID Instrument Id (e.g. \&quot;LusidInstrumentId eq &#39;LUID_12345678&#39;\&quot;) or by Property (Read more about filtering results from LUSID here:              https://support.lusid.com/filtering-results-from-lusid). | [optional] 
 **property_keys** | [**list[str]**](str.md)| A list of property keys from the \&quot;Allocations\&quot; domain to decorate onto each allocation.                  These take the format {domain}/{scope}/{code} e.g. \&quot;Allocations/system/Name\&quot;. | [optional] 

### Return type

[**PagedResourceListOfAllocation**](PagedResourceListOfAllocation.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Allocations in scope. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_allocations**
> ResourceListOfAllocation upsert_allocations(request=request)

[EXPERIMENTAL] Upsert; update existing allocations with given ids, or create new allocations otherwise.

### Example

* OAuth Authentication (oauth2):
```python
from __future__ import print_function
import time
import lusid
from lusid.rest import ApiException
from pprint import pprint
configuration = lusid.Configuration()
# Configure OAuth2 access token for authorization: oauth2
configuration.access_token = 'YOUR_ACCESS_TOKEN'

# Defining host is optional and default to http://localhost/api
configuration.host = "http://localhost/api"
# Create an instance of the API class
api_instance = lusid.AllocationsApi(lusid.ApiClient(configuration))
request = lusid.AllocationSetRequest() # AllocationSetRequest | The collection of allocation requests. (optional)

try:
    # [EXPERIMENTAL] Upsert; update existing allocations with given ids, or create new allocations otherwise.
    api_response = api_instance.upsert_allocations(request=request)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling AllocationsApi->upsert_allocations: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**AllocationSetRequest**](AllocationSetRequest.md)| The collection of allocation requests. | [optional] 

### Return type

[**ResourceListOfAllocation**](ResourceListOfAllocation.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | A collection of allocations. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

