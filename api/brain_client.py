"""
WorldQuant Brain REST API Client.
Handles authentication, data field discovery, asynchronous simulation submission,
backtest polling, submission checks, and alpha submission.
Uses standard Python library (urllib.request, http.cookiejar, json) for maximum portability.
"""

import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar
import json
import base64
import time
import os
from typing import Dict, Any, List, Optional
from config import BRAIN_API_BASE_URL, CREDENTIALS_PATH, DEFAULT_SIMULATION_SETTINGS

class BrainClient:
    """WorldQuant Brain Platform REST API Interface."""

    def __init__(self, credentials_path: str = CREDENTIALS_PATH):
        self.base_url = BRAIN_API_BASE_URL
        self.credentials_path = credentials_path
        self.cookie_jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(self.cookie_jar)
        )
        self.authenticated = False
        self.username = None
        self._load_saved_credentials()

    def _load_saved_credentials(self):
        """Load email/password from local file if exists."""
        if os.path.exists(self.credentials_path):
            try:
                with open(self.credentials_path, "r") as f:
                    data = json.load(f)
                    self.username = data.get("username")
                    self.password = data.get("password")
            except Exception:
                pass

    def save_credentials(self, username: str, password: str):
        """Store credentials locally."""
        self.username = username
        self.password = password
        with open(self.credentials_path, "w") as f:
            json.dump({"username": username, "password": password}, f)
        print(f"Credentials saved to {self.credentials_path}")

    def authenticate(self, username: Optional[str] = None, password: Optional[str] = None) -> bool:
        """Authenticate with WorldQuant Brain API."""
        user = username or self.username
        pwd = password or getattr(self, "password", None)

        if not user or not pwd:
            print("No Brain credentials available. Please provide username and password.")
            return False

        auth_url = f"{self.base_url}/authentication"
        req = urllib.request.Request(auth_url, method="POST")
        
        # WorldQuant Brain accepts HTTP Basic Auth on /authentication
        auth_str = f"{user}:{pwd}"
        b64_auth = base64.b64encode(auth_str.encode("utf-8")).decode("utf-8")
        req.add_header("Authorization", f"Basic {b64_auth}")
        req.add_header("Content-Type", "application/json")
        req.data = b"{}"

        try:
            with self.opener.open(req) as resp:
                if resp.status in (200, 201):
                    self.authenticated = True
                    self.username = user
                    print(f"Successfully authenticated with WorldQuant Brain as {user}")
                    return True
                else:
                    print(f"Authentication returned status {resp.status}")
                    return False
        except urllib.error.HTTPError as e:
            print(f"Brain Authentication Failed: HTTP {e.code} - {e.reason}")
            try:
                err_body = e.read().decode("utf-8")
                print(f"Details: {err_body}")
            except Exception:
                pass
            return False
        except Exception as e:
            print(f"Connection error to Brain API: {e}")
            return False

    def search_data_fields(self, search: str, region: str = "USA", universe: str = "TOP3000", limit: int = 20) -> List[Dict[str, Any]]:
        """Search available datasets and fields on WorldQuant Brain."""
        params = {
            "instrumentType": "EQUITY",
            "region": region,
            "delay": "1",
            "universe": universe,
            "limit": str(limit),
            "search": search
        }
        query_string = urllib.parse.urlencode(params)
        url = f"{self.base_url}/data-fields?{query_string}"

        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")

        try:
            with self.opener.open(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                results = data.get("results", data)
                return results if isinstance(results, list) else []
        except Exception as e:
            print(f"Error searching data fields: {e}")
            return []

    def submit_simulation(self, formula: str, settings: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Submit an alpha for simulation.
        Returns the simulation ID or None if failed.
        """
        if not self.authenticated:
            if not self.authenticate():
                print("Must be authenticated to run live simulations.")
                return None

        sim_settings = DEFAULT_SIMULATION_SETTINGS.copy()
        if settings:
            sim_settings.update(settings)

        payload = {
            "type": "REGULAR",
            "settings": sim_settings,
            "regular": formula.strip()
        }

        url = f"{self.base_url}/simulations"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.data = json.dumps(payload).encode("utf-8")

        try:
            with self.opener.open(req) as resp:
                # WQ Brain returns 201 Created with Location header or JSON
                location = resp.headers.get("Location")
                if location:
                    sim_id = location.rstrip("/").split("/")[-1]
                    return sim_id
                
                body = resp.read().decode("utf-8")
                if body:
                    data = json.loads(body)
                    sim_id = data.get("id") or data.get("simulation")
                    return sim_id
                return None
        except urllib.error.HTTPError as e:
            print(f"Simulation submission HTTP Error {e.code}: {e.reason}")
            try:
                print(e.read().decode("utf-8"))
            except Exception:
                pass
            return None
        except Exception as e:
            print(f"Simulation error: {e}")
            return None

    def poll_simulation(self, sim_id: str, max_wait_sec: int = 300, poll_interval: int = 5) -> Optional[Dict[str, Any]]:
        """
        Poll simulation until finished.
        Returns full results dictionary when complete.
        """
        url = f"{self.base_url}/simulations/{sim_id}"
        start_time = time.time()

        print(f"Monitoring simulation {sim_id}...")
        while time.time() - start_time < max_wait_sec:
            req = urllib.request.Request(url, method="GET")
            req.add_header("Accept", "application/json")

            try:
                with self.opener.open(req) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    status = data.get("status", "").upper()
                    progress = data.get("progress", 0)

                    if status == "COMPLETE":
                        print(f"\nSimulation {sim_id} Complete!")
                        alpha_id = data.get("alpha")
                        if alpha_id:
                            return self.get_alpha_details(alpha_id, sim_id=sim_id)
                        return {"status": "COMPLETE", "raw": data, "sim_id": sim_id}
                    elif status in ("ERROR", "FAIL", "FAILED"):
                        print(f"\nSimulation {sim_id} Failed: {data.get('message', 'Unknown error')}")
                        return {"status": "ERROR", "message": data.get("message"), "sim_id": sim_id}
                    else:
                        print(f"\rProgress: {progress * 100:.1f}% ({status})...", end="", flush=True)

            except Exception as e:
                print(f"\nPolling error: {e}")

            time.sleep(poll_interval)

        print("\nSimulation polling timed out.")
        return None

    def get_alpha_details(self, alpha_id: str, sim_id: Optional[str] = None) -> Dict[str, Any]:
        """Fetch backtest metrics and submission readiness for an alpha."""
        url = f"{self.base_url}/alphas/{alpha_id}"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")

        try:
            with self.opener.open(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                is_stats = data.get("is", {})
                
                # Check submission readiness
                checks = self.check_submission(alpha_id)

                return {
                    "brain_alpha_id": alpha_id,
                    "brain_sim_id": sim_id,
                    "sharpe": is_stats.get("sharpe"),
                    "turnover": is_stats.get("turnover"),
                    "fitness": is_stats.get("fitness"),
                    "returns": is_stats.get("returns"),
                    "margin_bps": (is_stats.get("margin", 0.0) * 10000) if is_stats.get("margin") is not None else None,
                    "max_drawdown": is_stats.get("drawdown"),
                    "sub_universe_passed": checks.get("sub_universe_passed", False),
                    "submission_ready": checks.get("can_submit", False),
                    "checks": checks,
                    "raw": data
                }
        except Exception as e:
            print(f"Error fetching alpha details: {e}")
            return {"brain_alpha_id": alpha_id, "error": str(e)}

    def check_submission(self, alpha_id: str) -> Dict[str, Any]:
        """Verify whether an alpha passes Brain's official submission requirements."""
        url = f"{self.base_url}/alphas/{alpha_id}/check"
        req = urllib.request.Request(url, method="GET")
        req.add_header("Accept", "application/json")

        try:
            with self.opener.open(req) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                checks = data.get("checks", [])
                
                sub_pass = True
                can_submit = True
                
                for c in checks:
                    if c.get("name") == "SUB_UNIVERSE_SHARPE" and c.get("result") != "PASS":
                        sub_pass = False
                    if c.get("result") not in ("PASS", "WARNING"):
                        can_submit = False

                return {
                    "can_submit": can_submit,
                    "sub_universe_passed": sub_pass,
                    "checks_detail": checks,
                    "raw": data
                }
        except Exception as e:
            return {"can_submit": False, "sub_universe_passed": False, "error": str(e)}

    def submit_alpha(self, alpha_id: str) -> bool:
        """Officially submit a passing alpha to WorldQuant Brain."""
        url = f"{self.base_url}/alphas/{alpha_id}/submit"
        req = urllib.request.Request(url, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Accept", "application/json")
        req.data = b"{}"

        try:
            with self.opener.open(req) as resp:
                if resp.status in (200, 201):
                    print(f"Alpha {alpha_id} successfully submitted!")
                    return True
                else:
                    print(f"Submission status: {resp.status}")
                    return False
        except urllib.error.HTTPError as e:
            print(f"Submission failed: HTTP {e.code} - {e.reason}")
            try:
                print(e.read().decode("utf-8"))
            except Exception:
                pass
            return False
        except Exception as e:
            print(f"Submission error: {e}")
            return False

