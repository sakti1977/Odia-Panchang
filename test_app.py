#!/usr/bin/env python3
"""
Test script for Odia Panchang Phase 1 implementation.
Tests all new features including web interface, multi-city support, and downloads.
"""

import sys
import time
import requests
from datetime import datetime

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def print_test(test_name, status, message=""):
    """Print test result with color coding."""
    symbol = f"{GREEN}✅{RESET}" if status else f"{RED}❌{RESET}"
    print(f"{symbol} {test_name}")
    if message:
        print(f"   {message}")

def test_health_check(base_url):
    """Test basic API health check."""
    try:
        response = requests.get(f"{base_url}/api", timeout=5)
        if response.status_code == 200 and response.json().get("status") == "ok":
            print_test("Health Check", True, "API is running")
            return True
        else:
            print_test("Health Check", False, f"Unexpected response: {response.status_code}")
            return False
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False

def test_web_interface(base_url):
    """Test if web interface is accessible."""
    try:
        response = requests.get(base_url, timeout=5)
        if response.status_code == 200 and "ଓଡ଼ିଆ ପଞ୍ଜିକା" in response.text:
            print_test("Web Interface", True, "HTML page loads with Odia content")
            return True
        else:
            print_test("Web Interface", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Web Interface", False, f"Error: {str(e)}")
        return False

def test_cities_endpoint(base_url):
    """Test cities API endpoint."""
    try:
        response = requests.get(f"{base_url}/api/cities", timeout=5)
        if response.status_code == 200:
            cities = response.json()
            if len(cities) >= 12:
                city_names = [c['name'] for c in cities[:3]]
                print_test("Cities Endpoint", True, f"Found {len(cities)} cities: {', '.join(city_names)}...")
                return True
            else:
                print_test("Cities Endpoint", False, f"Only {len(cities)} cities found")
                return False
        else:
            print_test("Cities Endpoint", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Cities Endpoint", False, f"Error: {str(e)}")
        return False

def test_today_panchang(base_url):
    """Test today's Panchang endpoint."""
    try:
        response = requests.get(f"{base_url}/today", timeout=5)
        if response.status_code == 200:
            data = response.json()
            required_fields = ['date', 'vara', 'tithi', 'nakshatra', 'sunrise', 'sunset']
            missing = [f for f in required_fields if f not in data]
            if not missing:
                print_test("Today's Panchang", True, f"Date: {data['date']}, Tithi: {data['tithi']['or']}")
                return True
            else:
                print_test("Today's Panchang", False, f"Missing fields: {missing}")
                return False
        else:
            print_test("Today's Panchang", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Today's Panchang", False, f"Error: {str(e)}")
        return False

def test_city_specific_panchang(base_url):
    """Test city-specific Panchang."""
    test_cities = ['puri', 'bhubaneswar', 'cuttack']
    success_count = 0

    for city in test_cities:
        try:
            response = requests.get(f"{base_url}/api/panchang/today/{city}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'city' in data and 'sunrise' in data and 'sunset' in data:
                    success_count += 1
                    if city == test_cities[0]:
                        print_test(f"City-Specific ({city})", True,
                                 f"{data['city_or']} - Sunrise: {data['sunrise']}, Sunset: {data['sunset']}")
                else:
                    print_test(f"City-Specific ({city})", False, "Missing required fields")
        except Exception as e:
            print_test(f"City-Specific ({city})", False, f"Error: {str(e)}")

    if success_count == len(test_cities):
        print_test(f"All {len(test_cities)} Cities", True, "All city-specific endpoints working")
        return True
    else:
        print_test(f"City Coverage", False, f"Only {success_count}/{len(test_cities)} working")
        return False

def test_monthly_download(base_url):
    """Test monthly Panchang download."""
    try:
        today = datetime.now()
        year = today.year
        month = today.month

        response = requests.get(
            f"{base_url}/api/panchang/monthly/{year}/{month}/download",
            params={"city": "puri", "format": "text"},
            timeout=5
        )

        if response.status_code == 200:
            content = response.text
            if "ଓଡ଼ିଆ ପଞ୍ଜିକା" in content and "Odia Panchang" in content:
                lines = len(content.split('\n'))
                print_test("Monthly Download", True, f"Downloaded {lines} lines for {month}/{year}")
                return True
            else:
                print_test("Monthly Download", False, "Missing expected content")
                return False
        else:
            print_test("Monthly Download", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Monthly Download", False, f"Error: {str(e)}")
        return False

def test_static_files(base_url):
    """Test if static files are accessible."""
    static_files = [
        ('/static/style.css', 'text/css'),
        ('/static/script.js', 'application/javascript'),
    ]

    success_count = 0
    for path, expected_type in static_files:
        try:
            response = requests.get(f"{base_url}{path}", timeout=5)
            if response.status_code == 200:
                success_count += 1
        except:
            pass

    if success_count == len(static_files):
        print_test("Static Files", True, f"All {len(static_files)} files accessible")
        return True
    else:
        print_test("Static Files", False, f"Only {success_count}/{len(static_files)} accessible")
        return False

def test_festivals_endpoint(base_url):
    """Test festivals endpoint."""
    try:
        year = datetime.now().year
        response = requests.get(f"{base_url}/festivals/{year}", timeout=5)

        if response.status_code == 200:
            festivals = response.json()
            if len(festivals) > 0:
                print_test("Festivals Endpoint", True, f"Found {len(festivals)} festivals for {year}")
                return True
            else:
                print_test("Festivals Endpoint", False, "No festivals found")
                return False
        else:
            print_test("Festivals Endpoint", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        print_test("Festivals Endpoint", False, f"Error: {str(e)}")
        return False

def run_all_tests(base_url):
    """Run all tests and report results."""
    print("\n" + "="*60)
    print(f"{YELLOW}Odia Panchang Phase 1 - Test Suite{RESET}")
    print("="*60 + "\n")

    tests = [
        ("Health Check", test_health_check),
        ("Web Interface", test_web_interface),
        ("Cities API", test_cities_endpoint),
        ("Today's Panchang", test_today_panchang),
        ("City-Specific Panchang", test_city_specific_panchang),
        ("Monthly Download", test_monthly_download),
        ("Static Files", test_static_files),
        ("Festivals", test_festivals_endpoint),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(base_url)
            results.append((test_name, result))
        except Exception as e:
            print_test(test_name, False, f"Unexpected error: {str(e)}")
            results.append((test_name, False))
        print()  # Empty line between tests

    # Summary
    print("="*60)
    passed = sum(1 for _, result in results if result)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\n{YELLOW}Test Summary:{RESET}")
    print(f"Passed: {GREEN}{passed}{RESET}/{total}")
    print(f"Failed: {RED}{total - passed}{RESET}/{total}")
    print(f"Success Rate: {GREEN if percentage >= 80 else RED}{percentage:.1f}%{RESET}\n")

    if percentage == 100:
        print(f"{GREEN}🎉 All tests passed! Phase 1 implementation is working perfectly.{RESET}\n")
    elif percentage >= 80:
        print(f"{YELLOW}⚠️  Most tests passed, but some issues remain.{RESET}\n")
    else:
        print(f"{RED}❌ Multiple tests failed. Review the implementation.{RESET}\n")

    return percentage >= 80

if __name__ == "__main__":
    base_url = "http://127.0.0.1:8001"

    if len(sys.argv) > 1:
        base_url = sys.argv[1]

    print(f"Testing server at: {base_url}")
    print("Make sure the server is running: uvicorn main:app --port 8001\n")

    # Wait a moment for the server
    time.sleep(1)

    success = run_all_tests(base_url)
    sys.exit(0 if success else 1)
