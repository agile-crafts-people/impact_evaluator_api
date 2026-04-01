"""
TestData routes for Flask API.

Provides endpoints for TestData domain:
- POST /api/testdata - Create a new testdata document
- GET /api/testdata - Get all testdata documents (with optional ?name= query parameter)
- GET /api/testdata/<id> - Get a specific testdata document by ID
- PATCH /api/testdata/<id> - Update a testdata document
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.testdata_service import TestDataService

import logging
logger = logging.getLogger(__name__)


def create_testdata_routes():
    """
    Create a Flask Blueprint exposing testdata endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with testdata routes
    """
    testdata_routes = Blueprint('testdata_routes', __name__)
    
    @testdata_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_testdata():
        """
        POST /api/testdata - Create a new testdata document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the created testdata document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        testdata_id = TestDataService.create_testdata(data, token, breadcrumb)
        testdata = TestDataService.get_testdata(testdata_id, token, breadcrumb)
        
        logger.info(f"create_testdata Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(testdata), 201
    
    @testdata_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_testdatas():
        """
        GET /api/testdata - Retrieve infinite scroll batch of sorted, filtered testdata documents.
        
        Query Parameters:
            name: Optional name filter
            after_id: Cursor for infinite scroll (ID of last item from previous batch, omit for first request)
            limit: Items per batch (default: 10, max: 100)
            sort_by: Field to sort by (default: 'name')
            order: Sort order 'asc' or 'desc' (default: 'asc')
        
        Returns:
            JSON response with infinite scroll results: {
                'items': [...],
                'limit': int,
                'has_more': bool,
                'next_cursor': str|None
            }
        
        Raises:
            400 Bad Request: If invalid parameters provided
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        # Get query parameters
        name = request.args.get('name')
        after_id = request.args.get('after_id')
        limit = request.args.get('limit', 10, type=int)
        sort_by = request.args.get('sort_by', 'name')
        order = request.args.get('order', 'asc')
        
        # Service layer validates parameters and raises HTTPBadRequest if invalid
        # @handle_route_exceptions decorator will catch and format the exception
        result = TestDataService.get_testdatas(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_testdatas Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @testdata_routes.route('/<testdata_id>', methods=['GET'])
    @handle_route_exceptions
    def get_testdata(testdata_id):
        """
        GET /api/testdata/<id> - Retrieve a specific testdata document by ID.
        
        Args:
            testdata_id: The testdata ID to retrieve
            
        Returns:
            JSON response with the testdata document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        testdata = TestDataService.get_testdata(testdata_id, token, breadcrumb)
        logger.info(f"get_testdata Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(testdata), 200
    
    @testdata_routes.route('/<testdata_id>', methods=['PATCH'])
    @handle_route_exceptions
    def update_testdata(testdata_id):
        """
        PATCH /api/testdata/<id> - Update a testdata document.
        
        Args:
            testdata_id: The testdata ID to update
            
        Request body (JSON):
        {
            "name": "new_value",
            "description": "new_value",
            "status": "archived",
            ...
        }
        
        Returns:
            JSON response with the updated testdata document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        testdata = TestDataService.update_testdata(testdata_id, data, token, breadcrumb)
        
        logger.info(f"update_testdata Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(testdata), 200
    
    logger.info("TestData Flask Routes Registered")
    return testdata_routes