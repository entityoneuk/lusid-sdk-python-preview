# lusid.PersonsApi

All URIs are relative to *http://localhost/api*

Method | HTTP request | Description
------------- | ------------- | -------------
[**delete_person**](PersonsApi.md#delete_person) | **DELETE** /api/persons/{idTypeScope}/{idTypeCode}/{code} | [EXPERIMENTAL] Delete person
[**delete_person_access_metadata**](PersonsApi.md#delete_person_access_metadata) | **DELETE** /api/persons/{idTypeScope}/{idTypeCode}/{code}/metadata/{metadataKey} | [EXPERIMENTAL] Delete a Person Access Metadata entry
[**get_all_person_access_metadata**](PersonsApi.md#get_all_person_access_metadata) | **GET** /api/persons/{idTypeScope}/{idTypeCode}/{code}/metadata | [EXPERIMENTAL] Get Access Metadata rules for a Person
[**get_person**](PersonsApi.md#get_person) | **GET** /api/persons/{idTypeScope}/{idTypeCode}/{code} | [EXPERIMENTAL] Get Person
[**get_person_access_metadata_by_key**](PersonsApi.md#get_person_access_metadata_by_key) | **GET** /api/persons/{idTypeScope}/{idTypeCode}/{code}/metadata/{metadataKey} | [EXPERIMENTAL] Get an entry identified by a metadataKey in the Access Metadata of a Person
[**upsert_person**](PersonsApi.md#upsert_person) | **POST** /api/persons | [EXPERIMENTAL] Upsert Person
[**upsert_person_access_metadata**](PersonsApi.md#upsert_person_access_metadata) | **PUT** /api/persons/{idTypeScope}/{idTypeCode}/{code}/metadata/{metadataKey} | [EXPERIMENTAL] Upsert a Person Access Metadata entry associated with a specific metadataKey. This creates or updates the data in LUSID.


# **delete_person**
> DeletedEntityResponse delete_person(id_type_scope, id_type_code, code)

[EXPERIMENTAL] Delete person

Delete a person. Deletion will be valid from the person's creation datetime.  This means that the person will no longer exist at any effective datetime from the asAt datetime of deletion.

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
api_instance = lusid.PersonsApi(lusid.ApiClient(configuration))
id_type_scope = 'id_type_scope_example' # str | The scope of the person identifier type.
id_type_code = 'id_type_code_example' # str | The code of the person identifier type.
code = 'code_example' # str | Code of the person under specified identifier type scope and code. This together with defined              identifier type uniquely identifies the person to delete.

try:
    # [EXPERIMENTAL] Delete person
    api_response = api_instance.delete_person(id_type_scope, id_type_code, code)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PersonsApi->delete_person: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id_type_scope** | **str**| The scope of the person identifier type. | 
 **id_type_code** | **str**| The code of the person identifier type. | 
 **code** | **str**| Code of the person under specified identifier type scope and code. This together with defined              identifier type uniquely identifies the person to delete. | 

### Return type

[**DeletedEntityResponse**](DeletedEntityResponse.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The response from deleting person. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_person_access_metadata**
> DeletedEntityResponse delete_person_access_metadata(id_type_scope, id_type_code, code, metadata_key, effective_at=effective_at)

[EXPERIMENTAL] Delete a Person Access Metadata entry

Deletes the Person Access Metadata entry that exactly matches the provided identifier parts.    It is important to always check to verify success (or failure).

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
api_instance = lusid.PersonsApi(lusid.ApiClient(configuration))
id_type_scope = 'id_type_scope_example' # str | Scope of the person identifier.
id_type_code = 'id_type_code_example' # str | Code of the person identifier.
code = 'code_example' # str | Code of the person under specified identifier type's scope and code.
metadata_key = 'metadata_key_example' # str | Key of the metadata entry to retrieve
effective_at = 'effective_at_example' # str | The effective date to delete at, if this is not supplied, it will delete all data found (optional)

try:
    # [EXPERIMENTAL] Delete a Person Access Metadata entry
    api_response = api_instance.delete_person_access_metadata(id_type_scope, id_type_code, code, metadata_key, effective_at=effective_at)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PersonsApi->delete_person_access_metadata: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id_type_scope** | **str**| Scope of the person identifier. | 
 **id_type_code** | **str**| Code of the person identifier. | 
 **code** | **str**| Code of the person under specified identifier type&#39;s scope and code. | 
 **metadata_key** | **str**| Key of the metadata entry to retrieve | 
 **effective_at** | **str**| The effective date to delete at, if this is not supplied, it will delete all data found | [optional] 

### Return type

[**DeletedEntityResponse**](DeletedEntityResponse.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The Access Metadata with the given metadataKey has been deleted |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_all_person_access_metadata**
> dict(str, list[AccessMetadataValue]) get_all_person_access_metadata(id_type_scope, id_type_code, code, effective_at=effective_at, as_at=as_at)

[EXPERIMENTAL] Get Access Metadata rules for a Person

Pass the Scope and Code of the Person identifier along with the person code parameter to retrieve the associated Access Metadata

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
api_instance = lusid.PersonsApi(lusid.ApiClient(configuration))
id_type_scope = 'id_type_scope_example' # str | Scope of the person identifier.
id_type_code = 'id_type_code_example' # str | Code of the person identifier.
code = 'code_example' # str | Code of the person under specified identifier type's scope and code.
effective_at = 'effective_at_example' # str | The effectiveAt datetime at which to retrieve the Access Metadata (optional)
as_at = '2013-10-20T19:20:30+01:00' # datetime | The asAt datetime at which to retrieve the Access Metadata (optional)

try:
    # [EXPERIMENTAL] Get Access Metadata rules for a Person
    api_response = api_instance.get_all_person_access_metadata(id_type_scope, id_type_code, code, effective_at=effective_at, as_at=as_at)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PersonsApi->get_all_person_access_metadata: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id_type_scope** | **str**| Scope of the person identifier. | 
 **id_type_code** | **str**| Code of the person identifier. | 
 **code** | **str**| Code of the person under specified identifier type&#39;s scope and code. | 
 **effective_at** | **str**| The effectiveAt datetime at which to retrieve the Access Metadata | [optional] 
 **as_at** | **datetime**| The asAt datetime at which to retrieve the Access Metadata | [optional] 

### Return type

**dict(str, list[AccessMetadataValue])**

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The access metadata for the Person or any failure. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_person**
> Person get_person(id_type_scope, id_type_code, code, property_keys=property_keys, effective_at=effective_at, as_at=as_at)

[EXPERIMENTAL] Get Person

Retrieve the definition of a person.

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
api_instance = lusid.PersonsApi(lusid.ApiClient(configuration))
id_type_scope = 'id_type_scope_example' # str | Scope of the person identifier.
id_type_code = 'id_type_code_example' # str | Code of the person identifier.
code = 'code_example' # str | Code of the person under specified scope and code. This together with stated identifier type uniquely              identifies the person.
property_keys = ['property_keys_example'] # list[str] | A list of property keys from the \"Person\" domain to decorate onto each person.              These take the format {domain}/{scope}/{code} e.g. \"Person/ContactDetails/Address\". Defaults to include all properties if not specified. (optional)
effective_at = 'effective_at_example' # str | The effective datetime or cut label at which to retrieve the person. Defaults to the current LUSID system datetime if not specified. (optional)
as_at = '2013-10-20T19:20:30+01:00' # datetime | The asAt datetime at which to retrieve the person. Defaults to return the latest version of the person if not specified. (optional)

try:
    # [EXPERIMENTAL] Get Person
    api_response = api_instance.get_person(id_type_scope, id_type_code, code, property_keys=property_keys, effective_at=effective_at, as_at=as_at)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PersonsApi->get_person: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id_type_scope** | **str**| Scope of the person identifier. | 
 **id_type_code** | **str**| Code of the person identifier. | 
 **code** | **str**| Code of the person under specified scope and code. This together with stated identifier type uniquely              identifies the person. | 
 **property_keys** | [**list[str]**](str.md)| A list of property keys from the \&quot;Person\&quot; domain to decorate onto each person.              These take the format {domain}/{scope}/{code} e.g. \&quot;Person/ContactDetails/Address\&quot;. Defaults to include all properties if not specified. | [optional] 
 **effective_at** | **str**| The effective datetime or cut label at which to retrieve the person. Defaults to the current LUSID system datetime if not specified. | [optional] 
 **as_at** | **datetime**| The asAt datetime at which to retrieve the person. Defaults to return the latest version of the person if not specified. | [optional] 

### Return type

[**Person**](Person.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The requested person definition |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_person_access_metadata_by_key**
> list[AccessMetadataValue] get_person_access_metadata_by_key(id_type_scope, id_type_code, code, metadata_key, effective_at=effective_at, as_at=as_at)

[EXPERIMENTAL] Get an entry identified by a metadataKey in the Access Metadata of a Person

Get a specific Person Access Metadata by specifying the corresponding identifier parts and Person code                No matching will be performed through this endpoint. To retrieve an entry, it is necessary to specify, exactly, the identifier of the entry

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
api_instance = lusid.PersonsApi(lusid.ApiClient(configuration))
id_type_scope = 'id_type_scope_example' # str | Scope of the person identifier.
id_type_code = 'id_type_code_example' # str | Code of the person identifier.
code = 'code_example' # str | Code of the person under specified identifier type's scope and code.
metadata_key = 'metadata_key_example' # str | Key of the metadata entry to retrieve
effective_at = 'effective_at_example' # str | The effectiveAt datetime at which to retrieve the Access Metadata (optional)
as_at = '2013-10-20T19:20:30+01:00' # datetime | The asAt datetime at which to retrieve the Access Metadata (optional)

try:
    # [EXPERIMENTAL] Get an entry identified by a metadataKey in the Access Metadata of a Person
    api_response = api_instance.get_person_access_metadata_by_key(id_type_scope, id_type_code, code, metadata_key, effective_at=effective_at, as_at=as_at)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PersonsApi->get_person_access_metadata_by_key: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id_type_scope** | **str**| Scope of the person identifier. | 
 **id_type_code** | **str**| Code of the person identifier. | 
 **code** | **str**| Code of the person under specified identifier type&#39;s scope and code. | 
 **metadata_key** | **str**| Key of the metadata entry to retrieve | 
 **effective_at** | **str**| The effectiveAt datetime at which to retrieve the Access Metadata | [optional] 
 **as_at** | **datetime**| The asAt datetime at which to retrieve the Access Metadata | [optional] 

### Return type

[**list[AccessMetadataValue]**](AccessMetadataValue.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The successfully retrieved Person access metadata filtered by metadataKey or any failure. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_person**
> Person upsert_person(request=request)

[EXPERIMENTAL] Upsert Person

Create or update new person under specified scope

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
api_instance = lusid.PersonsApi(lusid.ApiClient(configuration))
request = lusid.UpsertPersonRequest() # UpsertPersonRequest | Request to create or update a person. (optional)

try:
    # [EXPERIMENTAL] Upsert Person
    api_response = api_instance.upsert_person(request=request)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PersonsApi->upsert_person: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **request** | [**UpsertPersonRequest**](UpsertPersonRequest.md)| Request to create or update a person. | [optional] 

### Return type

[**Person**](Person.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | The newly created or updated person |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **upsert_person_access_metadata**
> ResourceListOfAccessMetadataValueOf upsert_person_access_metadata(id_type_scope, id_type_code, code, metadata_key, request, effective_at=effective_at)

[EXPERIMENTAL] Upsert a Person Access Metadata entry associated with a specific metadataKey. This creates or updates the data in LUSID.

Update or insert one Person Access Metadata entry in a single scope. An item will be updated if it already exists  and inserted if it does not.                The response will return the successfully updated or inserted Person Access Metadata rule or failure message if unsuccessful.                It is important to always check to verify success (or failure).                Multiple rules for a metadataKey can exist with different effective at dates, when resources are accessed the rule that is active for the current time will be fetched.

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
api_instance = lusid.PersonsApi(lusid.ApiClient(configuration))
id_type_scope = 'id_type_scope_example' # str | Scope of the person identifier.
id_type_code = 'id_type_code_example' # str | Code of the person identifier.
code = 'code_example' # str | Code of the person under specified identifier type's scope and code.
metadata_key = 'metadata_key_example' # str | Key of the metadata entry to retrieve
request = lusid.UpsertPersonAccessMetadataRequest() # UpsertPersonAccessMetadataRequest | The Person Access Metadata entry to upsert
effective_at = 'effective_at_example' # str | The effectiveAt datetime at which to upsert the Access Metadata (optional)

try:
    # [EXPERIMENTAL] Upsert a Person Access Metadata entry associated with a specific metadataKey. This creates or updates the data in LUSID.
    api_response = api_instance.upsert_person_access_metadata(id_type_scope, id_type_code, code, metadata_key, request, effective_at=effective_at)
    pprint(api_response)
except ApiException as e:
    print("Exception when calling PersonsApi->upsert_person_access_metadata: %s\n" % e)
```

### Parameters

Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **id_type_scope** | **str**| Scope of the person identifier. | 
 **id_type_code** | **str**| Code of the person identifier. | 
 **code** | **str**| Code of the person under specified identifier type&#39;s scope and code. | 
 **metadata_key** | **str**| Key of the metadata entry to retrieve | 
 **request** | [**UpsertPersonAccessMetadataRequest**](UpsertPersonAccessMetadataRequest.md)| The Person Access Metadata entry to upsert | 
 **effective_at** | **str**| The effectiveAt datetime at which to upsert the Access Metadata | [optional] 

### Return type

[**ResourceListOfAccessMetadataValueOf**](ResourceListOfAccessMetadataValueOf.md)

### Authorization

[oauth2](../README.md#oauth2)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: text/plain, application/json, text/json

### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | The successfully updated or inserted item or any failure. |  -  |
**400** | The details of the input related failure |  -  |
**0** | Error response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

