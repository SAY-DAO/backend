import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

let dashboardErrorRate = new Rate("Dashboard errors");
let DashboardTrend = new Trend("dashboard");

export let options = {
  thresholds: {
    "Dashboard Users": ["p(95)<500"],
  }
};

export default function() {
  let urlDashboard = "http://0.0.0.0:5000/api/v2/dashboard";
  let params = {
    headers: {
      Authorization:
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MDIzNTQ1MzEsIm5iZiI6MTYwMjM1NDUzMSwianRpIjoiMGYzYTUwYzItNjk1Zi00M2ViLThhNzEtNGQzYjk3NzA5YjA4IiwiZXhwIjoxNjAyNDQwOTMxLCJpZGVudGl0eSI6MTI2LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJ1c2VybmFtZSI6InJob25pbiIsImZpcnN0TmFtZSI6Ilx1MDYyMlx1MDYzMVx1MDYzNCIsImxhc3ROYW1lIjoiXHUwNjQxXHUwNjJhXHUwNjI3XHUwNjJkXHUyMDBjXHUwNjMyXHUwNjI3XHUwNjJmXHUwNjQ3IiwiYXZhdGFyVXJsIjoiL2ZpbGVzLzEyNi11c2VyLzEyNjU4NDQwLWF2YXRhcl8xMjYucG5nIn19.vYhJLYcuo4VN0l1RT2RCfY0OQUxoXBuCLTgu1hVn5KE",
    },
  };

  let requests = {
    "Get Dashboard": {
      method: "GET",
      url: urlDashboard,
      params: params,
    },
  };

  let responses = http.batch(requests);
  let dashboardResp = responses["Get Dashboard"];

  check(dashboardResp, {
    "status is 200": (r) => r.status === 200
  }) || dashboardErrorRate.add(1);

  DashboardTrend.add(dashboardResp.timings.duration);

  sleep(1);
};