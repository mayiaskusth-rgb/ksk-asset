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
          bindings: { TEST_MIGRATIONS: migrations, OWNER_PASSWORD: "test-owner-password-only", SESSION_SECRET: "test-session-secret-at-least-32-characters-long" },
        },
      },
    },
  },
});
