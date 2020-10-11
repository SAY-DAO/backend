import http, { request } from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

export let options = {
  vus: 3,
  duration: "1m",

  thresholds: {
    http_req_duration: ["p(95)<1000"],
  },
};

const BASE_URL = __ENV.BASE_URL || "http://0.0.0.0:5000";
const SLEEP_DURATION = 0.1;

const APIS = {
  dashboard: {
    url: "/api/v2/dashboard",
    method: "GET",
  },
  randomSearch: {
    url: "/api/v2/search/random",
    method: "POST",
  },
  getChild: {
    url: "/api/v2/child/childId=1&confirm=2",
    method: "GET",
  },
  userChildren: {
    url: "/api/v2/user/children/userId=me",
    method: "GET",
  },
  childNeeds: {
    url: "/api/v2/child/childId=69/needs",
    method: "GET",
  },
};

Object.keys(APIS).map(function (api, index) {
  APIS[api].params = {};
  APIS[api].url = BASE_URL + APIS[api].url;
  APIS[api].trend = new Trend(api);
  APIS[api].errors = new Rate(api);
});

export default function () {
  const loginUrl = BASE_URL + "/api/v2/auth/login?_lang=fa";

  const loginResp = http.post(loginUrl, {
    username: "rhonin",
    password: 2,
    isInstalled: 1,
  });
  const token = loginResp.json().accessToken;

  Object.keys(APIS).map(function (api, index) {
    if (APIS[api].params.headers) {
      APIS[api].params.headers.Authorization = token;
    } else {
      APIS[api].params.headers = { Authorization: token };
    }
  });

  const responses = http.batch(APIS);

  Object.keys(responses).map(function (api, index) {
    check(responses[api], {
      "status is 200": (r) => r.status === 200,
    }) || APIS[api].errors.add(1);

    APIS[api].trend.add(responses[api].timings.duration);
  });

  sleep(SLEEP_DURATION);
}
