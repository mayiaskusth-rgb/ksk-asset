import { defineWorkersConfig } from "@cloudflare/vitest-pool-workers/config";
import { readD1Migrations } from "@cloudflare/vitest-pool-workers/config";

const migrations = await readD1Migrations("./migrations");

export default defineWorkersConfig({
  test: {
    setupFiles: ["./test/apply-migrations.ts"],
    poolOptions: {
      workers: {
        wrangler: { configPath: "./wrangler.toml" },
        miniflare: {
          ratelimits: [{ name: "LOGIN_RATE_LIMITER", namespace_id: "864201", simple: { limit: 5, period: 60 } }],
          bindings: { TEST_MIGRATIONS: migrations, OWNER_PASSWORD: "test-owner-password-only", SESSION_SECRET: "test-session-secret-at-least-32-characters-long" },
        },
      },
    },
  },
});
