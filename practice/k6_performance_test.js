import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

let dashboardErrorRate = new Rate("Dashboard errors");
let DashboardTrend = new Trend("dashboard");

let randomSearchErrorRate = new Rate("Random Search errors");
let RandomSearchTrend = new Trend("randomSearch");

let getChildErrorRate = new Rate("Get Child errors");
let GetChildTrend = new Trend("getChild");


export default function() {
  let urlDashboard = "https://sayapp.company/api/v2/dashboard";
  let urlRandomSearch = "https://sayapp.company/api/v2/search/random";
  let urlGetChild = "https://sayapp.company/api/v2/child/childId=37&confirm=2";

  let params = {
    headers: {
      "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE1ODEwMDM5OTMsIm5iZiI6MTU4MTAwMzk5MywianRpIjoiNGUzZjhlOWQtZGQyNi00MjQyLTkwMmQtNTI5Y2ViODM2ZmQxIiwiZXhwIjoxNTgxMDkwMzkzLCJpZGVudGl0eSI6MTI2LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJ1c2VybmFtZSI6InJob25pbiIsImZpcnN0TmFtZSI6IkFyYXNoIiwibGFzdE5hbWUiOiJGYXRhaHphZGUiLCJhdmF0YXJVcmwiOm51bGx9fQ.xS1b2dRhgkE8emZAF8uE243Z6NObu-D8w_8U9ickPS4",
    }
  };

  let requests = {
    "Dashboard": {
      method: "GET",
      url: urlDashboard,
      params: params,
    },
    "Random Search": {
      method: "GET",
      url: urlRandomSearch,
      params: params,
    },
    "Get Child": {
      method: "GET",
      url: urlGetChild,
      params: params,
    },
  };

  let responses = http.batch(requests);
  let dashboardResp = responses["Dashboard"];
  let randomSearchResp = responses["Random Search"];
  let getChildResp = responses["Get Child"];

  check(dashboardResp, {
    "status is 200": (r) => r.status === 200
  }) || dashboardErrorRate.add(1);

  DashboardTrend.add(dashboardResp.timings.duration);

  check(randomSearchResp, {
    "status is 200": (r) => r.status === 200
  }) || randomSearchErrorRate.add(1);

  RandomSearchTrend.add(randomSearchResp.timings.duration);

  check(getChildResp, {
    "status is 200": (r) => r.status === 200
  }) || getChildErrorRate.add(1);

  GetChildTrend.add(getChildResp.timings.duration);

  sleep(1);
};