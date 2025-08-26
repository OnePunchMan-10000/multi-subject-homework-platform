#!/usr/bin/env python3
"""
Simple test to verify UI components can be imported
"""

def test_imports():
    try:
        # Test importing the main UI functions
        from app.ui import (
            render_landing_page,
            render_home_page, 
            render_navigation,
            render_footer,
            render_qa_page,
            render_qa_processing_page,
            auth_ui
        )
        print("✅ All UI components imported successfully!")
        
        # Test importing main app
        from app.main import main, render_global_css
        print("✅ Main app functions imported successfully!")
        
        print("\n🎉 All imports successful! The new UI is ready to use.")
        print("\nTo run the app:")
        print("streamlit run app/main.py --server.port 8501")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_imports()

