import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

let childErrorRate = new Rate("Child errors");
let ChildTrend = new Trend("Child");

export let options = {
  thresholds: {
    "Child Users": ["p(95)<500"],
  },
};

export default function () {
  let urlChild =
    "http://0.0.0.0:5000/api/v2/child/childId=70&confirm=1?_lang=fa";
  let params = {
    headers: {
      Authorization:
        "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpYXQiOjE2MDIzNTQ1MzEsIm5iZiI6MTYwMjM1NDUzMSwianRpIjoiMGYzYTUwYzItNjk1Zi00M2ViLThhNzEtNGQzYjk3NzA5YjA4IiwiZXhwIjoxNjAyNDQwOTMxLCJpZGVudGl0eSI6MTI2LCJmcmVzaCI6ZmFsc2UsInR5cGUiOiJhY2Nlc3MiLCJ1c2VyX2NsYWltcyI6eyJ1c2VybmFtZSI6InJob25pbiIsImZpcnN0TmFtZSI6Ilx1MDYyMlx1MDYzMVx1MDYzNCIsImxhc3ROYW1lIjoiXHUwNjQxXHUwNjJhXHUwNjI3XHUwNjJkXHUyMDBjXHUwNjMyXHUwNjI3XHUwNjJmXHUwNjQ3IiwiYXZhdGFyVXJsIjoiL2ZpbGVzLzEyNi11c2VyLzEyNjU4NDQwLWF2YXRhcl8xMjYucG5nIn19.vYhJLYcuo4VN0l1RT2RCfY0OQUxoXBuCLTgu1hVn5KE",
    },
  };

  let requests = {
    "Get Child": {
      method: "GET",
      url: urlChild,
      params: params,
    },
  };

  let responses = http.batch(requests);
  let childResp = responses["Get Child"];

  check(childResp, {
    "status is 200": (r) => r.status === 200,
  }) || childErrorRate.add(1);

  ChildTrend.add(childResp.timings.duration);

  sleep(1);
}
