"""Real API server implementations for Mixpanel, PostHog, Jira, Confluence, Salesforce."""

import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx

from ..utils.config import config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class RealServerBase:
    """Base class for real API server implementations."""

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        self.name = server_name
        self.config = server_config
        self.capabilities = server_config.get("capabilities", [])

    def call_tool(self, capability: str, params: Dict[str, Any]) -> Dict[str, Any]:
        if capability not in self.capabilities:
            raise ValueError(f"Capability {capability} not supported by {self.name}")
        method_name = f"api_{capability}"
        if hasattr(self, method_name):
            try:
                return getattr(self, method_name)(params)
            except Exception as e:
                logger.error(f"Error calling {self.name}.{capability}: {e}")
                return {"error": str(e)}
        return {"error": f"Method {method_name} not implemented"}


# ---------------------------------------------------------------------------
# Mixpanel - REST API
# Docs: https://developer.mixpanel.com/reference
# ---------------------------------------------------------------------------

class RealMixpanelServer(RealServerBase):
    """Real Mixpanel API integration."""

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        super().__init__(server_name, server_config)
        self.project_id = config.mixpanel_project_id
        self.api_secret = config.mixpanel_api_secret
        self.base_url = "https://mixpanel.com/api"
        self.data_url = "https://data.mixpanel.com/api/2.0"
        self.eu = config.mixpanel_eu  # EU residency

        if self.eu:
            self.base_url = "https://eu.mixpanel.com/api"
            self.data_url = "https://data-eu.mixpanel.com/api/2.0"

    def _headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Basic {self.api_secret}",
        }

    def _get(self, url: str, params: Optional[Dict] = None) -> Dict:
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers(), params=params or {})
            resp.raise_for_status()
            return resp.json()

    def _post(self, url: str, payload: Optional[Dict] = None) -> Dict:
        with httpx.Client(timeout=30) as client:
            resp = client.post(url, headers=self._headers(), json=payload or {})
            resp.raise_for_status()
            return resp.json()

    def api_query_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Query top events from last 30 days."""
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        url = f"{self.base_url}/2.0/insights"
        query_params = {
            "project_id": self.project_id,
            "bookmark": json.dumps({
                "sections": {
                    "show": [{
                        "dataset": "$mixpanel",
                        "value": {"name": "", "resourceType": "events"},
                        "resourceType": "events",
                        "profileType": "events",
                        "search": "",
                        "math": "total",
                    }]
                },
                "time": {"dateRange": "30d"},
            }),
        }

        # Fallback: use the segmentation endpoint which is simpler
        seg_url = f"{self.base_url}/2.0/segmentation"
        try:
            # Try to get top events via the events endpoint
            events_url = f"{self.base_url}/2.0/events/top"
            data = self._get(events_url, {
                "project_id": self.project_id,
                "limit": 10,
            })
            events = []
            for name, info in data.get("events", {}).items():
                events.append({"name": name, "count": info.get("total", 0)})
            return {"events": events, "date_range": f"{from_date} to {to_date}"}
        except Exception as e:
            logger.warning(f"Mixpanel events fallback: {e}")
            # Return minimal data on failure
            return {"events": [], "date_range": f"{from_date} to {to_date}", "error": str(e)}

    def api_get_user_metrics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get user engagement metrics."""
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        try:
            # Engage endpoint for user counts
            url = f"{self.base_url}/2.0/engage"
            data = self._get(url, {
                "project_id": self.project_id,
                "page_size": 0,
            })
            total_users = data.get("total", 0)

            return {
                "total_users": total_users,
                "date_range": f"{from_date} to {to_date}",
            }
        except Exception as e:
            logger.warning(f"Mixpanel user metrics fallback: {e}")
            return {"total_users": 0, "error": str(e)}

    def api_get_funnel_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get funnel data. Requires funnel_id in params or uses first available."""
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        try:
            # List funnels
            list_url = f"{self.base_url}/2.0/funnels/list"
            funnels = self._get(list_url, {"project_id": self.project_id})

            if not funnels:
                return {"funnel_name": "No funnels found", "steps": []}

            funnel_id = params.get("funnel_id") or funnels[0].get("funnel_id")
            funnel_name = funnels[0].get("name", "Funnel")

            # Get funnel data
            url = f"{self.base_url}/2.0/funnels"
            data = self._get(url, {
                "project_id": self.project_id,
                "funnel_id": funnel_id,
                "from_date": from_date,
                "to_date": to_date,
            })

            steps = []
            for step in data.get("data", {}).get("steps", []):
                steps.append({
                    "step": step.get("event"),
                    "users": step.get("count", 0),
                    "conversion": step.get("step_conv_ratio", 0),
                })

            return {"funnel_name": funnel_name, "steps": steps}
        except Exception as e:
            logger.warning(f"Mixpanel funnel fallback: {e}")
            return {"funnel_name": "Error", "steps": [], "error": str(e)}

    def api_get_retention_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get retention data."""
        to_date = datetime.now().strftime("%Y-%m-%d")
        from_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")

        try:
            url = f"{self.base_url}/2.0/retention"
            data = self._get(url, {
                "project_id": self.project_id,
                "from_date": from_date,
                "to_date": to_date,
                "born_event": params.get("born_event", ""),
                "event": params.get("event", ""),
                "unit": "day",
            })

            retention = {}
            for entry in data.get("data", []):
                counts = entry.get("counts", [])
                if len(counts) > 1:
                    base = counts[0] if counts[0] > 0 else 1
                    if len(counts) > 1:
                        retention["day_1"] = round(counts[1] / base, 2) if len(counts) > 1 else 0
                    if len(counts) > 7:
                        retention["day_7"] = round(counts[7] / base, 2)
                    if len(counts) > 30:
                        retention["day_30"] = round(counts[30] / base, 2)

            return {"retention": retention}
        except Exception as e:
            logger.warning(f"Mixpanel retention fallback: {e}")
            return {"retention": {}, "error": str(e)}


# ---------------------------------------------------------------------------
# PostHog - REST API
# Docs: https://posthog.com/docs/api
# ---------------------------------------------------------------------------

class RealPostHogServer(RealServerBase):
    """Real PostHog API integration."""

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        super().__init__(server_name, server_config)
        self.api_key = config.posthog_api_key
        self.project_id = config.posthog_project_id
        self.host = config.posthog_host  # e.g. https://app.posthog.com

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"{self.host}/api/projects/{self.project_id}{path}"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers(), params=params or {})
            resp.raise_for_status()
            return resp.json()

    def api_query_events(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent events summary."""
        try:
            # Get event definitions to see what's tracked
            data = self._get("/event_definitions", {"limit": 20})
            events = []
            for ev in data.get("results", []):
                events.append({
                    "event": ev.get("name"),
                    "count": ev.get("query_usage_30_day", 0),
                    "volume": ev.get("volume_30_day", 0),
                })
            return {"events": events}
        except Exception as e:
            logger.warning(f"PostHog events fallback: {e}")
            return {"events": [], "error": str(e)}

    def api_get_feature_flags(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get feature flags."""
        try:
            data = self._get("/feature_flags", {"limit": 50})
            flags = []
            for flag in data.get("results", []):
                flags.append({
                    "name": flag.get("key"),
                    "enabled": flag.get("active", False),
                    "rollout": flag.get("rollout_percentage", 0),
                    "filters": flag.get("filters", {}),
                })
            return {"flags": flags}
        except Exception as e:
            logger.warning(f"PostHog feature flags fallback: {e}")
            return {"flags": [], "error": str(e)}

    def api_get_session_recordings(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get recent session recordings summary."""
        try:
            data = self._get("/session_recordings", {"limit": 10})
            recordings = []
            for rec in data.get("results", []):
                recordings.append({
                    "id": rec.get("id"),
                    "duration": rec.get("recording_duration"),
                    "start_time": rec.get("start_time"),
                    "person": rec.get("person", {}).get("distinct_ids", [None])[0],
                })
            return {"recordings": recordings, "total": data.get("count", 0)}
        except Exception as e:
            logger.warning(f"PostHog recordings fallback: {e}")
            return {"recordings": [], "error": str(e)}

    def api_get_user_cohorts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get cohorts."""
        try:
            data = self._get("/cohorts")
            cohorts = []
            for c in data.get("results", []):
                cohorts.append({
                    "name": c.get("name"),
                    "count": c.get("count", 0),
                    "created_at": c.get("created_at"),
                })
            return {"cohorts": cohorts}
        except Exception as e:
            logger.warning(f"PostHog cohorts fallback: {e}")
            return {"cohorts": [], "error": str(e)}


# ---------------------------------------------------------------------------
# Jira - REST API v3 (Cloud)
# Docs: https://developer.atlassian.com/cloud/jira/platform/rest/v3/
# ---------------------------------------------------------------------------

class RealJiraServer(RealServerBase):
    """Real Jira API integration."""

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        super().__init__(server_name, server_config)
        self.domain = config.jira_domain  # e.g. yourcompany.atlassian.net
        self.email = config.jira_email
        self.api_token = config.jira_api_token
        self.project_key = config.jira_project_key

    def _headers(self) -> Dict[str, str]:
        import base64
        creds = base64.b64encode(f"{self.email}:{self.api_token}".encode()).decode()
        return {
            "Authorization": f"Basic {creds}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"https://{self.domain}/rest/api/3{path}"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers(), params=params or {})
            resp.raise_for_status()
            return resp.json()

    def api_get_issues(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get issue summary for the project."""
        try:
            jql = f"project = {self.project_key} ORDER BY updated DESC"
            data = self._get("/search", {
                "jql": jql,
                "maxResults": 0,
                "fields": "summary",
            })
            total = data.get("total", 0)

            # Get issue type counts
            type_counts = {}
            for itype in ["Bug", "Story", "Task", "Epic"]:
                jql_type = f"project = {self.project_key} AND issuetype = {itype}"
                d = self._get("/search", {"jql": jql_type, "maxResults": 0})
                type_counts[itype.lower()] = d.get("total", 0)

            # Open issues
            jql_open = f"project = {self.project_key} AND status != Done"
            d_open = self._get("/search", {"jql": jql_open, "maxResults": 0})

            # In progress
            jql_prog = f'project = {self.project_key} AND status = "In Progress"'
            d_prog = self._get("/search", {"jql": jql_prog, "maxResults": 0})

            return {
                "total_issues": total,
                "open_issues": d_open.get("total", 0),
                "in_progress": d_prog.get("total", 0),
                "by_type": type_counts,
            }
        except Exception as e:
            logger.warning(f"Jira issues fallback: {e}")
            return {"total_issues": 0, "error": str(e)}

    def api_get_sprint_data(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get current sprint data."""
        try:
            # Find the board
            boards = self._get(
                f"/board",
                {"projectKeyOrId": self.project_key, "maxResults": 1}
            )
            # Jira Agile uses a different base URL
            board_url = f"https://{self.domain}/rest/agile/1.0"

            with httpx.Client(timeout=30) as client:
                # Get boards
                resp = client.get(
                    f"{board_url}/board",
                    headers=self._headers(),
                    params={"projectKeyOrId": self.project_key, "maxResults": 1},
                )
                resp.raise_for_status()
                boards_data = resp.json()

                if not boards_data.get("values"):
                    return {"current_sprint": "No board found", "error": "No board"}

                board_id = boards_data["values"][0]["id"]

                # Get active sprint
                resp = client.get(
                    f"{board_url}/board/{board_id}/sprint",
                    headers=self._headers(),
                    params={"state": "active"},
                )
                resp.raise_for_status()
                sprints = resp.json()

                if not sprints.get("values"):
                    return {"current_sprint": "No active sprint"}

                sprint = sprints["values"][0]
                sprint_id = sprint["id"]

                # Get sprint issues
                resp = client.get(
                    f"{board_url}/sprint/{sprint_id}/issue",
                    headers=self._headers(),
                    params={"maxResults": 100},
                )
                resp.raise_for_status()
                issues = resp.json()

                done_count = sum(
                    1 for i in issues.get("issues", [])
                    if i.get("fields", {}).get("status", {}).get("statusCategory", {}).get("key") == "done"
                )

                return {
                    "current_sprint": sprint.get("name"),
                    "total_issues": issues.get("total", 0),
                    "completed": done_count,
                    "start_date": sprint.get("startDate"),
                    "end_date": sprint.get("endDate"),
                }
        except Exception as e:
            logger.warning(f"Jira sprint fallback: {e}")
            return {"current_sprint": "Error", "error": str(e)}

    def api_get_backlog(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get top backlog items by priority."""
        try:
            jql = (
                f"project = {self.project_key} AND status = Backlog "
                f"ORDER BY priority ASC, votes DESC"
            )
            data = self._get("/search", {
                "jql": jql,
                "maxResults": 20,
                "fields": "summary,priority,votes,issuetype",
            })

            items = []
            for issue in data.get("issues", []):
                fields = issue.get("fields", {})
                items.append({
                    "key": issue.get("key"),
                    "summary": fields.get("summary"),
                    "priority": fields.get("priority", {}).get("name"),
                    "votes": fields.get("votes", {}).get("votes", 0),
                    "type": fields.get("issuetype", {}).get("name"),
                })

            return {"total_items": data.get("total", 0), "top_priority": items}
        except Exception as e:
            logger.warning(f"Jira backlog fallback: {e}")
            return {"total_items": 0, "top_priority": [], "error": str(e)}

    def api_get_velocity(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get velocity data from recent sprints."""
        try:
            board_url = f"https://{self.domain}/rest/agile/1.0"
            with httpx.Client(timeout=30) as client:
                resp = client.get(
                    f"{board_url}/board",
                    headers=self._headers(),
                    params={"projectKeyOrId": self.project_key, "maxResults": 1},
                )
                resp.raise_for_status()
                boards_data = resp.json()

                if not boards_data.get("values"):
                    return {"velocity": []}

                board_id = boards_data["values"][0]["id"]

                # Get closed sprints
                resp = client.get(
                    f"{board_url}/board/{board_id}/sprint",
                    headers=self._headers(),
                    params={"state": "closed", "maxResults": 5},
                )
                resp.raise_for_status()
                sprints = resp.json()

                velocity = []
                for sprint in sprints.get("values", []):
                    velocity.append({
                        "sprint": sprint.get("name"),
                        "completed_issues": sprint.get("completeDate") is not None,
                    })

                return {"velocity": velocity}
        except Exception as e:
            logger.warning(f"Jira velocity fallback: {e}")
            return {"velocity": [], "error": str(e)}


# ---------------------------------------------------------------------------
# Confluence - REST API v2 (Cloud)
# Docs: https://developer.atlassian.com/cloud/confluence/rest/v2/
# ---------------------------------------------------------------------------

class RealConfluenceServer(RealServerBase):
    """Real Confluence API integration."""

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        super().__init__(server_name, server_config)
        self.domain = config.confluence_domain  # same as jira domain usually
        self.email = config.confluence_email
        self.api_token = config.confluence_api_token
        self.space_key = config.confluence_space_key

    def _headers(self) -> Dict[str, str]:
        import base64
        creds = base64.b64encode(f"{self.email}:{self.api_token}".encode()).decode()
        return {
            "Authorization": f"Basic {creds}",
            "Accept": "application/json",
        }

    def _get(self, path: str, params: Optional[Dict] = None) -> Dict:
        url = f"https://{self.domain}/wiki/rest/api{path}"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers(), params=params or {})
            resp.raise_for_status()
            return resp.json()

    def api_search_pages(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search Confluence pages."""
        try:
            query = params.get("query", "product requirements")
            cql = f'space = "{self.space_key}" AND text ~ "{query}"'
            data = self._get("/content/search", {"cql": cql, "limit": 10})

            results = []
            for page in data.get("results", []):
                results.append({
                    "title": page.get("title"),
                    "id": page.get("id"),
                    "url": page.get("_links", {}).get("webui", ""),
                    "type": page.get("type"),
                })

            return {"results": results}
        except Exception as e:
            logger.warning(f"Confluence search fallback: {e}")
            return {"results": [], "error": str(e)}

    def api_get_product_docs(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get product documentation pages."""
        try:
            cql = f'space = "{self.space_key}" AND label = "product-doc"'
            data = self._get("/content/search", {"cql": cql, "limit": 20})

            pages = []
            for page in data.get("results", []):
                pages.append({
                    "title": page.get("title"),
                    "id": page.get("id"),
                    "last_modified": page.get("version", {}).get("when"),
                })

            return {"pages": pages}
        except Exception as e:
            logger.warning(f"Confluence docs fallback: {e}")
            return {"pages": [], "error": str(e)}

    def api_get_requirements(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get requirement documents."""
        try:
            cql = f'space = "{self.space_key}" AND (label = "requirement" OR label = "prd" OR title ~ "requirement")'
            data = self._get("/content/search", {"cql": cql, "limit": 20})

            requirements = []
            for page in data.get("results", []):
                requirements.append({
                    "id": page.get("id"),
                    "title": page.get("title"),
                    "url": page.get("_links", {}).get("webui", ""),
                    "status": page.get("status", "current"),
                })

            return {"requirements": requirements}
        except Exception as e:
            logger.warning(f"Confluence requirements fallback: {e}")
            return {"requirements": [], "error": str(e)}

    def api_get_user_stories(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get user story documents."""
        try:
            cql = f'space = "{self.space_key}" AND (label = "user-story" OR title ~ "user story")'
            data = self._get("/content/search", {"cql": cql, "limit": 20})

            stories = []
            for page in data.get("results", []):
                stories.append({
                    "title": page.get("title"),
                    "id": page.get("id"),
                })

            return {"stories": stories}
        except Exception as e:
            logger.warning(f"Confluence stories fallback: {e}")
            return {"stories": [], "error": str(e)}


# ---------------------------------------------------------------------------
# Salesforce - REST API
# Docs: https://developer.salesforce.com/docs/atlas.en-us.api_rest.meta
# ---------------------------------------------------------------------------

class RealSalesforceServer(RealServerBase):
    """Real Salesforce API integration."""

    def __init__(self, server_name: str, server_config: Dict[str, Any]):
        super().__init__(server_name, server_config)
        self.instance_url = config.salesforce_instance_url  # e.g. https://yourcompany.salesforce.com
        self.access_token = config.salesforce_access_token
        self._token = None

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    def _query(self, soql: str) -> Dict:
        url = f"{self.instance_url}/services/data/v59.0/query"
        with httpx.Client(timeout=30) as client:
            resp = client.get(url, headers=self._headers(), params={"q": soql})
            resp.raise_for_status()
            return resp.json()

    def api_get_opportunities(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get opportunity pipeline data."""
        try:
            data = self._query(
                "SELECT Id, Name, Amount, StageName, Probability, Account.Name, CloseDate "
                "FROM Opportunity WHERE IsClosed = false ORDER BY Amount DESC LIMIT 20"
            )
            total_data = self._query(
                "SELECT COUNT(Id) total, SUM(Amount) total_value FROM Opportunity WHERE IsClosed = false"
            )
            won_data = self._query(
                "SELECT COUNT(Id) total FROM Opportunity WHERE IsWon = true AND CloseDate = THIS_YEAR"
            )
            lost_data = self._query(
                "SELECT COUNT(Id) total FROM Opportunity WHERE IsWon = false AND IsClosed = true AND CloseDate = THIS_YEAR"
            )

            opps = []
            for rec in data.get("records", []):
                opps.append({
                    "account": rec.get("Account", {}).get("Name", "Unknown"),
                    "value": f"${rec.get('Amount', 0):,.0f}" if rec.get("Amount") else "$0",
                    "stage": rec.get("StageName"),
                    "probability": rec.get("Probability"),
                    "close_date": rec.get("CloseDate"),
                })

            summary = total_data.get("records", [{}])[0] if total_data.get("records") else {}
            won = won_data.get("records", [{}])[0].get("total", 0) if won_data.get("records") else 0
            lost = lost_data.get("records", [{}])[0].get("total", 0) if lost_data.get("records") else 0
            win_rate = round(won / (won + lost), 2) if (won + lost) > 0 else 0

            return {
                "total_opportunities": summary.get("total", 0),
                "total_value": f"${summary.get('total_value', 0):,.0f}" if summary.get("total_value") else "$0",
                "win_rate": win_rate,
                "top_opportunities": opps[:5],
            }
        except Exception as e:
            logger.warning(f"Salesforce opportunities fallback: {e}")
            return {"total_opportunities": 0, "error": str(e)}

    def api_get_accounts(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get key accounts."""
        try:
            data = self._query(
                "SELECT Id, Name, Industry, AnnualRevenue, NumberOfEmployees "
                "FROM Account ORDER BY AnnualRevenue DESC NULLS LAST LIMIT 10"
            )
            accounts = []
            for rec in data.get("records", []):
                accounts.append({
                    "name": rec.get("Name"),
                    "industry": rec.get("Industry"),
                    "revenue": rec.get("AnnualRevenue"),
                    "employees": rec.get("NumberOfEmployees"),
                })
            return {"accounts": accounts}
        except Exception as e:
            logger.warning(f"Salesforce accounts fallback: {e}")
            return {"accounts": [], "error": str(e)}

    def api_get_win_loss_reasons(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get win/loss reason analysis from closed opportunities."""
        try:
            # Won deals
            won = self._query(
                "SELECT Id, Name, Description FROM Opportunity "
                "WHERE IsWon = true AND CloseDate = THIS_YEAR LIMIT 20"
            )
            # Lost deals
            lost = self._query(
                "SELECT Id, Name, Description, StageName FROM Opportunity "
                "WHERE IsWon = false AND IsClosed = true AND CloseDate = THIS_YEAR LIMIT 20"
            )

            return {
                "won_deals": len(won.get("records", [])),
                "lost_deals": len(lost.get("records", [])),
                "recent_wins": [r.get("Name") for r in won.get("records", [])[:5]],
                "recent_losses": [r.get("Name") for r in lost.get("records", [])[:5]],
            }
        except Exception as e:
            logger.warning(f"Salesforce win/loss fallback: {e}")
            return {"won_deals": 0, "lost_deals": 0, "error": str(e)}

    def api_get_customer_feedback(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get customer feedback from cases or custom objects."""
        try:
            # Use Case object as feedback proxy
            data = self._query(
                "SELECT Id, Subject, Description, Status, Priority, Account.Name "
                "FROM Case WHERE Status != 'Closed' ORDER BY CreatedDate DESC LIMIT 20"
            )
            feedback = []
            for rec in data.get("records", []):
                feedback.append({
                    "account": rec.get("Account", {}).get("Name", "Unknown"),
                    "subject": rec.get("Subject"),
                    "priority": rec.get("Priority"),
                    "status": rec.get("Status"),
                })
            return {"feedback": feedback}
        except Exception as e:
            logger.warning(f"Salesforce feedback fallback: {e}")
            return {"feedback": [], "error": str(e)}


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

def create_real_server(server_name: str, server_config: Dict[str, Any]) -> RealServerBase:
    """Create appropriate real server based on server name."""
    server_map = {
        "mixpanel": RealMixpanelServer,
        "posthog": RealPostHogServer,
        "jira": RealJiraServer,
        "confluence": RealConfluenceServer,
        "salesforce": RealSalesforceServer,
    }
    server_class = server_map.get(server_name)
    if not server_class:
        raise ValueError(f"No real server implementation for: {server_name}")
    return server_class(server_name, server_config)
