"""
Site Monitor for dopamine.watch
Checks site health and performance
"""

import os
import json
import requests
from datetime import datetime


class SiteMonitor:
    """Monitor site health and performance"""

    def __init__(self):
        self.base_dir = os.path.dirname(__file__)
        self.log_dir = os.path.join(self.base_dir, "logs", "monitoring")
        os.makedirs(self.log_dir, exist_ok=True)

        self.urls_to_monitor = [
            ("Homepage", "https://dopamine.watch/"),
            ("Blog Homepage", "https://dopamine.watch/blog/"),
            ("Blog Post 1", "https://dopamine.watch/blog/posts/adhd-decision-paralysis-science.html"),
            ("Blog Post 2", "https://dopamine.watch/blog/posts/netflix-algorithm-not-built-for-adhd.html"),
            ("Blog Post 3", "https://dopamine.watch/blog/posts/shows-that-help-anxiety.html"),
            ("Sitemap", "https://dopamine.watch/blog/sitemap.xml"),
            ("Robots.txt", "https://dopamine.watch/robots.txt"),
            ("App", "https://app.dopamine.watch/"),
        ]

    def check_all_pages(self) -> bool:
        """Check if all pages are up"""

        print("\n" + "="*60)
        print("🔍 SITE HEALTH CHECK")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        all_up = True
        results = []

        for name, url in self.urls_to_monitor:
            result = self._check_url(name, url)
            results.append(result)
            if result['status'] != 'up':
                all_up = False

        # Summary
        if all_up:
            print("\n✅ ALL SYSTEMS OPERATIONAL")
        else:
            print("\n⚠️  ISSUES DETECTED - CHECK ABOVE")

        print("\n" + "="*60 + "\n")

        # Log results
        self._log_check(all_up, results)

        return all_up

    def _check_url(self, name: str, url: str) -> dict:
        """Check a single URL"""

        result = {
            "name": name,
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "status_code": None,
            "load_time": None,
            "error": None
        }

        try:
            response = requests.get(url, timeout=15)
            result['status_code'] = response.status_code
            result['load_time'] = response.elapsed.total_seconds()

            if response.status_code == 200:
                result['status'] = 'up'
                print(f"✅ {name}")
                print(f"   URL: {url}")
                print(f"   Status: {response.status_code} | Load: {result['load_time']:.2f}s")

                # Warn if slow
                if result['load_time'] > 3:
                    print(f"   ⚠️ Slow load time (> 3s)")

            else:
                result['status'] = 'error'
                print(f"❌ {name}")
                print(f"   URL: {url}")
                print(f"   Status: {response.status_code}")

        except requests.exceptions.Timeout:
            result['status'] = 'timeout'
            result['error'] = 'Request timed out'
            print(f"❌ {name}")
            print(f"   URL: {url}")
            print(f"   Error: Timeout (> 15s)")

        except requests.exceptions.ConnectionError as e:
            result['status'] = 'down'
            result['error'] = str(e)
            print(f"❌ {name}")
            print(f"   URL: {url}")
            print(f"   Error: Connection failed")

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"❌ {name}")
            print(f"   URL: {url}")
            print(f"   Error: {str(e)}")

        print()
        return result

    def _log_check(self, all_up: bool, results: list):
        """Log monitoring results"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": "up" if all_up else "issues",
            "checks": len(results),
            "up_count": sum(1 for r in results if r['status'] == 'up'),
            "results": results
        }

        log_file = os.path.join(self.log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json")

        logs = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)

        logs.append(log_entry)

        with open(log_file, 'w') as f:
            json.dump(logs, f, indent=2)

        print(f"📄 Results logged to: {log_file}")

    def check_single_url(self, url: str) -> dict:
        """Check a single URL"""

        print(f"\n🔍 Checking: {url}\n")
        return self._check_url("Custom URL", url)

    def get_uptime_report(self, days: int = 7) -> dict:
        """Generate uptime report for past N days"""

        print("\n" + "="*60)
        print(f"📊 UPTIME REPORT (Last {days} days)")
        print("="*60 + "\n")

        total_checks = 0
        up_checks = 0

        for i in range(days):
            from datetime import timedelta
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            log_file = os.path.join(self.log_dir, f"{date}.json")

            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)

                for log in logs:
                    total_checks += log['checks']
                    up_checks += log['up_count']

        if total_checks > 0:
            uptime = (up_checks / total_checks) * 100
            print(f"Total Checks: {total_checks}")
            print(f"Successful: {up_checks}")
            print(f"Uptime: {uptime:.2f}%")

            if uptime >= 99.9:
                print("🎉 Excellent uptime!")
            elif uptime >= 99:
                print("👍 Good uptime")
            elif uptime >= 95:
                print("⚠️ Some issues detected")
            else:
                print("🚨 Significant downtime")
        else:
            print("No monitoring data found for this period.")
            uptime = 0

        print("\n" + "="*60 + "\n")

        return {
            "days": days,
            "total_checks": total_checks,
            "up_checks": up_checks,
            "uptime_percent": uptime
        }


if __name__ == "__main__":
    import sys

    monitor = SiteMonitor()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--report":
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
            monitor.get_uptime_report(days)
        elif sys.argv[1] == "--url":
            if len(sys.argv) > 2:
                monitor.check_single_url(sys.argv[2])
            else:
                print("Usage: python monitor.py --url <URL>")
        else:
            print("Usage:")
            print("  python monitor.py           # Run health check")
            print("  python monitor.py --report  # Get uptime report")
            print("  python monitor.py --url URL # Check specific URL")
    else:
        monitor.check_all_pages()
