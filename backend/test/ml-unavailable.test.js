const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");
const http = require("node:http");

// Runs in its own process (node --test isolates files), so ML_SERVICE_URL can
// point at a port where nothing is listening.

let server;
let baseUrl;

before(async () => {
  const probe = http.createServer();
  await new Promise((resolve) => probe.listen(0, "127.0.0.1", resolve));
  const closedPort = probe.address().port;
  await new Promise((resolve) => probe.close(resolve));

  process.env.ML_SERVICE_URL = `http://127.0.0.1:${closedPort}`;
  const { app } = require("../app");
  await new Promise((resolve) => {
    server = app.listen(0, "127.0.0.1", resolve);
  });
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(() => server.close());

test("Flask service unavailable -> 500 Prediction failed, backend stays up", async () => {
  const res = await fetch(`${baseUrl}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ weight: 72, height: 175, goal: "Cut", experience: "Beginner" }),
  });
  assert.equal(res.status, 500);
  assert.deepEqual(await res.json(), { error: "Prediction failed" });

  const health = await fetch(`${baseUrl}/health`);
  assert.equal(health.status, 200);
});
