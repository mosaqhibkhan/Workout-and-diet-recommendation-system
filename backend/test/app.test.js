const { test, before, after, beforeEach } = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");

/* ─── Fake Flask ML service ───────────────────────────────────────────────── */

let mlHandler;
let mlRequests;
const mlServer = http.createServer((req, res) => {
  let body = "";
  req.on("data", (chunk) => (body += chunk));
  req.on("end", () => {
    mlRequests.push({ url: req.url, body: JSON.parse(body) });
    mlHandler(req, res, JSON.parse(body));
  });
});

const sendJson = (res, status, payload) => {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(payload));
};

const PREFIX = { Cut: "FatLoss", Bulk: "MuscleGain", Maintain: "Maintenance" };
const ruleHandler = (req, res, body) =>
  sendJson(res, 200, { plan: `${PREFIX[body.goal]}_${body.experience}` });

let server;
let baseUrl;
let WORKOUT_PLANS;
let DIET_PLANS;

before(async () => {
  await new Promise((resolve) => mlServer.listen(0, "127.0.0.1", resolve));
  process.env.ML_SERVICE_URL = `http://127.0.0.1:${mlServer.address().port}`;
  const mod = require("../app");
  ({ WORKOUT_PLANS, DIET_PLANS } = mod);
  await new Promise((resolve) => {
    server = mod.app.listen(0, "127.0.0.1", resolve);
  });
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(() => {
  server.close();
  mlServer.close();
});

beforeEach(() => {
  mlHandler = ruleHandler;
  mlRequests = [];
});

const VALID = { weight: 72, height: 175, goal: "Cut", experience: "Beginner" };

const predict = async (body) => {
  const res = await fetch(`${baseUrl}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return { status: res.status, data: await res.json() };
};

/* ─── Health ─────────────────────────────────────────────────────────────── */

test("GET /health", async () => {
  const res = await fetch(`${baseUrl}/health`);
  assert.equal(res.status, 200);
  assert.deepEqual(await res.json(), { status: "ok" });
});

/* ─── Existing input validation ──────────────────────────────────────────── */

for (const field of ["weight", "height", "goal", "experience"]) {
  test(`missing field '${field}' -> 400`, async () => {
    const body = { ...VALID };
    delete body[field];
    const { status, data } = await predict(body);
    assert.equal(status, 400);
    assert.equal(data.error, `Missing field: '${field}'`);
    assert.equal(mlRequests.length, 0);
  });
}

const invalidCases = [
  [{ goal: "Shred" }, "Invalid goal 'Shred'. Choose: Cut, Bulk, Maintain"],
  [{ experience: "Pro" }, "Invalid experience 'Pro'. Choose: Beginner, Intermediate, Advanced"],
  [{ weight: "abc" }, "Weight and height must be numbers."],
  [{ weight: 19 }, "Weight must be between 20 and 300 kg."],
  [{ weight: 301 }, "Weight must be between 20 and 300 kg."],
  [{ height: 99 }, "Height must be between 100 and 250 cm."],
  [{ height: 251 }, "Height must be between 100 and 250 cm."],
];

for (const [override, message] of invalidCases) {
  test(`invalid input ${JSON.stringify(override)} -> 400`, async () => {
    const { status, data } = await predict({ ...VALID, ...override });
    assert.equal(status, 400);
    assert.equal(data.error, message);
    assert.equal(mlRequests.length, 0);
  });
}

test("malformed JSON -> 400 with a JSON error body", async () => {
  const res = await fetch(`${baseUrl}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: "{ not json",
  });
  assert.equal(res.status, 400);
  assert.deepEqual(await res.json(), { error: "Invalid JSON body." });
});

test("non-JSON content type -> 400", async () => {
  const res = await fetch(`${baseUrl}/predict`, { method: "POST", body: "weight=72" });
  assert.equal(res.status, 400);
  assert.deepEqual(await res.json(), { error: "Invalid JSON body." });
});

test("CORS allows any origin when CORS_ORIGIN is unset", async () => {
  const res = await fetch(`${baseUrl}/health`, { headers: { Origin: "http://localhost:5173" } });
  assert.equal(res.headers.get("access-control-allow-origin"), "*");
});

/* ─── Successful prediction and template mapping ─────────────────────────── */

for (const goal of ["Cut", "Bulk", "Maintain"]) {
  for (const experience of ["Beginner", "Intermediate", "Advanced"]) {
    test(`${goal} + ${experience} maps to workout and diet templates`, async () => {
      const { status, data } = await predict({ ...VALID, weight: "80", goal, experience });
      const plan = `${PREFIX[goal]}_${experience}`;

      assert.equal(status, 200);
      assert.deepEqual(mlRequests, [
        { url: "/ml-predict", body: { weight: 80, height: 175, goal, experience } },
      ]);
      assert.equal(data.plan, plan);
      assert.deepEqual(data.workout, WORKOUT_PLANS[plan]);
      // Diet stays rule-based: chosen from the goal, not from the model output.
      assert.deepEqual(data.diet, DIET_PLANS[goal]);
      assert.equal(data.message, "Follow this plan consistently for 4 weeks for best results!");
    });
  }
}

test("response shape matches what the React components read", async () => {
  const { data } = await predict(VALID);
  assert.deepEqual(Object.keys(data).sort(), ["diet", "message", "plan", "workout"]);
  assert.equal(typeof data.plan.replaceAll, "function"); // PlanHero
  for (const value of Object.values(data.workout)) assert.equal(typeof value, "string"); // WorkoutList
  for (const value of Object.values(data.diet)) assert.equal(typeof value, "string"); // DietList
});

/* ─── ML service failures ────────────────────────────────────────────────── */

const failureHandlers = {
  "ML service returns 500": (req, res) => sendJson(res, 500, { error: "boom" }),
  "ML service returns 400": (req, res) => sendJson(res, 400, { error: "bad input" }),
  "ML service drops the connection": (req) => req.socket.destroy(),
  "ML response has no plan": (req, res) => sendJson(res, 200, {}),
  "ML response has an unknown plan": (req, res) => sendJson(res, 200, { plan: "Yoga_Beginner" }),
  "ML response plan is an Object prototype key": (req, res) => sendJson(res, 200, { plan: "constructor" }),
  "ML response plan is not a string": (req, res) => sendJson(res, 200, { plan: ["FatLoss_Beginner"] }),
  "ML response is not JSON": (req, res) => {
    res.writeHead(200, { "Content-Type": "text/plain" });
    res.end("FatLoss_Beginner");
  },
};

for (const [name, handler] of Object.entries(failureHandlers)) {
  test(`${name} -> 500 Prediction failed`, async () => {
    mlHandler = handler;
    const { status, data } = await predict(VALID);
    assert.equal(status, 500);
    assert.deepEqual(data, { error: "Prediction failed" });
  });
}
