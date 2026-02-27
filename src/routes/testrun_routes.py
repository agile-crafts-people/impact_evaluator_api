"""
TestRun routes for Flask API.

Provides endpoints for TestRun domain:
- POST /api/testrun - Create a new testrun document
- GET /api/testrun - Get all testrun documents (with optional ?name= query parameter)
- GET /api/testrun/<id> - Get a specific testrun document by ID
- PATCH /api/testrun/<id> - Update a testrun document
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.testrun_service import TestRunService

import logging
logger = logging.getLogger(__name__)


def create_testrun_routes():
    """
    Create a Flask Blueprint exposing testrun endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with testrun routes
    """
    testrun_routes = Blueprint('testrun_routes', __name__)
    
    @testrun_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_testrun():
        """
        POST /api/testrun - Create a new testrun document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the created testrun document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        testrun_id = TestRunService.create_testrun(data, token, breadcrumb)
        testrun = TestRunService.get_testrun(testrun_id, token, breadcrumb)
        
        logger.info(f"create_testrun Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(testrun), 201
    
    @testrun_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_testruns():
        """
        GET /api/testrun - Retrieve infinite scroll batch of sorted, filtered testrun documents.
        
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
        result = TestRunService.get_testruns(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_testruns Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @testrun_routes.route('/<testrun_id>', methods=['GET'])
    @handle_route_exceptions
    def get_testrun(testrun_id):
        """
        GET /api/testrun/<id> - Retrieve a specific testrun document by ID.
        
        Args:
            testrun_id: The testrun ID to retrieve
            
        Returns:
            JSON response with the testrun document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        testrun = TestRunService.get_testrun(testrun_id, token, breadcrumb)
        logger.info(f"get_testrun Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(testrun), 200
    
    @testrun_routes.route('/<testrun_id>', methods=['PATCH'])
    @handle_route_exceptions
    def update_testrun(testrun_id):
        """
        PATCH /api/testrun/<id> - Update a testrun document.
        
        Args:
            testrun_id: The testrun ID to update
            
        Request body (JSON):
        {
            "name": "new_value",
            "description": "new_value",
            "status": "archived",
            ...
        }
        
        Returns:
            JSON response with the updated testrun document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        testrun = TestRunService.update_testrun(testrun_id, data, token, breadcrumb)
        
        logger.info(f"update_testrun Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(testrun), 200
    
    logger.info("TestRun Flask Routes Registered")
    return testrun_routes