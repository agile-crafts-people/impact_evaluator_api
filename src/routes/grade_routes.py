"""
Grade routes for Flask API.

Provides endpoints for Create domain:
- POST /api/grade - Create a new grade document
- GET /api/grade - Get all grade documents
- GET /api/grade/<id> - Get a specific grade document by ID
"""
from flask import Blueprint, jsonify, request
from api_utils.flask_utils.token import create_flask_token
from api_utils.flask_utils.breadcrumb import create_flask_breadcrumb
from api_utils.flask_utils.route_wrapper import handle_route_exceptions
from src.services.grade_service import GradeService

import logging
logger = logging.getLogger(__name__)


def create_grade_routes():
    """
    Create a Flask Blueprint exposing grade endpoints.
    
    Returns:
        Blueprint: Flask Blueprint with grade routes
    """
    grade_routes = Blueprint('grade_routes', __name__)
    
    @grade_routes.route('', methods=['POST'])
    @handle_route_exceptions
    def create_grade():
        """
        POST /api/grade - Create a new grade document.
        
        Request body (JSON):
        {
            "name": "value",
            "description": "value",
            "status": "active",
            ...
        }
        
        Returns:
            JSON response with the graded grade document including _id
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        data = request.get_json() or {}
        grade_id = GradeService.create_grade(data, token, breadcrumb)
        grade = GradeService.get_grade(grade_id, token, breadcrumb)
        
        logger.info(f"create_grade Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(grade), 201
    
    @grade_routes.route('', methods=['GET'])
    @handle_route_exceptions
    def get_grades():
        """
        GET /api/grade - Retrieve infinite scroll batch of sorted, filtered grade documents.
        
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
        result = GradeService.get_grades(
            token, 
            breadcrumb, 
            name=name,
            after_id=after_id,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        logger.info(f"get_grades Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(result), 200
    
    @grade_routes.route('/<grade_id>', methods=['GET'])
    @handle_route_exceptions
    def get_grade(grade_id):
        """
        GET /api/grade/<id> - Retrieve a specific grade document by ID.
        
        Args:
            grade_id: The grade ID to retrieve
            
        Returns:
            JSON response with the grade document
        """
        token = create_flask_token()
        breadcrumb = create_flask_breadcrumb(token)
        
        grade = GradeService.get_grade(grade_id, token, breadcrumb)
        logger.info(f"get_grade Success {str(breadcrumb['at_time'])}, {breadcrumb['correlation_id']}")
        return jsonify(grade), 200
    
    logger.info("Create Flask Routes Registered")
    return grade_routes