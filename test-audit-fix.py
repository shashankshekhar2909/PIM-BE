#!/usr/bin/env python3
"""
Quick test to verify the audit model fix
"""

def test_audit_model_import():
    """Test that the AuditLog model can be imported without errors"""
    try:
        # Test importing the model
        from app.models.audit import AuditLog
        print("✅ AuditLog model imported successfully")
        
        # Test creating an instance
        audit_log = AuditLog(
            user_id=1,
            action="test",
            resource_type="test",
            audit_metadata={"test": "data"}
        )
        print("✅ AuditLog instance created successfully")
        
        # Test the repr method
        repr_str = repr(audit_log)
        print(f"✅ AuditLog repr: {repr_str}")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_superadmin_import():
    """Test that the superadmin endpoints can be imported"""
    try:
        from app.api.v1.endpoints.superadmin import router
        print("✅ Superadmin router imported successfully")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Audit Model Fix")
    print("=" * 30)
    
    success = True
    
    # Test audit model
    if not test_audit_model_import():
        success = False
    
    # Test superadmin endpoints
    if not test_superadmin_import():
        success = False
    
    if success:
        print("\n🎉 All tests passed! The audit model fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.") 