#!/usr/bin/env python3
"""Quick validation of current parse_usage_limit_error implementation"""

def validate_parse_function():
    try:
        from automate_dev import parse_usage_limit_error
        
        # Test successful case
        error_message = "You have reached your usage limit. You can try again at 7pm (America/Chicago)."
        result = parse_usage_limit_error(error_message)
        
        success = (
            isinstance(result, dict) and
            result.get("reset_time") == "7pm" and
            result.get("timezone") == "America/Chicago" and
            result.get("format") == "natural_language"
        )
        
        if success:
            print("✅ Current implementation working correctly")
            return True
        else:
            print(f"❌ Current implementation issue: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing current implementation: {e}")
        return False

if __name__ == "__main__":
    validate_parse_function()