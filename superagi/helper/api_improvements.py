
from typing import Dict, Any, Optional, List
import json
import logging
from datetime import datetime
import asyncio
from concurrent.futures import ThreadPoolExecutor
import time

class APIPerformanceManager:
    """
    API Performance Manager - Handle API optimization and monitoring
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Performance tracking
        self.request_times = []
        self.error_rates = {}
        self.cache = {}
        self.cache_ttl = self.config.get("cache_ttl", 300)  # 5 minutes
        
        # Concurrency control
        self.max_concurrent_requests = self.config.get("max_concurrent", 5)
        self.executor = ThreadPoolExecutor(max_workers=self.max_concurrent_requests)
        
    def track_request(self, endpoint: str, duration: float, success: bool):
        """Track API request performance"""
        timestamp = time.time()
        
        self.request_times.append({
            "endpoint": endpoint,
            "duration": duration,
            "timestamp": timestamp,
            "success": success
        })
        
        # Keep only last 1000 requests
        if len(self.request_times) > 1000:
            self.request_times = self.request_times[-1000:]
        
        # Update error rates
        if endpoint not in self.error_rates:
            self.error_rates[endpoint] = {"total": 0, "errors": 0}
        
        self.error_rates[endpoint]["total"] += 1
        if not success:
            self.error_rates[endpoint]["errors"] += 1
    
    def get_cache_key(self, endpoint: str, params: Dict[str, Any]) -> str:
        """Generate cache key for request"""
        cache_params = json.dumps(params, sort_keys=True)
        return f"{endpoint}:{hash(cache_params)}"
    
    def get_cached_response(self, cache_key: str) -> Optional[Any]:
        """Get cached response if valid"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if time.time() - cached_data["timestamp"] < self.cache_ttl:
                self.logger.debug(f"Cache hit for key: {cache_key}")
                return cached_data["response"]
            else:
                # Cache expired
                del self.cache[cache_key]
        
        return None
    
    def cache_response(self, cache_key: str, response: Any):
        """Cache API response"""
        self.cache[cache_key] = {
            "response": response,
            "timestamp": time.time()
        }
        
        # Clean old cache entries
        self._clean_cache()
    
    def _clean_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.cache.items()
            if current_time - data["timestamp"] > self.cache_ttl
        ]
        
        for key in expired_keys:
            del self.cache[key]
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get API performance statistics"""
        if not self.request_times:
            return {"status": "no_data"}
        
        # Calculate averages
        total_requests = len(self.request_times)
        successful_requests = len([r for r in self.request_times if r["success"]])
        
        avg_response_time = sum(r["duration"] for r in self.request_times) / total_requests
        success_rate = (successful_requests / total_requests) * 100
        
        # Recent performance (last 100 requests)
        recent_requests = self.request_times[-100:]
        recent_avg = sum(r["duration"] for r in recent_requests) / len(recent_requests)
        
        # Error rates by endpoint
        endpoint_stats = {}
        for endpoint, stats in self.error_rates.items():
            error_rate = (stats["errors"] / stats["total"]) * 100 if stats["total"] > 0 else 0
            endpoint_stats[endpoint] = {
                "total_requests": stats["total"],
                "error_rate": round(error_rate, 2)
            }
        
        return {
            "total_requests": total_requests,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(avg_response_time, 3),
            "recent_avg_response_time": round(recent_avg, 3),
            "cache_size": len(self.cache),
            "endpoint_stats": endpoint_stats
        }
    
    async def make_concurrent_requests(self, requests: List[Dict[str, Any]]) -> List[Any]:
        """Make multiple API requests concurrently"""
        loop = asyncio.get_event_loop()
        
        # Create tasks for concurrent execution
        tasks = []
        for request_config in requests:
            task = loop.run_in_executor(
                self.executor,
                self._execute_single_request,
                request_config
            )
            tasks.append(task)
        
        # Wait for all requests to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return results
    
    def _execute_single_request(self, request_config: Dict[str, Any]) -> Any:
        """Execute a single API request"""
        start_time = time.time()
        success = False
        
        try:
            # This would be replaced with actual API call
            endpoint = request_config.get("endpoint", "unknown")
            params = request_config.get("params", {})
            
            # Check cache first
            cache_key = self.get_cache_key(endpoint, params)
            cached_response = self.get_cached_response(cache_key)
            
            if cached_response:
                success = True
                return cached_response
            
            # Make actual request (placeholder)
            response = self._make_api_request(endpoint, params)
            
            # Cache successful response
            if response:
                self.cache_response(cache_key, response)
                success = True
            
            return response
            
        except Exception as e:
            self.logger.error(f"Request failed: {e}")
            return {"error": str(e)}
            
        finally:
            duration = time.time() - start_time
            self.track_request(request_config.get("endpoint", "unknown"), duration, success)
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Any:
        """Placeholder for actual API request implementation"""
        # This would be implemented with actual API calls
        # For now, return a mock response
        time.sleep(0.1)  # Simulate API delay
        return {
            "endpoint": endpoint,
            "params": params,
            "response": "Mock API response",
            "timestamp": datetime.now().isoformat()
        }
    
    def optimize_request_batching(self, requests: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Optimize request batching for better performance"""
        # Group requests by endpoint
        endpoint_groups = {}
        for request in requests:
            endpoint = request.get("endpoint", "default")
            if endpoint not in endpoint_groups:
                endpoint_groups[endpoint] = []
            endpoint_groups[endpoint].append(request)
        
        # Create optimized batches
        batches = []
        for endpoint, endpoint_requests in endpoint_groups.items():
            # Split into smaller batches to avoid overwhelming the API
            batch_size = self.config.get("batch_size", 10)
            for i in range(0, len(endpoint_requests), batch_size):
                batch = endpoint_requests[i:i + batch_size]
                batches.append(batch)
        
        return batches
    
    def should_use_cache(self, endpoint: str, params: Dict[str, Any]) -> bool:
        """Determine if request should use cache"""
        # Don't cache write operations
        if any(method in endpoint.lower() for method in ["post", "put", "delete", "create", "update"]):
            return False
        
        # Don't cache time-sensitive requests
        if "real_time" in params or "no_cache" in params:
            return False
        
        return True
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get API health metrics"""
        stats = self.get_performance_stats()
        
        health_status = "healthy"
        if stats.get("success_rate", 100) < 90:
            health_status = "degraded"
        if stats.get("avg_response_time", 0) > 5.0:
            health_status = "slow"
        if stats.get("success_rate", 100) < 50:
            health_status = "critical"
        
        return {
            "status": health_status,
            "metrics": stats,
            "recommendations": self._get_performance_recommendations(stats)
        }
    
    def _get_performance_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """Get performance improvement recommendations"""
        recommendations = []
        
        if stats.get("avg_response_time", 0) > 2.0:
            recommendations.append("Consider implementing request caching")
        
        if stats.get("success_rate", 100) < 95:
            recommendations.append("Implement retry logic with exponential backoff")
        
        if stats.get("cache_size", 0) > 1000:
            recommendations.append("Consider reducing cache TTL or implementing LRU eviction")
        
        for endpoint, endpoint_stats in stats.get("endpoint_stats", {}).items():
            if endpoint_stats.get("error_rate", 0) > 10:
                recommendations.append(f"High error rate for {endpoint} - investigate endpoint health")
        
        return recommendations

# Global performance manager instance
performance_manager = APIPerformanceManager()
