"""
Microsoft Business Central Dynamics 365 Integration

Provides integration with D&S ERP system for:
- Customer data and discount groups
- Product catalog and pricing
- Inventory/stock levels
- Quote creation and management

Supports both Basic Auth (primary) and OAuth token authentication.
Uses OData V4 API endpoints matching the pattern from tasks.py.
"""
import httpx
import requests
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio
from functools import lru_cache
from requests.auth import HTTPBasicAuth

from app.core.config import settings


@dataclass
class BCToken:
    """Azure AD access token for Business Central."""
    access_token: str
    expires_at: datetime
    
    @property
    def is_valid(self) -> bool:
        return datetime.utcnow() < self.expires_at - timedelta(minutes=5)


class BusinessCentralClient:
    """
    Client for Microsoft Business Central REST API.
    
    Handles authentication and provides methods for:
    - Customer lookup (from Customer_Card entity)
    - Product/Item queries (from Items/Item entities)
    - Price list retrieval
    - Quote creation
    
    Supports both Basic Auth (primary) and OAuth token authentication.
    Uses OData V4 API matching the pattern: https://bctest.dayliff.com:7048/BC160/ODataV4/Company('{country}')
    """
    
    def __init__(self, country: str = "KENYA"):
        """
        Initialize Business Central client.
        
        Args:
            country: Company/country code (e.g., 'KENYA', 'UGANDA', 'TANZANIA')
        """
        self.country = country
        self.tenant_id = settings.BC_TENANT_ID
        self.client_id = settings.BC_CLIENT_ID
        self.client_secret = settings.BC_CLIENT_SECRET
        self.base_url = settings.BC_BASE_URL
        self.environment = settings.BC_ENVIRONMENT
        self.company_id = settings.BC_COMPANY_ID
        
        # Basic Auth credentials (primary method)
        self.username = settings.BC_USERNAME
        self.password = settings.BC_PASSWORD
        
        # OAuth token (fallback method)
        self._token: Optional[BCToken] = None
        self._http_client: Optional[httpx.AsyncClient] = None
        self._sync_client: Optional[requests.Session] = None
    
    def get_base_url(self) -> str:
        """
        Get the base URL for Business Central OData API.
        
        Pattern (matching tasks.py): https://bc.dayliff.com:7048/BC160/ODataV4/Company('{country}')
        
        Examples:
        - Kenya: https://bc.dayliff.com:7048/BC160/ODataV4/Company('KENYA')
        - Uganda: https://bc.dayliff.com:7048/BC160/ODataV4/Company('UGANDA')
        - Tanzania: https://bc.dayliff.com:7048/BC160/ODataV4/Company('TANZANIA')
        
        Falls back to BC_URL if set, otherwise constructs from BC_BASE_URL.
        """
        if settings.BC_URL:
            # Use explicit URL if provided (matches tasks.py pattern)
            # Replace {country} placeholder if present
            url = settings.BC_URL.rstrip('/')
            if '{country}' in url or "'{country}'" in url:
                url = url.replace("'{country}'", f"'{self.country}'").replace("{country}", self.country)
            return url
        
        # Construct URL from base URL pattern
        # Default pattern: https://bc.dayliff.com:7048/BC160/ODataV4/Company('{country}')
        if "bc.dayliff.com" in (settings.BC_BASE_URL or ""):
            return f"https://bc.dayliff.com:7048/BC160/ODataV4/Company('{self.country}')"
        
        # Fallback to standard BC API URL (OAuth method)
        return f"{self.base_url}/{self.tenant_id}/{self.environment}/api/v2.0/companies({self.company_id})"
    
    def _get_sync_client(self) -> requests.Session:
        """Get or create synchronous HTTP client for Basic Auth requests."""
        if self._sync_client is None:
            self._sync_client = requests.Session()
        return self._sync_client
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = httpx.AsyncClient(timeout=30.0)
        return self._http_client
    
    async def _get_access_token(self) -> str:
        """
        Get Azure AD access token using client credentials flow.
        """
        if self._token and self._token.is_valid:
            return self._token.access_token
        
        token_url = f"https://login.microsoftonline.com/{self.tenant_id}/oauth2/v2.0/token"
        
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": "https://api.businesscentral.dynamics.com/.default"
        }
        
        client = await self._get_http_client()
        response = await client.post(token_url, data=data)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get access token: {response.text}")
        
        token_data = response.json()
        
        self._token = BCToken(
            access_token=token_data["access_token"],
            expires_at=datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
        )
        
        return self._token.access_token
    
    def _make_sync_request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None,
        use_basic_auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make synchronous authenticated request to Business Central API.
        
        Uses Basic Auth by default (matching tasks.py pattern).
        Falls back to OAuth if Basic Auth credentials are not available.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint (e.g., "Customer_Card", "Items")
            data: Request body data (for POST/PATCH)
            params: Query parameters (OData filters, selects, etc.)
            use_basic_auth: Whether to use Basic Auth (default True)
        
        Returns:
            JSON response data
        """
        base_url = self.get_base_url()
        url = f"{base_url}/{endpoint}"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        # Use Basic Auth if credentials are available (primary method)
        if use_basic_auth and self.username and self.password:
            auth = HTTPBasicAuth(self.username, self.password)
            client = self._get_sync_client()
        else:
            # Fallback to OAuth token (async, but we'll handle it)
            # For now, raise error if Basic Auth not available
            if not self.username or not self.password:
                raise ValueError("BC_USERNAME and BC_PASSWORD must be set for Basic Auth")
            auth = HTTPBasicAuth(self.username, self.password)
            client = self._get_sync_client()
        
        try:
            if method == "GET":
                response = client.get(url, headers=headers, params=params, auth=auth, timeout=30)
            elif method == "POST":
                response = client.post(url, headers=headers, json=data, auth=auth, timeout=30)
            elif method == "PATCH":
                response = client.patch(url, headers=headers, json=data, auth=auth, timeout=30)
            elif method == "DELETE":
                response = client.delete(url, headers=headers, auth=auth, timeout=30)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
            
            return response.json()
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as conn_error:
            # Handle connection errors specifically
            error_msg = f"Business Central connection error: {str(conn_error)}"
            # Re-raise as ConnectionError for upstream handling
            raise ConnectionError(error_msg) from conn_error
        except requests.exceptions.Timeout as timeout_error:
            raise TimeoutError(f"Business Central request timeout: {str(timeout_error)}") from timeout_error
        except requests.exceptions.RequestException as e:
            error_msg = f"BC API Error: {method} {url}"
            if hasattr(e, 'response') and e.response is not None:
                error_msg += f" - Status {e.response.status_code}: {e.response.text}"
            else:
                error_msg += f" - {str(e)}"
            raise Exception(error_msg)
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Dict = None,
        params: Dict = None,
        use_basic_auth: bool = True
    ) -> Dict[str, Any]:
        """
        Make asynchronous authenticated request to Business Central API.
        
        Prefers Basic Auth (matching tasks.py pattern) but supports OAuth fallback.
        """
        # For async, we can use Basic Auth with httpx
        if use_basic_auth and self.username and self.password:
            base_url = self.get_base_url()
            url = f"{base_url}/{endpoint}"
            
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            
            client = await self._get_http_client()
            
            # httpx supports Basic Auth
            auth = (self.username, self.password)
            
            try:
                if method == "GET":
                    response = await client.get(url, headers=headers, params=params, auth=auth)
                elif method == "POST":
                    response = await client.post(url, headers=headers, json=data, auth=auth)
                elif method == "PATCH":
                    response = await client.patch(url, headers=headers, json=data, auth=auth)
                elif method == "DELETE":
                    response = await client.delete(url, headers=headers, auth=auth)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                if response.status_code >= 400:
                    raise Exception(f"BC API Error: {response.status_code} - {response.text}")
                
                if response.status_code == 204:
                    return {}
                
                return response.json()
            except httpx.HTTPStatusError as e:
                raise Exception(f"BC API Error: {e.response.status_code} - {e.response.text}")
        else:
            # Fallback to OAuth token method
            token = await self._get_access_token()
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            url = f"{self.get_base_url()}/{endpoint}"
            client = await self._get_http_client()
            
            if method == "GET":
                response = await client.get(url, headers=headers, params=params)
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            if response.status_code >= 400:
                raise Exception(f"BC API Error: {response.status_code} - {response.text}")
            
            if response.status_code == 204:
                return {}
            
            return response.json()
    
    # =========================================================================
    # CUSTOMER OPERATIONS (matching tasks.py pattern)
    # =========================================================================
    
    def get_customer_card(self, customer_no: str, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get customer details from Customer_Card entity (matching tasks.py pattern).
        
        Args:
            customer_no: Customer number (e.g., 'C00123')
            fields: Optional list of fields to select (e.g., ['Phone_No', 'Name', 'Customer_Discount_Group'])
        
        Returns:
            Customer record or None if not found
        """
        params = {"$filter": f"No eq '{customer_no}'"}
        
        if fields:
            params["$select"] = ",".join(fields)
        
        try:
            result = self._make_sync_request("GET", "Customer_Card", params=params)
            customers = result.get("value", [])
            return customers[0] if customers else None
        except Exception as e:
            print(f"Error fetching customer {customer_no}: {e}")
            return None
    
    def get_customer_phone(self, customer_no: str) -> Optional[str]:
        """
        Get customer phone number from Customer_Card (matching tasks.py pattern).
        
        Args:
            customer_no: Customer number
        
        Returns:
            Phone number or None
        """
        customer = self.get_customer_card(customer_no, fields=["Phone_No"])
        return customer.get("Phone_No") if customer else None
    
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer details by ID (async version).
        
        Args:
            customer_id: Business Central customer ID
        
        Returns:
            Customer record with pricing group and credit info
        """
        # Try Customer_Card first (matching tasks.py pattern)
        customer = self.get_customer_card(customer_id)
        if customer:
            return customer
        
        # Fallback to standard customers endpoint
        return await self._make_request("GET", f"customers({customer_id})", use_basic_auth=False)
    
    def search_customers(
        self,
        search_term: str,
        search_by: str = "name",  # "name", "no", "phone", or "all"
        max_results: int = 10,
        exact_match: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Search customers by name, number, or phone.
        
        Args:
            search_term: Search string
            search_by: Search field - "name", "no", "phone", or "all"
            max_results: Maximum results to return
            exact_match: If True, use exact match (eq) instead of contains
        
        Returns:
            List of matching customers from Customer_Card entity
        """
        # Escape single quotes in search term for OData
        escaped_term = search_term.replace("'", "''")
        
        # Build filter based on search_by parameter
        if search_by == "name":
            if exact_match:
                filter_param = f"Name eq '{escaped_term}'"
            else:
                filter_param = f"contains(Name,'{escaped_term}')"
        elif search_by == "no":
            if exact_match:
                filter_param = f"No eq '{escaped_term}'"
            else:
                filter_param = f"contains(No,'{escaped_term}')"
        elif search_by == "phone":
            filter_param = f"contains(Phone_No,'{escaped_term}')"
        else:  # "all"
            # Search across name, number, and phone
            filter_param = (
                f"contains(Name,'{escaped_term}') or "
                f"contains(No,'{escaped_term}') or "
                f"contains(Phone_No,'{escaped_term}')"
            )
        
        params = {
            "$filter": filter_param,
            "$top": max_results
        }
        
        try:
            # Use Customer_Card entity (matching the ERP structure)
            result = self._make_sync_request("GET", "Customer_Card", params=params)
            return result.get("value", [])
        except (ConnectionError, OSError, TimeoutError) as conn_error:
            # Connection errors - ERP not reachable
            # Re-raise to let caller handle appropriately
            raise
        except Exception as e:
            # Other errors - log and return empty list
            print(f"Error searching customers: {e}")
            return []
    
    async def get_customer_price_group(self, customer_id: str) -> Dict[str, Any]:
        """
        Get customer's assigned price group and discount group.
        
        Args:
            customer_id: Customer number
        
        Returns:
            Customer pricing information
        """
        # Use Customer_Card entity (matching tasks.py pattern)
        customer = self.get_customer_card(
            customer_id,
            fields=["No", "Name", "Customer_Price_Group", "Customer_Discount_Group", "Payment_Terms_Code", "Credit_Limit"]
        )
        
        if customer:
            return {
                "customer_id": customer.get("No"),
                "customer_name": customer.get("Name"),
                "price_group": customer.get("Customer_Price_Group"),
                "discount_group": customer.get("Customer_Discount_Group"),
                "payment_terms": customer.get("Payment_Terms_Code"),
                "credit_limit": customer.get("Credit_Limit")
            }
        
        # Fallback to async method
        customer = await self.get_customer(customer_id)
        return {
            "customer_id": customer_id,
            "customer_name": customer.get("displayName") or customer.get("Name"),
            "price_group": customer.get("customerPriceGroup") or customer.get("Customer_Price_Group"),
            "discount_group": customer.get("customerDiscountGroup") or customer.get("Customer_Discount_Group"),
            "payment_terms": customer.get("paymentTermsCode") or customer.get("Payment_Terms_Code"),
            "credit_limit": customer.get("creditLimit") or customer.get("Credit_Limit")
        }
    
    # =========================================================================
    # ITEM/PRODUCT OPERATIONS (matching tasks.py pattern)
    # =========================================================================
    
    def get_item_sync(self, item_number: str, fields: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """
        Get item/product details by number (synchronous, matching tasks.py pattern).
        
        Args:
            item_number: Item number (SKU)
            fields: Optional list of fields to select
        
        Returns:
            Item record or None if not found
        """
        params = {"$filter": f"No eq '{item_number}'"}
        
        if fields:
            params["$select"] = ",".join(fields)
        
        try:
            result = self._make_sync_request("GET", "ItemsAPI", params=params)
            items = result.get("value", [])
            return items[0] if items else None
        except Exception as e:
            print(f"Error fetching item {item_number}: {e}")
            return None
    
    async def get_item(self, item_number: str) -> Optional[Dict[str, Any]]:
        """
        Get item/product details by number (async version).
        
        Args:
            item_number: Item number (SKU)
        
        Returns:
            Item record with pricing and inventory
        """
        # Try Items entity first (matching tasks.py pattern)
        item = self.get_item_sync(item_number)
        if item:
            return item
        
        # Fallback to standard items endpoint
        params = {"$filter": f"number eq '{item_number}'"}
        result = await self._make_request("GET", "items", params=params, use_basic_auth=False)
        items = result.get("value", [])
        return items[0] if items else None
    
    def search_items_sync(
        self,
        search_term: str,
        category: str = None,
        max_results: int = 20,
        fields: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search items by description or number (synchronous, matching tasks.py pattern).
        
        Args:
            search_term: Search string
            category: Optional category filter
            max_results: Maximum results
            fields: Optional list of fields to select
        
        Returns:
            List of matching items
        """
        filter_parts = [
            f"(contains(Description,'{search_term}') or contains(No,'{search_term}'))"
        ]
        
        if category:
            filter_parts.append(f"Item_Category_Code eq '{category}'")
        
        params = {
            "$filter": " and ".join(filter_parts),
            "$top": max_results
        }
        
        if fields:
            params["$select"] = ",".join(fields)
        
        try:
            result = self._make_sync_request("GET", "ItemsAPI", params=params)
            return result.get("value", [])
        except Exception as e:
            print(f"Error searching items: {e}")
            return []
    
    async def search_items(
        self,
        search_term: str,
        category: str = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search items by description or number (async version).
        
        Args:
            search_term: Search string
            category: Optional category filter
            max_results: Maximum results
        
        Returns:
            List of matching items
        """
        # Try Items entity first (matching tasks.py pattern)
        items = self.search_items_sync(search_term, category, max_results)
        if items:
            return items
        
        # Fallback to standard items endpoint
        filter_parts = [
            f"(contains(displayName,'{search_term}') or contains(number,'{search_term}'))"
        ]
        
        if category:
            filter_parts.append(f"itemCategoryCode eq '{category}'")
        
        params = {
            "$filter": " and ".join(filter_parts),
            "$top": max_results
        }
        
        result = await self._make_request("GET", "items", params=params, use_basic_auth=False)
        return result.get("value", [])
    
    def get_item_price_sync(
        self,
        item_number: str,
        customer_price_group: str = None,
        quantity: float = 1
    ) -> Dict[str, Any]:
        """
        Get item price including any special pricing (synchronous, matching tasks.py pattern).
        
        Args:
            item_number: Item number
            customer_price_group: Customer's price group for special pricing
            quantity: Quantity for volume pricing
        
        Returns:
            Price information
        """
        # ItemsAPI does not expose Unit_of_Measure_Code; request only fields that exist
        item = self.get_item_sync(
            item_number,
            fields=["No", "Description", "Unit_Price", "Inventory"]
        )
        
        if not item:
            return {"error": f"Item {item_number} not found"}
        
        base_price = item.get("Unit_Price") or item.get("unitPrice", 0)
        
        # Check for special prices
        special_price = base_price
        if customer_price_group:
            # Query sales prices for this item and price group
            params = {
                "$filter": f"Item_No eq '{item_number}' and Sales_Code eq '{customer_price_group}'"
            }
            try:
                prices_result = self._make_sync_request("GET", "Sales_Prices", params=params)
                prices = prices_result.get("value", [])
                if prices:
                    # Find applicable price based on quantity
                    for price in sorted(prices, key=lambda p: p.get("Minimum_Quantity", 0) or 0, reverse=True):
                        min_qty = price.get("Minimum_Quantity", 0) or 0
                        if quantity >= min_qty:
                            special_price = price.get("Unit_Price", base_price) or base_price
                            break
            except Exception:
                pass  # Fall back to base price
        
        return {
            "item_number": item_number,
            "description": item.get("Description") or item.get("displayName"),
            "unit_of_measure": item.get("Unit_of_Measure_Code") or item.get("unitOfMeasureCode") or "",
            "base_price": base_price,
            "special_price": special_price,
            "currency": "KES",
            "inventory": item.get("Inventory", 0) or item.get("inventory", 0)
        }
    
    async def get_item_price(
        self,
        item_number: str,
        customer_price_group: str = None,
        quantity: float = 1
    ) -> Dict[str, Any]:
        """
        Get item price including any special pricing (async version).
        
        Args:
            item_number: Item number
            customer_price_group: Customer's price group for special pricing
            quantity: Quantity for volume pricing
        
        Returns:
            Price information
        """
        # Use synchronous method (matching tasks.py pattern)
        return self.get_item_price_sync(item_number, customer_price_group, quantity)
    
    def get_item_inventory_sync(self, item_number: str) -> Dict[str, Any]:
        """
        Get item inventory/stock level (synchronous, matching tasks.py pattern).
        
        Args:
            item_number: Item number
        
        Returns:
            Inventory information
        """
        # ItemsAPI does not expose Reserved_Quantity; request only fields that exist
        item = self.get_item_sync(
            item_number,
            fields=["No", "Description", "Inventory"]
        )
        
        if not item:
            return {"error": f"Item {item_number} not found"}
        
        inventory = item.get("Inventory", 0) or item.get("inventory", 0)
        # ItemsAPI does not have Reserved_Quantity; treat as 0
        reserved = item.get("Reserved_Quantity", 0) or item.get("reservedQuantity", 0)
        
        return {
            "item_number": item_number,
            "description": item.get("Description") or item.get("displayName"),
            "inventory": inventory,
            "reserved": reserved,
            "available": inventory - reserved
        }
    
    async def get_item_inventory(self, item_number: str) -> Dict[str, Any]:
        """
        Get item inventory/stock level (async version).
        
        Args:
            item_number: Item number
        
        Returns:
            Inventory information
        """
        # Use synchronous method (matching tasks.py pattern)
        return self.get_item_inventory_sync(item_number)
    
    def get_items_url(self, filters: Optional[Dict[str, str]] = None, select_fields: Optional[List[str]] = None, top: int = 1000, skip: int = 0) -> str:
        """
        Get the full URL for querying items/products from Business Central.
        
        Useful for ensuring products are loaded correctly from Microsoft Business Central.
        
        Args:
            filters: Optional dict of filter conditions (e.g., {"No": "DS*"})
            select_fields: Optional list of fields to select
            top: Maximum number of results (default 1000)
            skip: Number of results to skip (for pagination)
        
        Returns:
            Full OData URL for Items entity
        """
        base_url = self.get_base_url()
        # Use ItemsAPI endpoint (not Items) - matches actual BC OData structure
        url = f"{base_url}/ItemsAPI"
        
        params = []
        
        # Build filter string
        if filters:
            filter_parts = [f"{k} eq '{v}'" for k, v in filters.items()]
            params.append(f"$filter={' and '.join(filter_parts)}")
        
        # Add select
        if select_fields:
            params.append(f"$select={','.join(select_fields)}")
        
        # Add pagination
        if top > 0:
            params.append(f"$top={top}")
        if skip > 0:
            params.append(f"$skip={skip}")
        
        if params:
            url += "?" + "&".join(params)
        
        return url
    
    def fetch_items_paginated(
        self,
        filters: Optional[Dict[str, str]] = None,
        select_fields: Optional[List[str]] = None,
        batch_size: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch all items with pagination support (matching tasks.py pattern).
        
        Args:
            filters: Optional dict of filter conditions
            select_fields: Optional list of fields to select
            batch_size: Number of items per batch (default 1000)
        
        Returns:
            List of all items
        """
        all_items = []
        skip = 0
        has_more = True
        
        while has_more:
            params = {}
            
            if filters:
                filter_parts = [f"{k} eq '{v}'" for k, v in filters.items()]
                params["$filter"] = " and ".join(filter_parts)
            
            if select_fields:
                params["$select"] = ",".join(select_fields)
            
            params["$top"] = batch_size
            params["$skip"] = skip
            
            try:
                result = self._make_sync_request("GET", "ItemsAPI", params=params)
                items = result.get("value", [])
                all_items.extend(items)
                
                # Check if there are more pages
                has_more = "@odata.nextLink" in result
                if has_more:
                    skip += batch_size
                else:
                    has_more = len(items) == batch_size  # Might have more if exactly batch_size returned
                    if has_more:
                        skip += batch_size
            except Exception as e:
                print(f"Error fetching items batch (skip={skip}): {e}")
                break
        
        return all_items
    
    # =========================================================================
    # QUOTE OPERATIONS
    # =========================================================================
    
    async def create_sales_quote(
        self,
        customer_id: str,
        lines: List[Dict[str, Any]],
        external_document_number: str = None
    ) -> Dict[str, Any]:
        """
        Create a sales quote in Business Central.
        
        Args:
            customer_id: Customer ID
            lines: Quote lines with item_number and quantity
            external_document_number: External reference (e.g., AILIFF quote ID)
        
        Returns:
            Created quote details
        """
        # Create quote header
        quote_data = {
            "customerId": customer_id,
            "externalDocumentNumber": external_document_number
        }
        
        quote = await self._make_request("POST", "salesQuotes", data=quote_data)
        quote_id = quote.get("id")
        
        if not quote_id:
            raise Exception("Failed to create quote header")
        
        # Add quote lines
        for line in lines:
            line_data = {
                "documentId": quote_id,
                "sequence": line.get("line_number", 0),
                "itemId": line.get("item_id"),
                "quantity": line.get("quantity", 1),
                "unitPrice": line.get("unit_price")
            }
            
            if line.get("description"):
                line_data["description"] = line.get("description")
            
            await self._make_request("POST", f"salesQuotes({quote_id})/salesQuoteLines", data=line_data)
        
        # Return the complete quote
        return await self.get_sales_quote(quote_id)
    
    async def get_sales_quote(self, quote_id: str) -> Dict[str, Any]:
        """Get sales quote details."""
        quote = await self._make_request("GET", f"salesQuotes({quote_id})")
        
        # Get quote lines
        lines = await self._make_request("GET", f"salesQuotes({quote_id})/salesQuoteLines")
        quote["lines"] = lines.get("value", [])
        
        return quote
    
    def create_sales_quote_sync(
        self,
        customer_no: str,
        lines: List[Dict[str, Any]],
        external_document_number: Optional[str] = None,
        salesperson_code: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create a sales quote in Business Central (synchronous).
        Used by the proposal flow to create sales quote lines in ERP before generating the proposal.

        Args:
            customer_no: Customer number (e.g. '114328')
            lines: Quote lines with bc_item_no (or product_no), product_name, quantity, unit_price
            external_document_number: External reference (e.g. proposal number)
            salesperson_code: Salesperson code for the quote (from logged-in user)

        Returns:
            { "quote_id", "number", "reference_number", "lines" } or raises on error
        """
        quote_data = {
            "customerNumber": customer_no,
            "externalDocumentNumber": external_document_number or "",
        }
        if salesperson_code:
            quote_data["salespersonCode"] = salesperson_code

        quote = None
        used_entity = None
        for entity in ("salesQuotes", "Sales_Quote"):
            try:
                quote = self._make_sync_request("POST", entity, data=quote_data)
                used_entity = entity
                break
            except Exception as e:
                if entity == "Sales_Quote":
                    raise Exception(
                        f"Sales quote creation failed. Ensure BC exposes salesQuotes or Sales_Quote. {e}"
                    ) from e
                continue

        if not quote:
            raise Exception("Sales quote creation failed")

        quote_id = quote.get("id")
        quote_number = quote.get("number", quote.get("No", str(quote_id)))

        if not quote_id:
            raise Exception("BC did not return quote id")

        if used_entity == "Sales_Quote":
            doc_entity, line_entity = "Sales_Quote", "Sales_QuoteLine"
        else:
            doc_entity, line_entity = "salesQuotes", "salesQuoteLines"

        for seq, line in enumerate(lines, 1):
            bc_no = (line.get("bc_item_no") or line.get("product_no") or line.get("erp_number") or "").strip()
            if not bc_no:
                continue
            line_data = {
                "documentId": quote_id,
                "sequence": seq * 10000,
                "lineType": "Item",
                "lineObjectNumber": bc_no,
                "description": (line.get("product_name") or line.get("description") or bc_no).strip(),
                "quantity": float(line.get("quantity", 1) or 1),
                "unitPrice": float(line.get("unit_price", 0) or 0),
            }
            try:
                self._make_sync_request(
                    "POST", f"{doc_entity}({quote_id})/{line_entity}", data=line_data
                )
            except Exception as e:
                raise Exception(f"Failed to add quote line for {bc_no}: {e}") from e

        reference_number = quote_number
        return {
            "quote_id": quote_id,
            "number": quote_number,
            "reference_number": reference_number,
            "lines": lines,
        }
    
    # =========================================================================
    # UTILITY METHODS
    # =========================================================================
    
    def test_connection_sync(self) -> Dict[str, Any]:
        """
        Test the connection to Business Central (synchronous, matching tasks.py pattern).
        
        Returns:
            Connection status and company info
        """
        try:
            # Test by fetching a simple entity (e.g., Customer_Card with limit 1)
            params = {"$top": 1}
            result = self._make_sync_request("GET", "Customer_Card", params=params)
            
            return {
                "status": "connected",
                "base_url": self.get_base_url(),
                "country": self.country,
                "auth_method": "Basic Auth" if self.username else "OAuth",
                "test_successful": True
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "base_url": self.get_base_url(),
                "country": self.country
            }
    
    async def test_connection(self) -> Dict[str, Any]:
        """
        Test the connection to Business Central (async version).
        
        Returns:
            Connection status and company info
        """
        # Use synchronous method (matching tasks.py pattern)
        return self.test_connection_sync()
    
    def close_sync(self):
        """Close the synchronous HTTP client."""
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None
    
    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None
        if self._sync_client:
            self._sync_client.close()
            self._sync_client = None


# Singleton instance
_bc_client: Optional[BusinessCentralClient] = None


def get_bc_client(country: str = "KENYA") -> BusinessCentralClient:
    """
    Get the Business Central client singleton.
    
    Args:
        country: Company/country code (default: "KENYA")
    
    Returns:
        BusinessCentralClient instance
    """
    global _bc_client
    if _bc_client is None:
        _bc_client = BusinessCentralClient(country=country)
    elif _bc_client.country != country:
        # If country changed, create new client
        _bc_client.close_sync()
        _bc_client = BusinessCentralClient(country=country)
    return _bc_client
