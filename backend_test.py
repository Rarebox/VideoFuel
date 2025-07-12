#!/usr/bin/env python3
"""
VideoFuel AI Backend API Testing Suite
Tests all API endpoints for the YouTube content generation SaaS
"""

import requests
import sys
import json
from datetime import datetime

class VideoFuelAPITester:
    def __init__(self, base_url="https://0a5cbc47-5f2a-4d3d-8c8b-fd869f52a0d2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_data = {}

    def log_test(self, name, success, details=""):
        """Log test results"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {name} - PASSED")
        else:
            print(f"❌ {name} - FAILED: {details}")
        
        if details:
            print(f"   Details: {details}")

    def test_health_check(self):
        """Test the root health check endpoint"""
        try:
            response = requests.get(f"{self.api_url}/", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_keys = ["message", "version"]
                has_expected_keys = all(key in data for key in expected_keys)
                success = has_expected_keys
                details = f"Response: {data}" if has_expected_keys else f"Missing keys in response: {data}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Health Check (/api/)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Health Check (/api/)", False, str(e))
            return False

    def test_get_models(self):
        """Test the models endpoint"""
        try:
            response = requests.get(f"{self.api_url}/models", timeout=10)
            success = response.status_code == 200
            
            if success:
                data = response.json()
                expected_models = ["deephermes2pro", "mixtral", "gpt4o"]
                has_models = "models" in data and isinstance(data["models"], list)
                has_expected_models = all(model in data["models"] for model in expected_models)
                success = has_models and has_expected_models
                details = f"Available models: {data.get('models', [])}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Get Models (/api/models)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Get Models (/api/models)", False, str(e))
            return False

    def test_generate_titles(self, topic="how to cook pasta", language="en", model="deephermes2pro"):
        """Test title generation endpoint"""
        try:
            payload = {
                "topic": topic,
                "language": language,
                "model": model
            }
            
            response = requests.post(
                f"{self.api_url}/generate-titles", 
                json=payload, 
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_keys = ["titles", "language", "model_used"]
                has_required_keys = all(key in data for key in required_keys)
                has_five_titles = isinstance(data.get("titles"), list) and len(data.get("titles", [])) == 5
                success = has_required_keys and has_five_titles
                
                if success:
                    self.test_data["titles"] = data["titles"]
                    self.test_data["selected_title"] = data["titles"][0]  # Select first title for next tests
                    details = f"Generated {len(data['titles'])} titles: {data['titles'][:2]}..."
                else:
                    details = f"Invalid response structure: {data}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Generate Titles (/api/generate-titles)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Generate Titles (/api/generate-titles)", False, str(e))
            return False

    def test_generate_description(self, title=None, language="en", model="deephermes2pro"):
        """Test description generation endpoint"""
        if not title:
            title = self.test_data.get("selected_title", "How to Cook Perfect Pasta Every Time")
            
        try:
            payload = {
                "title": title,
                "language": language,
                "model": model
            }
            
            response = requests.post(
                f"{self.api_url}/generate-description", 
                json=payload, 
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_keys = ["description", "hashtags", "language", "model_used"]
                has_required_keys = all(key in data for key in required_keys)
                has_description = isinstance(data.get("description"), str) and len(data.get("description", "")) > 0
                has_hashtags = isinstance(data.get("hashtags"), list) and len(data.get("hashtags", [])) > 0
                success = has_required_keys and has_description and has_hashtags
                
                if success:
                    self.test_data["description"] = data["description"]
                    self.test_data["hashtags"] = data["hashtags"]
                    details = f"Description: {data['description'][:50]}..., Hashtags: {len(data['hashtags'])} tags"
                else:
                    details = f"Invalid response structure: {data}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Generate Description (/api/generate-description)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Generate Description (/api/generate-description)", False, str(e))
            return False

    def test_generate_script(self, title=None, language="en", video_length_minutes=5, model="deephermes2pro"):
        """Test script generation endpoint"""
        if not title:
            title = self.test_data.get("selected_title", "How to Cook Perfect Pasta Every Time")
            
        try:
            payload = {
                "title": title,
                "language": language,
                "video_length_minutes": video_length_minutes,
                "model": model
            }
            
            response = requests.post(
                f"{self.api_url}/generate-script", 
                json=payload, 
                timeout=45,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_keys = ["hook", "sections", "outro", "language", "model_used"]
                has_required_keys = all(key in data for key in required_keys)
                has_hook = isinstance(data.get("hook"), str) and len(data.get("hook", "")) > 0
                has_sections = isinstance(data.get("sections"), list) and len(data.get("sections", [])) > 0
                has_outro = isinstance(data.get("outro"), str) and len(data.get("outro", "")) > 0
                success = has_required_keys and has_hook and has_sections and has_outro
                
                if success:
                    self.test_data["script"] = data
                    details = f"Hook: {data['hook'][:30]}..., Sections: {len(data['sections'])}, Outro: {data['outro'][:30]}..."
                else:
                    details = f"Invalid response structure: {data}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Generate Script (/api/generate-script)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Generate Script (/api/generate-script)", False, str(e))
            return False

    def test_generate_thumbnail(self, title=None, language="en", model="deephermes2pro"):
        """Test thumbnail text generation endpoint"""
        if not title:
            title = self.test_data.get("selected_title", "How to Cook Perfect Pasta Every Time")
            
        try:
            payload = {
                "title": title,
                "language": language,
                "model": model
            }
            
            response = requests.post(
                f"{self.api_url}/generate-thumbnail", 
                json=payload, 
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_keys = ["thumbnail_texts", "language", "model_used"]
                has_required_keys = all(key in data for key in required_keys)
                has_thumbnail_texts = isinstance(data.get("thumbnail_texts"), list) and len(data.get("thumbnail_texts", [])) == 3
                success = has_required_keys and has_thumbnail_texts
                
                if success:
                    self.test_data["thumbnail_texts"] = data["thumbnail_texts"]
                    details = f"Generated {len(data['thumbnail_texts'])} thumbnail texts: {data['thumbnail_texts']}"
                else:
                    details = f"Invalid response structure: {data}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Generate Thumbnail (/api/generate-thumbnail)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Generate Thumbnail (/api/generate-thumbnail)", False, str(e))
            return False

    def test_analyze_seo(self, title=None, description=None, hashtags=None, language="en"):
        """Test SEO analysis endpoint"""
        if not title:
            title = self.test_data.get("selected_title", "How to Cook Perfect Pasta Every Time")
        if not description:
            description = self.test_data.get("description", "Learn how to cook perfect pasta with our step-by-step guide.")
        if not hashtags:
            hashtags = self.test_data.get("hashtags", ["#pasta", "#cooking", "#recipe"])
            
        try:
            payload = {
                "title": title,
                "description": description,
                "hashtags": hashtags,
                "language": language
            }
            
            response = requests.post(
                f"{self.api_url}/analyze-seo", 
                json=payload, 
                timeout=15,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                required_keys = ["scores", "recommendations"]
                has_required_keys = all(key in data for key in required_keys)
                
                if has_required_keys:
                    scores = data["scores"]
                    score_keys = ["clickbait_score", "keyword_relevance_score", "length_score", "overall_seo_score"]
                    has_score_keys = all(key in scores for key in score_keys)
                    scores_in_range = all(0 <= scores[key] <= 100 for key in score_keys if key in scores)
                    has_recommendations = isinstance(data.get("recommendations"), list)
                    success = has_score_keys and scores_in_range and has_recommendations
                    
                    if success:
                        details = f"SEO Scores - Clickbait: {scores['clickbait_score']}, Keyword: {scores['keyword_relevance_score']}, Length: {scores['length_score']}, Overall: {scores['overall_seo_score']}"
                    else:
                        details = f"Invalid scores structure: {data}"
                else:
                    details = f"Missing required keys: {data}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Analyze SEO (/api/analyze-seo)", success, details)
            return success
            
        except Exception as e:
            self.log_test("Analyze SEO (/api/analyze-seo)", False, str(e))
            return False

    def test_turkish_language(self):
        """Test Turkish language support"""
        try:
            # Test with Turkish topic
            payload = {
                "topic": "makarna nasıl pişirilir",
                "language": "tr",
                "model": "deephermes2pro"
            }
            
            response = requests.post(
                f"{self.api_url}/generate-titles", 
                json=payload, 
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            success = response.status_code == 200
            
            if success:
                data = response.json()
                has_titles = isinstance(data.get("titles"), list) and len(data.get("titles", [])) == 5
                language_correct = data.get("language") == "tr"
                success = has_titles and language_correct
                details = f"Turkish titles generated: {len(data.get('titles', []))} titles, Language: {data.get('language')}"
            else:
                details = f"Status: {response.status_code}, Response: {response.text}"
                
            self.log_test("Turkish Language Support", success, details)
            return success
            
        except Exception as e:
            self.log_test("Turkish Language Support", False, str(e))
            return False

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting VideoFuel AI Backend API Tests")
        print(f"📍 Testing against: {self.base_url}")
        print("=" * 60)
        
        # Basic connectivity tests
        health_ok = self.test_health_check()
        models_ok = self.test_get_models()
        
        if not health_ok:
            print("\n❌ Health check failed - stopping tests")
            return False
            
        # Content generation workflow tests
        titles_ok = self.test_generate_titles()
        description_ok = self.test_generate_description()
        script_ok = self.test_generate_script()
        thumbnail_ok = self.test_generate_thumbnail()
        seo_ok = self.test_analyze_seo()
        
        # Language support test
        turkish_ok = self.test_turkish_language()
        
        # Print summary
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {self.tests_passed}/{self.tests_run} tests passed")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed! Backend API is working correctly.")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} tests failed. Check the details above.")
            return False

def main():
    """Main test runner"""
    tester = VideoFuelAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())