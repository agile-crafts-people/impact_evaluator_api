"""
Grade service for business logic and RBAC.

Handles RBAC checks and MongoDB operations for Grade domain.
"""
from api_utils import MongoIO, Config
from api_utils.flask_utils.exceptions import HTTPBadRequest, HTTPForbidden, HTTPNotFound, HTTPInternalServerError
from api_utils.mongo_utils import execute_infinite_scroll_query
import logging

logger = logging.getLogger(__name__)

# Allowed sort fields for Grade domain
ALLOWED_SORT_FIELDS = ['name', 'description', 'created.at_time']


class GradeService:
    """
    Service class for Grade domain operations.
    
    Handles:
    - RBAC authorization checks (placeholder for future implementation)
    - MongoDB operations via MongoIO singleton
    - Business logic for Grade domain
    """
    
    @staticmethod
    def _check_permission(token, operation):
        """
        Check if the user has permission to perform an operation.
        
        Args:
            token: Token dictionary with user_id and roles
            operation: The operation being performed (e.g., 'read', 'create')
        
        Raises:
            HTTPForbidden: If user doesn't have required permission
            
        Note: This is a placeholder for future RBAC implementation.
        For now, all operations require a valid token (authentication only).
        
        Example RBAC implementation:
            if operation == 'create':
                # Grade requires staff or admin role
                if not any(role in token.get('roles', []) for role in ['staff', 'admin']):
                    raise HTTPForbidden("Staff or admin role required to create grade documents")
            elif operation == 'read':
                # Read requires any authenticated user (no additional check needed)
                pass
        """
        pass
    
    @staticmethod
    def create_grade(data, token, breadcrumb):
        """
        Create a new grade document.
        
        Args:
            data: Dictionary containing grade data
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging (contains at_time, by_user, from_ip, correlation_id)
            
        Returns:
            str: The ID of the graded grade document
        """
        try:
            GradeService._check_permission(token, 'create')
            
            # Remove _id if present (MongoDB will generate it)
            if '_id' in data:
                del data['_id']
            
            # Automatically populate required field: created
            # This is system-managed and should not be provided by the client
            # Use breadcrumb directly as it already has the correct structure
            data['created'] = breadcrumb
            
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            grade_id = mongo.create_document(config.GRADE_COLLECTION_NAME, data)
            logger.info(f"Created grade { grade_id} for user {token.get('user_id')}")
            return grade_id
        except HTTPForbidden:
            raise
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error creating grade: {error_msg}")
            raise HTTPInternalServerError(f"Failed to create grade: {error_msg}")
    
    @staticmethod
    def get_grades(token, breadcrumb, name=None, after_id=None, limit=10, sort_by='name', order='asc'):
        """
        Get infinite scroll batch of sorted, filtered grade documents.
        
        Args:
            token: Authentication token
            breadcrumb: Audit breadcrumb
            name: Optional name filter (simple search)
            after_id: Cursor (ID of last item from previous batch, None for first request)
            limit: Items per batch
            sort_by: Field to sort by
            order: Sort order ('asc' or 'desc')
        
        Returns:
            dict: {
                'items': [...],
                'limit': int,
                'has_more': bool,
                'next_cursor': str|None  # ID of last item, or None if no more
            }
        
        Raises:
            HTTPBadRequest: If invalid parameters provided
        """
        try:
            GradeService._check_permission(token, 'read')
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            collection = mongo.get_collection(config.GRADE_COLLECTION_NAME)
            result = execute_infinite_scroll_query(
                collection,
                name=name,
                after_id=after_id,
                limit=limit,
                sort_by=sort_by,
                order=order,
                allowed_sort_fields=ALLOWED_SORT_FIELDS,
            )
            logger.info(
                f"Retrieved {len(result['items'])} grades (has_more={result['has_more']}) "
                f"for user {token.get('user_id')}"
            )
            return result
        except HTTPBadRequest:
            raise
        except Exception as e:
            logger.error(f"Error retrieving grades: {str(e)}")
            raise HTTPInternalServerError("Failed to retrieve grades")
    
    @staticmethod
    def get_grade(grade_id, token, breadcrumb):
        """
        Retrieve a specific grade document by ID.
        
        Args:
            grade_id: The grade ID to retrieve
            token: Token dictionary with user_id and roles
            breadcrumb: Breadcrumb dictionary for logging
            
        Returns:
            dict: The grade document
            
        Raises:
            HTTPNotFound: If grade is not found
        """
        try:
            GradeService._check_permission(token, 'read')
            
            mongo = MongoIO.get_instance()
            config = Config.get_instance()
            grade = mongo.get_document(config.GRADE_COLLECTION_NAME, grade_id)
            if grade is None:
                raise HTTPNotFound(f"Grade { grade_id} not found")
            
            logger.info(f"Retrieved grade { grade_id} for user {token.get('user_id')}")
            return grade
        except HTTPNotFound:
            raise
        except Exception as e:
            logger.error(f"Error retrieving grade { grade_id}: {str(e)}")
            raise HTTPInternalServerError(f"Failed to retrieve grade { grade_id}")