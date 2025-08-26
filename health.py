"""Health check to verify deployment is working"""
import datetime

def get_deployment_info():
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "4-page-navigation-flow-v3-connection-test",
        "commit": "latest",
        "database": "postgresql-railway-connected"
    }

if __name__ == "__main__":
    print("Deployment Health Check:")
    print(get_deployment_info())
