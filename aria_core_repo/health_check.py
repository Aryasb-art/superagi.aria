#!/usr/bin/env python3
"""
System Health Check and Diagnostic Tool
"""
import requests
import json
import time
from datetime import datetime

class SystemHealthChecker:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
    
    def check_endpoint(self, endpoint, method="GET", data=None, expected_status=200):
        """Check individual endpoint health"""
        try:
            url = f"{self.base_url}{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data, timeout=10)
            
            result = {
                "endpoint": endpoint,
                "method": method,
                "status_code": response.status_code,
                "expected": expected_status,
                "success": response.status_code == expected_status,
                "response_time": response.elapsed.total_seconds(),
                "timestamp": datetime.now().isoformat()
            }
            
            try:
                result["response_body"] = response.json()
            except:
                result["response_body"] = response.text[:200] if response.text else "Empty response"
                
            self.results.append(result)
            return result
            
        except Exception as e:
            error_result = {
                "endpoint": endpoint,
                "method": method,
                "error": str(e),
                "success": False,
                "timestamp": datetime.now().isoformat()
            }
            self.results.append(error_result)
            return error_result
    
    def run_comprehensive_check(self):
        """Run comprehensive system health check"""
        print("🔍 Starting Comprehensive System Health Check...")
        print("=" * 60)
        
        # Basic endpoints
        print("\n📊 Basic Health Checks:")
        self.check_endpoint("/health")
        self.check_endpoint("/")
        self.check_endpoint("/ui")
        
        # Agent endpoints (public - no auth needed)
        print("\n🤖 Agent System Checks:")
        test_message = {"message": "system health check"}
        
        self.check_endpoint("/agent/public", "POST", test_message)
        self.check_endpoint("/agent/memory", "POST", test_message)
        self.check_endpoint("/agent/utility/public", "POST", test_message)
        self.check_endpoint("/agent/emotion-regulation/analyze/public", "POST", test_message)
        self.check_endpoint("/agent/bias-detection/analyze/public", "POST", test_message)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive health report"""
        print("\n" + "=" * 60)
        print("📋 HEALTH CHECK REPORT")
        print("=" * 60)
        
        total_checks = len(self.results)
        successful_checks = sum(1 for r in self.results if r.get("success", False))
        failed_checks = total_checks - successful_checks
        
        print(f"Total Checks: {total_checks}")
        print(f"✅ Successful: {successful_checks}")
        print(f"❌ Failed: {failed_checks}")
        print(f"Success Rate: {(successful_checks/total_checks)*100:.1f}%")
        
        print("\n🔍 Detailed Results:")
        for result in self.results:
            status = "✅" if result.get("success", False) else "❌"
            endpoint = result["endpoint"]
            method = result["method"]
            
            if result.get("success", False):
                response_time = result.get("response_time", 0)
                print(f"{status} {method} {endpoint} - {response_time:.2f}s")
            else:
                error = result.get("error", "Unknown error")
                print(f"{status} {method} {endpoint} - ERROR: {error}")
        
        print("\n💡 Recommendations:")
        if failed_checks > 0:
            print("- Some endpoints are failing. Check server logs for details.")
            print("- Verify database connections and API keys.")
            print("- Consider implementing additional fallback mechanisms.")
        else:
            print("- All systems operational!")
            print("- System is healthy and ready for production use.")

if __name__ == "__main__":
    checker = SystemHealthChecker()
    checker.run_comprehensive_check()