const { test, before, after } = require("node:test");
const assert = require("node:assert/strict");

// Runs in its own process (node --test isolates files), so CORS_ORIGIN can be
// set before app.js reads it.

let server;
let baseUrl;

before(async () => {
  process.env.CORS_ORIGIN = "http://localhost:5173, http://127.0.0.1:5173";
  const { app } = require("../app");
  await new Promise((resolve) => {
    server = app.listen(0, "127.0.0.1", resolve);
  });
  baseUrl = `http://127.0.0.1:${server.address().port}`;
});

after(() => server.close());

test("CORS_ORIGIN: listed origin is allowed", async () => {
  const res = await fetch(`${baseUrl}/health`, { headers: { Origin: "http://127.0.0.1:5173" } });
  assert.equal(res.headers.get("access-control-allow-origin"), "http://127.0.0.1:5173");
});

test("CORS_ORIGIN: other origins get no CORS header", async () => {
  const res = await fetch(`${baseUrl}/health`, { headers: { Origin: "http://evil.example" } });
  assert.equal(res.headers.get("access-control-allow-origin"), null);
});

test("CORS_ORIGIN: preflight for the frontend's POST succeeds", async () => {
  const res = await fetch(`${baseUrl}/predict`, {
    method: "OPTIONS",
    headers: {
      Origin: "http://localhost:5173",
      "Access-Control-Request-Method": "POST",
      "Access-Control-Request-Headers": "content-type",
    },
  });
  assert.equal(res.status, 204);
  assert.equal(res.headers.get("access-control-allow-origin"), "http://localhost:5173");
});
